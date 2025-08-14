import logging
import os
from pathlib import Path
from typing import List, Type, Annotated, Optional

import typer
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from rich.console import Console

from tickermood.agent import invoke_summarize_agent
from tickermood.source import BaseSource, Investing, Yahoo, Marketwatch, StockAnalysis
from tickermood.subject import (
    Subject,
    LLM,
    LLMSubject,
    check_ollama_model,
    check_openai_model,
)
from tickermood.types import DatabaseConfig

logger = logging.getLogger(__name__)
app = typer.Typer()


class TickerMoodNews(BaseModel):
    sources: List[Type[BaseSource]] = Field(
        default=[Investing, Yahoo, StockAnalysis, Marketwatch]
    )
    subjects: List[Subject]
    headless: bool = True
    database_config: DatabaseConfig = Field(default_factory=DatabaseConfig)

    def headed(self) -> None:
        self.headless = False

    def set_database(self, database_config: Optional[DatabaseConfig] = None) -> None:
        if database_config:
            self.database_config = database_config

    @classmethod
    def from_symbols(cls, symbols: List[str]) -> "TickerMoodNews":
        subjects = [Subject(symbol=symbol) for symbol in symbols]
        return cls(subjects=subjects)

    def summarize(self, subject: Subject, llm: LLM) -> None:
        llm_subject = LLMSubject.from_subject(subject, llm)
        summarized_subject = invoke_summarize_agent(llm_subject)
        summarized_subject.save(self.database_config)

    def search(self, llm: Optional[LLM] = None) -> None:
        for subject in self.subjects:
            for source in self.sources:
                try:
                    subject = source.search_subject(  # noqa: PLW2901
                        subject, headless=self.headless
                    )
                except Exception as e:  # noqa: PERF203
                    logger.warning(
                        f"Error searching for subject {subject.symbol} in {type(source).__name__}: {e}"
                    )
                    continue
            subject.save(self.database_config)
            if llm:
                self.summarize(subject, llm)


class TickerMood(TickerMoodNews):
    llm: LLM = Field(
        default_factory=lambda: LLM(
            model_name="qwen3:4b", model_type=ChatOllama, temperature=0.0
        )
    )

    @classmethod
    def from_subjects(cls, subjects: List[Subject]) -> "TickerMood":
        return cls(subjects=subjects)

    @classmethod
    def from_symbols(cls, symbols: List[str]) -> "TickerMood":
        subjects = [Subject(symbol=symbol) for symbol in symbols]
        return cls(subjects=subjects)

    def set_llm(self, llm: LLM) -> None:
        self.llm = llm

    def run(self) -> None:
        self.search()
        self.call_agent()
        logger.info("TickerMood run completed.")

    def call_agent(self) -> None:
        if self.llm is None:
            raise ValueError("LLM must be set before calling the agent.")
        for subject in self.subjects:
            self.summarize(subject, self.llm)


def get_news(
    symbols: List[str],
    database_config: DatabaseConfig,
    headless: bool = True,
    model_name: str = "gpt-4-turbo",
) -> None:
    llm = None
    ticker_mood = TickerMoodNews.from_symbols(symbols)
    ticker_mood.set_database(database_config)
    ticker_mood.headless = headless
    if check_openai_model(model_name):
        llm = LLM(model_name=model_name, model_type=ChatOpenAI, temperature=0.0)
    elif check_ollama_model(model_name):
        llm = LLM(model_name=model_name, model_type=ChatOllama, temperature=0.0)
    else:
        pass
    ticker_mood.search(llm)


@app.command()
def run(
    symbols: Annotated[List[str], typer.Argument()],
    path: Optional[Path] = None,
    model: Optional[str] = None,
    headless: bool = True,
    openai_api_key_path: Optional[Path] = None,
) -> None:
    ticker_mood = TickerMood.from_symbols(symbols)
    if not headless:
        ticker_mood.headed()
    path = path or Path.cwd() / "tickermood.db"
    ticker_mood.set_database(DatabaseConfig(database_path=path))
    if openai_api_key_path:
        openai_api_key_path = Path(openai_api_key_path)
        if not openai_api_key_path.exists():
            raise FileNotFoundError(
                f"OpenAI API key file not found: {openai_api_key_path}"
            )
        load_dotenv(dotenv_path=openai_api_key_path)
        if "OPENAI_API_KEY" not in os.environ:
            raise ValueError("OpenAI API key not found in environment variables.")
        model = model or "gpt-4o-mini"
        llm = LLM(model_name=model, model_type=ChatOpenAI, temperature=0.0)
        ticker_mood.set_llm(llm)
    if not openai_api_key_path and model:
        llm = LLM(model_name=model, model_type=ChatOllama, temperature=0.0)
        ticker_mood.set_llm(llm)
    console = Console()

    with console.status(
        f"[bold green]Fetching and analysing articles for {', '.join(symbols)}...[/]",
        spinner="dots",
    ):
        ticker_mood.run()
        console.log("[bold green]Done![/]")

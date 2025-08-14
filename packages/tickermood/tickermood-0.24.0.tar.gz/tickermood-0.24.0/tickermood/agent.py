import json
import logging
import re
from typing import get_args, Type

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel

from tickermood.subject import Subject, LLMSubject, PriceTarget, Consensus, NewsAnalysis
from tickermood.types import ConsensusType

logger = logging.getLogger(__name__)


def remove_tagged_text(text: str) -> str:
    pattern = r"<think>.*?</think>"
    return re.sub(pattern, "", text, flags=re.DOTALL).strip()


def get_json_schema(model: Type[BaseModel]) -> str:

    return json.dumps(model.model_json_schema().get("properties", {}), indent=4)


def parse_json_output(model_response: str, model: Type[BaseModel]) -> BaseModel:
    parser = JsonOutputParser()
    raw_model_response = remove_tagged_text(model_response)
    try:
        parsed_output = parser.parse(raw_model_response)
        return model.model_validate(parsed_output)
    except Exception as e:
        logger.error(
            f"Failed to parse model response into {model.__name__}: {e}. parsed_output: {raw_model_response}"
        )
        return model()


def summarize(state: LLMSubject) -> LLMSubject:
    llm = state.get_model()
    system_message = SystemMessage(
        "You are a helpful assistant that summarizes financial articles. "
        "Reasoning, thought process, or annotations like <think>. "
        "Only return the final summary in plain text. No tags, no notes, no process."
        "Only few sentences."
    )
    article = state.get_next_article()
    if article:
        human_message = HumanMessage(
            f"""
            Summarize the text below, which is about the equity {state.to_name()}.
            - Include only information that is directly relevant to {state.to_name()}.
            - Exclude unrelated market commentary, other companies, or general economic news.
            - The output should be an extensive summary in plain language, with no extra text or explanations.

            Article:
            {article.content}
            """
        )
        response = llm.invoke([system_message, human_message])
        state.add_news_summary(remove_tagged_text(str(response.content)), article)
    return state


def has_more_articles(state: LLMSubject) -> bool:
    return state.get_next_article() is not None


def reduce(state: LLMSubject) -> LLMSubject:
    llm = state.get_model()
    system_message = SystemMessage(
        "You are a helpful and smart financial assistant that can summarizes finance articles."
    )
    human_message = HumanMessage(
        f"""
        Read the articles below, all related to {state.to_name()}.
        1. Provide a concise summary containing only information directly relevant to {state.to_name()}.
        2. Based on the content, state whether the stock appears to be a Buy, Sell, or Cautious.
        3. Do not include unrelated market news or other companies.
        4. Output only the summary and the Buy/Sell/Cautious assessment.

        Articles:
        {state.combined_summary_news()}
        """
    )
    response = llm.invoke([system_message, human_message])
    state.add_summary(remove_tagged_text(str(response.content)))
    return state


def price_target(state: LLMSubject) -> LLMSubject:
    llm = state.get_model()
    system_message = SystemMessage(
        "You are a helpful assistant that summarizes financial articles."
    )
    human_message = HumanMessage(
        f"""
        From the text below (related to {state.to_name()}), do the following:
        1. Extract the **high price target** and **low price target** for {state.to_name()}.
        2. Provide a short summary containing only information directly relevant to {state.to_name()}.
        3. Return the result **strictly** in the following JSON format (no extra text or explanation):

        {get_json_schema(PriceTarget)}

        Text:
        {state.combined_price_target_news()}
        """
    )
    response = llm.invoke([system_message, human_message])
    state.add(parse_json_output(str(response.content), PriceTarget))
    return state


def get_consensus(state: LLMSubject) -> LLMSubject:
    llm = state.get_model()

    system_message = SystemMessage(
        "You are a helpful assistant that summarizes financial articles."
    )
    human_message = HumanMessage(
        f"""
        From the text below, summarize the **analyst consensus** for the stock with symbol {state.to_name()}.

        Instructions:
        1. Determine the consensus rating based only on the provided text.
        2. The "consensus" field must be exactly one of the following values: {list(get_args(ConsensusType))}.
        3. Return the result **strictly** in the following JSON format (no extra text or explanation):

        {get_json_schema(Consensus)}

        Text:
        {state.get_consensus_data()}
        """
    )
    response = llm.invoke([system_message, human_message])
    state.add(parse_json_output(str(response.content), Consensus))
    return state


def get_recommendation(state: LLMSubject) -> LLMSubject:
    llm = state.get_model()

    system_message = SystemMessage(
        "You are a helpful assistant that summarizes financial articles."
    )
    human_message = HumanMessage(
        f"""
        From the news below about {state.to_name()}, extract:
        1. **recommendation** — must be exactly one of: {list(get_args(ConsensusType))}
        2. **explanation** — a brief reason for the recommendation.

        Return the result **strictly** in the following JSON format (no extra text or explanation):

        {{
          "recommendation": "<one of {list(get_args(ConsensusType))}>",
          "explanation": "<brief reason>"
        }}

        News:
        {state.combined_summary_news()}
        """
    )
    response = llm.invoke([system_message, human_message])
    state.add(parse_json_output(str(response.content), NewsAnalysis))
    return state


def summarize_agent() -> CompiledStateGraph:
    graph = StateGraph(LLMSubject)

    graph.add_node("summarize", summarize)
    graph.add_node("reduce", reduce)
    graph.add_node("price_target", price_target)
    graph.add_node("get_consensus", get_consensus)
    graph.add_node("get_recommendation", get_recommendation)
    graph.set_entry_point("summarize")
    graph.add_conditional_edges(
        "summarize", has_more_articles, {True: "summarize", False: "reduce"}
    )
    graph.add_edge("reduce", "price_target")
    graph.add_edge("price_target", "get_consensus")
    graph.add_edge("get_consensus", "get_recommendation")

    graph.set_finish_point("get_recommendation")

    return graph.compile()


def invoke_summarize_agent(subject: LLMSubject) -> Subject:

    graph = summarize_agent()
    subject = graph.invoke(subject, config={"recursion_limit": 50})  # type: ignore
    return Subject.model_validate(subject)

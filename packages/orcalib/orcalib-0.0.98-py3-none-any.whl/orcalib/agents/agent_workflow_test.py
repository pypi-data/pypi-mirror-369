import asyncio
from typing import TypedDict

import pytest
from pydantic import BaseModel
from pydantic_ai.messages import ModelMessage, ModelRequest
from pydantic_ai.models.function import AgentInfo, DeltaToolCall, FunctionModel
from pydantic_ai.models.test import TestModel

from .agent_workflow import AgentWorkflow


class SimpleContext(BaseModel):
    value: str


class SimpleInput(BaseModel):
    question: str


class SimpleOutput(BaseModel):
    answer: str
    confidence: float


class SimpleStreamableOutput(TypedDict, total=False):
    answer: str
    confidence: float


@pytest.mark.asyncio
async def test_simple_agent_workflow():
    simple_agent = AgentWorkflow(
        TestModel(),
        input_type=SimpleInput,
        system_prompt="You are a helpful assistant.",
        prompt_template=lambda input: f"Question: {input.question}",
    )

    assert simple_agent.make_system_prompt() == "You are a helpful assistant."
    assert simple_agent.make_prompt(SimpleInput(question="What is 2+2?")) == "Question: What is 2+2?"

    result = await simple_agent.run(SimpleInput(question="What is 2+2?"))
    assert isinstance(result.output, str)
    assert len(result.output) > 0


@pytest.mark.asyncio
async def test_advanced_agent_workflow():
    advanced_agent = AgentWorkflow(
        TestModel(),
        deps_type=SimpleContext,
        input_type=SimpleInput,
        result_type=SimpleOutput,
        system_prompt=lambda deps: f"You are a helpful assistant with context: {deps.value}",
        prompt_template=lambda input, deps: f"Question: {input.question} (Context: {deps.value})",
    )

    assert (
        advanced_agent.make_system_prompt(SimpleContext(value="test context"))
        == "You are a helpful assistant with context: test context"
    )
    assert (
        advanced_agent.make_prompt(SimpleInput(question="What is 2+2?"), SimpleContext(value="test context"))
        == "Question: What is 2+2? (Context: test context)"
    )

    result = await advanced_agent.run(SimpleInput(question="What is 2+2?"), deps=SimpleContext(value="test context"))
    assert isinstance(result.output, SimpleOutput)
    assert isinstance(result.output.answer, str)
    assert len(result.output.answer) > 0
    assert isinstance(result.output.confidence, float)


@pytest.mark.asyncio
async def test_run_stream():
    async def fake_response_stream(messages: list[ModelMessage], _: AgentInfo):
        assert len(messages) == 1 and isinstance(messages[0], ModelRequest)
        assert messages[0].parts[0].content == "Question: Hi"

        yield "Hello, "
        await asyncio.sleep(0.1)
        yield "world!"

    agent = AgentWorkflow(
        FunctionModel(stream_function=fake_response_stream),
        input_type=SimpleInput,
        prompt_template=lambda input: f"Question: {input.question}",
    )

    stream_responses = []
    async with await agent.run_stream(SimpleInput(question="Hi")) as stream:
        async for chunk in stream.stream_text(delta=True):
            stream_responses.append(chunk)

    assert len(stream_responses) == 2
    assert "".join(stream_responses) == "Hello, world!"


@pytest.mark.asyncio
async def test_print_with_structured_output(stdout_capture):
    async def fake_response_stream(_: list[ModelMessage], agent_info: AgentInfo):
        assert agent_info.output_tools is not None
        assert len(agent_info.output_tools) == 1

        yield {0: DeltaToolCall(name=agent_info.output_tools[0].name)}
        yield {0: DeltaToolCall(json_args='{"answer": ')}
        yield {0: DeltaToolCall(json_args='"2+2=')}
        yield {0: DeltaToolCall(json_args='4", ')}
        yield {0: DeltaToolCall(json_args='"confidence": 0.9}')}

    agent = AgentWorkflow(
        FunctionModel(stream_function=fake_response_stream),
        input_type=SimpleInput,
        result_type=SimpleStreamableOutput,
        prompt_template=lambda input: f"Question: {input.question}",
    )

    await agent.print(SimpleInput(question="What is 2+2?"), text_attr="answer")
    output = stdout_capture.getvalue()
    assert len(output) > 0
    assert output.startswith("2+2=4")
    assert "confidence: 0.9" in output

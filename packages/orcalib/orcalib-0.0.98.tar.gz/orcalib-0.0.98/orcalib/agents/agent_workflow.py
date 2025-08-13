from contextlib import AbstractAsyncContextManager
from inspect import signature
from textwrap import dedent
from types import NoneType
from typing import Callable

from pydantic import BaseModel
from pydantic_ai.agent import Agent, AgentRunResult
from pydantic_ai.models import KnownModelName, Model
from pydantic_ai.result import StreamedRunResult


class AgentWorkflow[ResultT, InputT, DepsT]:
    """Light wrapper around [`Agent`][pydantic_ai.agent.Agent] that accepts a prompt template."""

    def __init__(
        self,
        model: Model | KnownModelName | None = None,
        *,
        result_type: type[ResultT] = str,
        input_type: type[InputT] = NoneType,
        deps_type: type[DepsT] = NoneType,
        system_prompt: Callable[[DepsT], str] | str | None = None,
        prompt_template: Callable[[InputT, DepsT], str] | Callable[[InputT], str],
        defer_model_check: bool = True,
        **kwargs,
    ):
        self.agent = Agent[DepsT, ResultT](
            model,
            # un parametrized system prompts can be passed to the constructor
            system_prompt=dedent(system_prompt) if isinstance(system_prompt, str) else (),
            output_type=result_type,
            deps_type=deps_type,
            defer_model_check=defer_model_check,
            **kwargs,
        )
        # parametrized system prompts need to be registered with the agent.system_prompt decorator
        # the system prompt template will then be called on run with the deps provided to run
        if isinstance(system_prompt, Callable):
            self.agent.system_prompt(lambda ctx: dedent(system_prompt(ctx.deps)))

        self.system_prompt_template = system_prompt
        self.prompt_template = prompt_template
        self.input_type = input_type

    def override(self, **kwargs):
        return self.agent.override(**kwargs)

    def make_system_prompt(
        self,
        deps: DepsT = None,  # type: ignore
    ) -> str:
        if isinstance(self.system_prompt_template, Callable):
            if self.agent._deps_type is not NoneType:
                assert deps is not None
            return dedent(self.system_prompt_template(deps))
        else:
            return dedent(self.system_prompt_template or "")

    def make_prompt(
        self,
        input: InputT,
        deps: DepsT = None,  # type: ignore
    ) -> str:
        if self.agent._deps_type is not NoneType:
            assert deps is not None
        return dedent(
            self.prompt_template(input, deps)  # type: ignore
            if len(signature(self.prompt_template).parameters) == 2
            else self.prompt_template(input)  # type: ignore
        )

    async def run(self, input: InputT, **kwargs) -> AgentRunResult[ResultT]:
        """
        Run the agent with a prompt built from the given input.

        Params:
            input: Input to the agent
            **kwargs: Additional keyword arguments to pass to [`Agent.run`][pydantic_ai.agent.Agent.run].

        Returns:
            Result of the agent run
        """
        deps: DepsT = kwargs.get("deps")  # type: ignore
        return await self.agent.run(
            self.make_prompt(input, deps=deps),
            **kwargs,
        )

    async def run_stream(
        self, input: InputT, **kwargs
    ) -> AbstractAsyncContextManager[StreamedRunResult[DepsT, ResultT], bool | None]:
        """
        Run the agent with a prompt built from the given input.

        Params:
            input: Input to the agent
            **kwargs: Additional keyword arguments to pass to [`Agent.run_stream`][pydantic_ai.agent.Agent.run_stream].

        Returns:
            Stream of the agent run
        """
        deps: DepsT = kwargs.get("deps")  # type: ignore
        return self.agent.run_stream(self.make_prompt(input, deps=deps), **kwargs)

    async def print(self, input: InputT, text_attr: str | None = None, **kwargs) -> None:
        """
        Print the output of the agent step by step as it is generated.

        If the result type is a structured object, a `text_attr` can be specified to stream the
        text response from that attribute if the model supports streaming structured responses.

        Params:
            input: Input to the agent
            text_attr: If the result type is not a string, this allows specifying the name of the
                attribute that contains the text response that should be printed incrementally.
                Streaming structured responses is only supported by some models.
            **kwargs: Additional keyword arguments to pass to [`Agent.run_stream`][pydantic_ai.agent.Agent.run_stream].
        """
        async with await self.run_stream(input, **kwargs) as res:
            if self.agent.output_type == str:
                # stream text response to print
                async for chunk in res.stream_text(delta=True):
                    print(chunk, end="")
                print()  # final newline
            elif text_attr is not None:
                # stream text attribute of structured response to print then print other attributes
                printed_so_far = ""
                async for object in res.stream():
                    text = object.get(text_attr, "") if isinstance(object, dict) else getattr(object, text_attr, "")
                    print(text.replace(printed_so_far, ""), end="")
                    printed_so_far = text
                print()  # final newline
                data = await res.get_output()
                data = data.model_dump() if isinstance(data, BaseModel) else data
                if isinstance(data, dict) and len(data) > 1:
                    print("---")
                    for key, value in data.items():
                        if key != text_attr:
                            print(f"{key}: {value}")
                else:
                    print(data)
            else:
                # just print all the attributes of the response
                data = await res.get_output()
                data = data.model_dump() if isinstance(data, BaseModel) else data
                if isinstance(data, dict):
                    for key, value in data.items():
                        print(f"{key}: {value}")
                else:
                    print(data)

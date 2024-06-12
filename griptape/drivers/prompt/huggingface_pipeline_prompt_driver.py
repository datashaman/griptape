from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

from attrs import Factory, define, field

from griptape.artifacts import TextArtifact
from griptape.common import (
    BaseDeltaPromptStackContent,
    DeltaPromptStackElement,
    PromptStack,
    PromptStackElement,
    TextPromptStackContent,
    BasePromptStackContent,
)
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import HuggingFaceTokenizer
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from transformers import TextGenerationPipeline


@define
class HuggingFacePipelinePromptDriver(BasePromptDriver):
    """
    Attributes:
        params: Custom model run parameters.
        model: Hugging Face Hub model name.

    """

    max_tokens: int = field(default=250, kw_only=True, metadata={"serializable": True})
    model: str = field(kw_only=True, metadata={"serializable": True})
    params: dict = field(factory=dict, kw_only=True, metadata={"serializable": True})
    tokenizer: HuggingFaceTokenizer = field(
        default=Factory(
            lambda self: HuggingFaceTokenizer(model=self.model, max_output_tokens=self.max_tokens), takes_self=True
        ),
        kw_only=True,
    )
    pipe: TextGenerationPipeline = field(
        default=Factory(
            lambda self: import_optional_dependency("transformers").pipeline(
                "text-generation", model=self.model, max_new_tokens=self.max_tokens, tokenizer=self.tokenizer.tokenizer
            ),
            takes_self=True,
        )
    )

    def try_run(self, prompt_stack: PromptStack) -> PromptStackElement:
        messages = self._prompt_stack_to_messages(prompt_stack)

        result = self.pipe(
            messages, max_new_tokens=self.max_tokens, temperature=self.temperature, do_sample=True, **self.params
        )

        if isinstance(result, list):
            if len(result) == 1:
                generated_text = result[0]["generated_text"][-1]["content"]

                input_tokens = len(self.__prompt_stack_to_tokens(prompt_stack))
                output_tokens = len(self.tokenizer.tokenizer.encode(generated_text))

                return PromptStackElement(
                    content=[TextPromptStackContent(TextArtifact(generated_text))],
                    role=PromptStackElement.ASSISTANT_ROLE,
                    usage=PromptStackElement.Usage(input_tokens=input_tokens, output_tokens=output_tokens),
                )
            else:
                raise Exception("completion with more than one choice is not supported yet")
        else:
            raise Exception("invalid output format")

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaPromptStackElement | BaseDeltaPromptStackContent]:
        raise NotImplementedError("streaming is not supported")

    def prompt_stack_to_string(self, prompt_stack: PromptStack) -> str:
        return self.tokenizer.tokenizer.decode(self.__prompt_stack_to_tokens(prompt_stack))

    def _prompt_stack_to_messages(self, prompt_stack: PromptStack) -> list[dict]:
        messages = []
        for i in prompt_stack.inputs:
            if len(i.content) == 1:
                messages.append({"role": i.role, "content": self.__prompt_stack_content_message_content(i.content[0])})
            else:
                raise ValueError("Invalid input content length.")

        return messages

    def __prompt_stack_to_tokens(self, prompt_stack: PromptStack) -> list[int]:
        messages = self._prompt_stack_to_messages(prompt_stack)
        tokens = self.tokenizer.tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=True)

        if isinstance(tokens, list):
            return tokens
        else:
            raise ValueError("Invalid output type.")

    def __prompt_stack_content_message_content(self, content: BasePromptStackContent) -> str:
        if isinstance(content, TextPromptStackContent):
            return content.artifact.value
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")

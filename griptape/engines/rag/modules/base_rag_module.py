from abc import ABC
from concurrent import futures
from attrs import define, field, Factory

from griptape.common import MessageStack, Message


@define(kw_only=True)
class BaseRagModule(ABC):
    futures_executor: futures.Executor = field(default=Factory(lambda: futures.ThreadPoolExecutor()))

    def generate_query_prompt_stack(self, system_prompt: str, query: str) -> MessageStack:
        return MessageStack(
            messages=[Message(system_prompt, role=Message.SYSTEM_ROLE), Message(query, role=Message.USER_ROLE)]
        )

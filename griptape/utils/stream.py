from __future__ import annotations

from collections.abc import Iterator
from queue import Queue
from threading import Thread
from typing import TYPE_CHECKING

from attrs import Factory, define, field

from griptape.artifacts import TextChunkArtifact
from griptape.events import (
    ActionChunkEvent,
    BaseEvent,
    CompletionChunkEvent,
    EventListener,
    FinishPromptEvent,
    FinishStructureRunEvent,
)

if TYPE_CHECKING:
    from griptape.structures import Structure


@define
class Stream:
    """A wrapper for Structures that converts `CompletionChunkEvent`s into an iterator of TextArtifacts.

    It achieves this by running the Structure in a separate thread, listening for events from the Structure,
    and yielding those events.

    See relevant Stack Overflow post: https://stackoverflow.com/questions/9968592/turn-functions-with-a-callback-into-python-generators

    Attributes:
        structure: The Structure to wrap.
        _event_queue: A queue to hold events from the Structure.
    """

    structure: Structure = field()

    @structure.validator  # pyright: ignore
    def validate_structure(self, _, structure: Structure):
        if structure and not structure.config.prompt_driver.stream:
            raise ValueError("prompt driver does not have streaming enabled, enable with stream=True")

    _event_queue: Queue[BaseEvent] = field(default=Factory(lambda: Queue()))

    def run(self, *args) -> Iterator[TextChunkArtifact]:
        t = Thread(target=self._run_structure, args=args)
        t.start()

        while True:
            event = self._event_queue.get()
            if isinstance(event, FinishStructureRunEvent):
                break
            elif isinstance(event, FinishPromptEvent):
                yield TextChunkArtifact(value="\n")
            elif isinstance(event, CompletionChunkEvent):
                yield TextChunkArtifact(value=event.token)
            elif isinstance(event, ActionChunkEvent):
                if event.name is not None:
                    yield TextChunkArtifact(value=f"\n{event.name}.{event.path} ({event.tag})")
                elif event.partial_input is not None:
                    yield TextChunkArtifact(value=event.partial_input)
        t.join()

    def _run_structure(self, *args):
        def event_handler(event: BaseEvent):
            self._event_queue.put(event)

        stream_event_listener = EventListener(
            handler=event_handler,
            event_types=[CompletionChunkEvent, ActionChunkEvent, FinishPromptEvent, FinishStructureRunEvent],
        )
        self.structure.add_event_listener(stream_event_listener)

        self.structure.run(*args)

        self.structure.remove_event_listener(stream_event_listener)

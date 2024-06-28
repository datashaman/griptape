from __future__ import annotations

from abc import ABC
from typing import Callable, Optional

from attrs import define, field

from griptape.artifacts import BaseArtifact, ErrorArtifact, TextArtifact
from griptape.tasks import BaseTask
from griptape.utils import J2
from griptape.artifacts import ControlFlowArtifact


@define
class ControlFlowTask(BaseTask, ABC):
    DEFAULT_INPUT_TEMPLATE = "{{ args[0] }}"

    control_flow_fn: Callable[[BaseArtifact | str], BaseTask | str] = field(metadata={"serializable": False})
    _input: str | BaseArtifact | Callable[[BaseTask], BaseArtifact] = field(
        default=DEFAULT_INPUT_TEMPLATE, alias="input"
    )
    output: Optional[BaseArtifact] = field(default=None, init=False)

    @property
    def input(self) -> BaseArtifact:
        if isinstance(self._input, BaseArtifact):
            return self._input
        elif isinstance(self._input, Callable):
            return self._input(self)
        else:
            return TextArtifact(J2().render_from_string(self._input, **self.full_context))

    @input.setter
    def input(self, value: str | TextArtifact | Callable[[BaseTask], TextArtifact]) -> None:
        self._input = value

    def before_run(self) -> None:
        super().before_run()

        self.structure.logger.info(f"{self.__class__.__name__} {self.id}\nInput: {self.input.to_text()}")

    def after_run(self) -> None:
        super().after_run()

        self.structure.logger.info(f"{self.__class__.__name__} {self.id}\nOutput: {self.output.to_text()}")

    def can_task_execute(self, child: BaseTask) -> bool:
        return super().can_task_execute(child) and self.output is not None and self.output == child

    def run(self) -> ControlFlowArtifact | ErrorArtifact:
        task = self.control_flow_fn(self.input)
        task_id = task.id if isinstance(task, BaseTask) else task

        if task_id not in self.child_ids:
            self.output = ErrorArtifact(f"ControlFlowTask {self.id} did not return a valid child task")
        else:
            from griptape.artifacts import TaskArtifact

            self.output = TaskArtifact(task)
        for child in filter(lambda child: child != task, self.children):
            if all(
                parent.state == BaseTask.State.FINISHED
                for parent in filter(lambda parent: parent != self, child.parents)
            ):
                child.state = BaseTask.State.CANCELLED
        return self.output

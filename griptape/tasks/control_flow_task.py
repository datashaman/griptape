from __future__ import annotations

from abc import ABC
from typing import Callable, Optional

from attrs import define, field

from griptape.artifacts import BaseArtifact, ErrorArtifact, TaskArtifact, ListArtifact
from griptape.tasks import BaseTask
from griptape.artifacts import ControlFlowArtifact


@define
class ControlFlowTask(BaseTask, ABC):
    control_flow_fn: Callable[
        [list[BaseTask] | BaseTask], tuple[list[BaseTask | str] | BaseTask | str, BaseArtifact]
    ] = field(metadata={"serializable": False})
    control_flow_output: Optional[ControlFlowArtifact | ErrorArtifact] = field(default=None, init=False)

    @property
    def input(self) -> BaseArtifact:
        if len(self.parents) == 1:
            return TaskArtifact(self.parents[0])
        return ListArtifact([TaskArtifact(parent) for parent in self.parents])

    def before_run(self) -> None:
        super().before_run()

        self.structure.logger.info(f"{self.__class__.__name__} {self.id}\nInput: {self.input.to_text()}")

    def after_run(self) -> None:
        super().after_run()

        self.structure.logger.info(f"{self.__class__.__name__} {self.id}\nOutput: {self.output.to_text()}")

    def run(self) -> ControlFlowArtifact | ErrorArtifact:
        tasks, fn_output = self.control_flow_fn(
            [artifact.value for artifact in self.input.value]
            if isinstance(self.input, ListArtifact)
            else self.input.value
        )
        if tasks is None or tasks == []:
            self.output = ErrorArtifact(f"ControlFlowTask {self.id} did not return any tasks")
            self.control_flow_output = self.output
            return self.control_flow_output

        if not isinstance(tasks, list):
            tasks = [tasks]

        tasks = [self.structure.find_task(task) if isinstance(task, str) else task for task in tasks]

        for task in tasks:
            if task.id not in self.child_ids:
                self.output = ErrorArtifact(f"ControlFlowTask {self.id} did not return a valid child task")
                self.control_flow_output = self.output
            else:
                from griptape.artifacts import TaskArtifact

                self.control_flow_output = TaskArtifact(task)
                self.output = fn_output
            for child in filter(lambda child: child != task, self.children):
                if all(
                    parent.state == BaseTask.State.FINISHED
                    for parent in filter(lambda parent: parent != self, child.parents)
                ):
                    child.state = BaseTask.State.CANCELLED
        return self.control_flow_output  # pyright: ignore

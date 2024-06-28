from __future__ import annotations
from attrs import define, field
from typing import Optional
from griptape.artifacts import ControlFlowArtifact
from griptape.artifacts.base_artifact import BaseArtifact
from griptape.tasks import BaseTask


@define
class TaskArtifact(ControlFlowArtifact):
    value: str | BaseTask = field(metadata={"serializable": True})

    @property
    def task_id(self) -> str:
        return self.value if isinstance(self.value, str) else self.task.id

    @property
    def task(self) -> Optional[BaseTask]:
        return self.value if isinstance(self.value, BaseTask) else None

    def to_text(self) -> str:
        return self.task_id

    def __add__(self, other: BaseArtifact) -> BaseArtifact:
        raise NotImplementedError("TaskArtifact does not support addition")

    def __eq__(self, value: object) -> bool:
        new_value_id = value.id if isinstance(value, BaseTask) else value if isinstance(value, str) else None
        if new_value_id is None:
            return False
        return self.task_id == new_value_id

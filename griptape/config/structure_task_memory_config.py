from attrs import define, field

from .structure_task_memory_query_engine_config import StructureTaskMemoryQueryEngineConfig
from .structure_task_memory_extraction_engine_config import StructureTaskMemoryExtractionEngineConfig
from .structure_task_memory_summary_engine_config import StructureTaskMemorySummaryEngineConfig


@define(kw_only=True)
class StructureTaskMemoryConfig:
    query_engine: StructureTaskMemoryQueryEngineConfig = field()
    extraction_engine: StructureTaskMemoryExtractionEngineConfig = field()
    summary_engine: StructureTaskMemorySummaryEngineConfig = field()

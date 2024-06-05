from __future__ import annotations

from abc import ABC
from typing import Optional

from attrs import define, field, Factory

from griptape.config import BaseConfig
from griptape.drivers import (
    BaseConversationMemoryDriver,
    BaseEmbeddingDriver,
    BaseImageGenerationDriver,
    BaseImageQueryDriver,
    BasePromptDriver,
    BaseVectorStoreDriver,
    BaseTextToSpeechDriver,
    BaseAudioTranscriptionDriver,
)
from griptape.utils import dict_merge


@define
class BaseStructureConfig(BaseConfig, ABC):
    prompt_driver_config: dict = field(kw_only=True, metadata={"serializable": True})
    image_generation_driver_config: dict = field(kw_only=True, metadata={"serializable": True})
    image_query_driver_config: dict = field(kw_only=True, metadata={"serializable": True})
    embedding_driver_config: dict = field(kw_only=True, metadata={"serializable": True})
    vector_store_driver_config: dict = field(kw_only=True, metadata={"serializable": True})
    conversation_memory_driver_config: dict = field(kw_only=True, metadata={"serializable": True})
    text_to_speech_driver_config: dict = field(kw_only=True, metadata={"serializable": True})
    audio_transcription_driver_config: dict = field(kw_only=True, metadata={"serializable": True})

    prompt_driver: BasePromptDriver = field(
        default=Factory(
            lambda self: self.prompt_driver_config.get("type").from_dict(self.prompt_driver_config), takes_self=True
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
    image_generation_driver: BaseImageGenerationDriver = field(
        default=Factory(
            lambda self: self.image_generation_driver_config.get("type").from_dict(self.image_generation_driver_config),
            takes_self=True,
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
    image_query_driver: BaseImageQueryDriver = field(
        default=Factory(
            lambda self: self.image_query_driver_config.get("type").from_dict(self.image_query_driver_config),
            takes_self=True,
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
    embedding_driver: BaseEmbeddingDriver = field(
        default=Factory(
            lambda self: self.embedding_driver_config.get("type").from_dict(self.embedding_driver_config),
            takes_self=True,
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
    vector_store_driver: BaseVectorStoreDriver = field(
        default=Factory(
            lambda self: self.vector_store_driver_config.get("type").from_dict(self.vector_store_driver_config),
            takes_self=True,
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
    conversation_memory_driver: Optional[BaseConversationMemoryDriver] = field(
        default=None, kw_only=True, metadata={"serializable": True}
    )
    text_to_speech_driver: BaseTextToSpeechDriver = field(
        default=Factory(
            lambda self: self.text_to_speech_driver_config.get("type").from_dict(self.text_to_speech_driver_config),
            takes_self=True,
        ),
        kw_only=True,
        metadata={"serializable": True},
    )
    audio_transcription_driver: BaseAudioTranscriptionDriver = field(
        default=Factory(
            lambda self: self.audio_transcription_driver_config.get("type").from_dict(
                self.audio_transcription_driver_config
            ),
            takes_self=True,
        ),
        kw_only=True,
        metadata={"serializable": True},
    )

    def merge_config(self, config: dict) -> BaseStructureConfig:
        base_config = self.to_dict()
        merged_config = dict_merge(base_config, config)

        return BaseStructureConfig.from_dict(merged_config)

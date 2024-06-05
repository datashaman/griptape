from attrs import define, field, NOTHING

from griptape.config import BaseStructureConfig

from griptape.drivers import (
    BaseConversationMemoryDriver,
    DummyVectorStoreDriver,
    DummyEmbeddingDriver,
    DummyImageGenerationDriver,
    DummyPromptDriver,
    DummyImageQueryDriver,
    BaseTextToSpeechDriver,
    BaseAudioTranscriptionDriver,
)


@define(init=False)
class StructureConfig(BaseStructureConfig):
    prompt_driver_config: dict = field(
        default={"type": DummyPromptDriver}, kw_only=True, metadata={"serializable": True}
    )
    image_generation_driver_config: dict = field(
        default={"type": DummyImageGenerationDriver}, kw_only=True, metadata={"serializable": True}
    )
    image_query_driver_config: dict = field(
        default={"type": DummyImageQueryDriver}, kw_only=True, metadata={"serializable": True}
    )
    embedding_driver_config: dict = field(
        default={"type": DummyEmbeddingDriver}, kw_only=True, metadata={"serializable": True}
    )
    vector_store_driver_config: dict = field(
        default={"type": DummyVectorStoreDriver}, kw_only=True, metadata={"serializable": True}
    )
    conversation_memory_driver_config: dict = field(
        default={"type": BaseConversationMemoryDriver}, kw_only=True, metadata={"serializable": True}
    )
    text_to_speech_driver_config: dict = field(
        default={"type": BaseTextToSpeechDriver}, kw_only=True, metadata={"serializable": True}
    )
    audio_transcription_driver_config: dict = field(
        default={"type": BaseAudioTranscriptionDriver}, kw_only=True, metadata={"serializable": True}
    )

    def __init__(self, **params):
        if params["type"] is not NOTHING:
            self.type = params["type"]
        else:
            self.type = __attr_factory_type(self)  # type: ignore

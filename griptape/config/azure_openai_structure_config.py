from typing import Callable, Optional
from attrs import Factory, define, field

from griptape.config import StructureConfig
from griptape.drivers import (
    LocalVectorStoreDriver,
    AzureOpenAiChatPromptDriver,
    AzureOpenAiEmbeddingDriver,
    AzureOpenAiImageGenerationDriver,
    AzureOpenAiImageQueryDriver,
    BasePromptDriver,
    BaseEmbeddingDriver,
    BaseImageGenerationDriver,
    BaseImageQueryDriver,
    BaseVectorStoreDriver,
)
from griptape.utils.dict_utils import dict_merge


@define
class AzureOpenAiStructureConfig(StructureConfig):
    """Azure OpenAI Structure Configuration.

    Attributes:
        azure_endpoint: The endpoint for the Azure OpenAI instance.
        azure_ad_token: An optional Azure Active Directory token.
        azure_ad_token_provider: An optional Azure Active Directory token provider.
        api_key: An optional Azure API key.
        prompt_driver: An Azure OpenAI Chat Prompt Driver.
        image_generation_driver: An Azure OpenAI Image Generation Driver.
        image_query_driver: An Azure OpenAI Vision Image Query Driver.
        embedding_driver: An Azure OpenAI Embedding Driver.
        vector_store_driver: A Local Vector Store Driver.
    """

    azure_endpoint: str = field(kw_only=True, metadata={"serializable": True})
    azure_ad_token: Optional[str] = field(kw_only=True, default=None, metadata={"serializable": False})
    azure_ad_token_provider: Optional[Callable[[], str]] = field(
        kw_only=True, default=None, metadata={"serializable": False}
    )
    api_key: Optional[str] = field(kw_only=True, default=None, metadata={"serializable": False})
    prompt_driver_config: dict = field(
        default=Factory(
            lambda self: {
                "type": AzureOpenAiChatPromptDriver,
                "model": "gpt-4o",
                "azure_endpoint": self.azure_endpoint,
                "api_key": self.api_key,
                "azure_ad_token": self.azure_ad_token,
                "azure_ad_token_provider": self.azure_ad_token_provider,
            },
            takes_self=True,
        ),
        kw_only=True,
        metadata={"serializable": True},
    )

    prompt_driver: BasePromptDriver = field(
        default=Factory(
            lambda self: AzureOpenAiChatPromptDriver(
                model="gpt-4o",
                azure_endpoint=self.azure_endpoint,
                api_key=self.api_key,
                azure_ad_token=self.azure_ad_token,
                azure_ad_token_provider=self.azure_ad_token_provider,
            ),
            takes_self=True,
        ),
        metadata={"serializable": True},
        kw_only=True,
    )
    image_generation_driver: BaseImageGenerationDriver = field(
        default=Factory(
            lambda self: AzureOpenAiImageGenerationDriver(
                model="dall-e-2",
                azure_endpoint=self.azure_endpoint,
                api_key=self.api_key,
                azure_ad_token=self.azure_ad_token,
                azure_ad_token_provider=self.azure_ad_token_provider,
                image_size="512x512",
            ),
            takes_self=True,
        ),
        metadata={"serializable": True},
        kw_only=True,
    )
    image_query_driver: BaseImageQueryDriver = field(
        default=Factory(
            lambda self: AzureOpenAiImageQueryDriver(
                model="gpt-4o",
                azure_endpoint=self.azure_endpoint,
                api_key=self.api_key,
                azure_ad_token=self.azure_ad_token,
                azure_ad_token_provider=self.azure_ad_token_provider,
            ),
            takes_self=True,
        ),
        metadata={"serializable": True},
        kw_only=True,
    )
    embedding_driver: BaseEmbeddingDriver = field(
        default=Factory(
            lambda self: AzureOpenAiEmbeddingDriver(
                model="text-embedding-3-small",
                azure_endpoint=self.azure_endpoint,
                api_key=self.api_key,
                azure_ad_token=self.azure_ad_token,
                azure_ad_token_provider=self.azure_ad_token_provider,
            ),
            takes_self=True,
        ),
        metadata={"serializable": True},
        kw_only=True,
    )
    vector_store_driver: BaseVectorStoreDriver = field(
        default=Factory(lambda self: LocalVectorStoreDriver(embedding_driver=self.embedding_driver), takes_self=True),
        metadata={"serializable": True},
        kw_only=True,
    )

    def __init__(self, **kwargs):
        # fmt: off
        if pd_config := kwargs.get("prompt_driver_config") is not None:
            kwargs["prompt_driver_config"] = dict_merge(__attr_factory_prompt_driver_config(self), pd_config)  # type: ignore
        if igd_config := kwargs.get("image_generation_driver_config") is not None:
            kwargs["image_generation_driver_config"] = dict_merge(
                __attr_factory_image_generation_driver_config(self), igd_config # type: ignore
            )
        if iqd_config := kwargs.get("image_query_driver_config") is not None:
            kwargs["image_query_driver_config"] = dict_merge(__attr_factory_image_query_driver_config(self), iqd_config)  # type: ignore
        if ed_config := kwargs.get("embedding_driver_config") is not None:
            kwargs["embedding_driver_config"] = dict_merge(__attr_factory_embedding_driver_config(self), ed_config)  # type: ignore
        if vsd_config := kwargs.get("vector_store_driver_config") is not None:
            kwargs["vector_store_driver_config"] = dict_merge(
                __attr_factory_vector_store_driver_config(self), vsd_config # type: ignore
            )
        __attrs_init__(self, **kwargs)  # type: ignore
        # fmt: on

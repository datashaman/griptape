from __future__ import annotations

from typing import Callable, Optional
from attrs import define, field, Factory
from griptape.drivers import OpenAiEmbeddingDriver
from griptape.tokenizers import OpenAiTokenizer
import openai


@define
class AzureOpenAiEmbeddingDriver(OpenAiEmbeddingDriver):
    """
    Attributes:
        azure_deployment: An optional Azure OpenAi deployment id. Defaults to the model name.
        azure_endpoint: An Azure OpenAi endpoint.
        azure_ad_token: An optional Azure Active Directory token.
        azure_ad_token_provider: An optional Azure Active Directory token provider.
        api_version: An Azure OpenAi API version.
        tokenizer: An `OpenAiTokenizer`.
        client: An `openai.AzureOpenAI` client.
    """

    azure_deployment: str = field(
        kw_only=True, default=Factory(lambda self: self.model, takes_self=True), metadata={"serializable": True}
    )
    azure_endpoint: str = field(kw_only=True, default=None, metadata={"serializable": True})
    azure_ad_token: Optional[str] = field(kw_only=True, default=None, metadata={"serializable": False})
    azure_ad_token_provider: Optional[Callable[[], str]] = field(
        kw_only=True, default=None, metadata={"serializable": False}
    )
    api_version: str = field(default="2023-05-15", kw_only=True, metadata={"serializable": True})
    tokenizer: OpenAiTokenizer = field(
        default=Factory(lambda self: OpenAiTokenizer(model=self.model), takes_self=True), kw_only=True
    )
    client: openai.AzureOpenAI = field(default=None, kw_only=True, metadata={"serializable": False})

    def __attrs_post_init__(self) -> None:
        if self.client is None:
            if (
                self.azure_endpoint
                and self.azure_deployment
                and self.api_version
                and (self.azure_ad_token or self.azure_ad_token_provider or self.api_key)
            ):
                self.client = openai.AzureOpenAI(
                    self.azure_endpoint,
                    self.azure_deployment,
                    self.api_version,
                    ad_token=self.azure_ad_token,
                    ad_token_provider=self.azure_ad_token_provider,
                )
            else:
                raise ValueError(
                    "AzureOpenAiEmbeddingDriver requires azure_endpoint, azure_deployment, api_version, and either azure_ad_token or azure_ad_token_provider or api_key."
                )

from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, List, Union

from pydantic import TypeAdapter

from haizelabs._resource import AsyncAPIResource, SyncAPIResource
from haizelabs.models import ChatCompletionMessage
from haizelabs.models.ai_system import (
    AISystem,
    AISystemType,
    CreateAISystemResponse,
    CreateSelfHostedAISystemRequest,
    CreateThirdPartyAISystemRequest,
    GetAISystemResponse,
    LLMProviderSecrets,
    SelfHostedConfig,
    ThirdPartyProvider,
    UpdateAISystemResponse,
    UpdateSelfHostedAISystemRequest,
    UpdateThirdPartyAISystemRequest,
)

AISystemFunction = Callable[[List[ChatCompletionMessage]], Union[str, Awaitable[str]]]


class SyncAISystems(SyncAPIResource):
    prefix: str = "/ai_systems"

    def create(
        self,
        name: str,
        api_key: str | None = None,
        model_id: str | None = None,
        provider: ThirdPartyProvider | None = None,
        self_hosted_config: SelfHostedConfig | None = None,
        system_config: Dict[str, Any] | None = None,
        system_prompt: str | None = None,
    ) -> AISystem:
        """Create a new AI system.

        Args:
            name: Name of the AI system
            api_key: API key for third-party systems
            model_id: Model ID for third-party systems
            provider: Provider for third-party systems
            self_hosted_config: Self-hosted configuration
            system_config: System configuration
            system_prompt: System prompt

        Returns:
            Details of the created AI system
        """
        if api_key:
            provider_secrets = LLMProviderSecrets(api_key=api_key)
        else:
            provider_secrets = None

        if self_hosted_config and provider:
            raise ValueError(
                "Only one of self_hosted_config or provider can be provided"
            )

        if self_hosted_config:
            request = CreateSelfHostedAISystemRequest(
                self_hosted_config=self_hosted_config,
                provider_secrets=provider_secrets,
                ai_system_type=AISystemType.SELF_HOSTED,
                name=name,
                system_config=system_config,
                system_prompt=system_prompt,
            )
        else:
            if not provider:
                raise ValueError("Provider is required for third-party AI systems")
            if not model_id:
                raise ValueError("Model ID is required for third-party AI systems")
            request = CreateThirdPartyAISystemRequest(
                ai_system_type=AISystemType.THIRD_PARTY,
                name=name,
                provider=provider,
                model_id=model_id,
                provider_secrets=provider_secrets,
                system_config=system_config,
                system_prompt=system_prompt,
            )

        response = self._client.post(f"{self.prefix}", json=request.model_dump())
        create_response = CreateAISystemResponse.model_validate(response)
        return self.get(create_response.id)

    def get(self, ai_system_id: str) -> AISystem:
        """Get an AI system by ID.

        Args:
            ai_system_id: ID of the AI system

        Returns:
            Details of the AI system
        """
        response = self._client.get(f"{self.prefix}/{ai_system_id}")
        response_model = GetAISystemResponse.model_validate(response)
        ai_system_dict = response_model.ai_system.model_dump(exclude_none=True)
        return TypeAdapter(AISystem).validate_python(ai_system_dict)

    def update(
        self,
        ai_system_id: str,
        name: str | None = None,
        api_key: str | None = None,
        provider: ThirdPartyProvider | None = None,
    ) -> AISystem:
        """Update an AI system.

        Args:
            ai_system_id: ID of the AI system
            name: New name for the AI system
            api_key: New API key
            provider: New provider

        Returns:
            Updated details of the AI system
        """
        if api_key:
            provider_secrets = LLMProviderSecrets(api_key=api_key)
        else:
            provider_secrets = None

        request = UpdateThirdPartyAISystemRequest(
            name=name,
            provider=provider,
            provider_secrets=provider_secrets,
        )
        response = self._client.post(
            f"{self.prefix}/{ai_system_id}/update", json=request.model_dump()
        )
        response_model = GetAISystemResponse.model_validate(response)
        ai_system_dict = response_model.ai_system.model_dump(exclude_none=True)
        return TypeAdapter(AISystem).validate_python(ai_system_dict)

    def upsert_by_name(
        self,
        name: str,
        url: str | None = None,
        api_key: str | None = None,
        model_id: str | None = None,
        provider: ThirdPartyProvider | None = None,
        self_hosted_config: SelfHostedConfig | None = None,
        system_config: Dict[str, Any] | None = None,
        system_prompt: str | None = None,
    ) -> AISystem:
        """Get or create an AI system by name.

        Args:
            name: Name of the AI system
            url: URL for self-hosted systems (deprecated)
            api_key: API key for third-party systems
            model_id: Model ID for third-party systems
            provider: Provider for third-party systems
            self_hosted_config: Self-hosted configuration
            system_config: System configuration
            system_prompt: System prompt

        Returns:
            Details of the AI system
        """
        if api_key:
            provider_secrets = LLMProviderSecrets(api_key=api_key)
        else:
            provider_secrets = None

        if self_hosted_config and provider:
            raise ValueError(
                "Only one of self_hosted_config or provider can be provided"
            )

        if self_hosted_config:
            request = CreateSelfHostedAISystemRequest(
                self_hosted_config=self_hosted_config,
                provider_secrets=provider_secrets,
                ai_system_type=AISystemType.SELF_HOSTED,
                name=name,
                system_config=system_config,
                system_prompt=system_prompt,
            )
        else:
            if not provider:
                raise ValueError("Provider is required for third-party AI systems")
            if not model_id:
                raise ValueError("Model ID is required for third-party AI systems")
            request = CreateThirdPartyAISystemRequest(
                ai_system_type=AISystemType.THIRD_PARTY,
                name=name,
                provider=provider,
                model_id=model_id,
                provider_secrets=provider_secrets,
                system_config=system_config,
                system_prompt=system_prompt,
            )

        response = self._client.post(
            f"{self.prefix}/upsert_by_name", json=request.model_dump()
        )
        response_model = UpdateAISystemResponse.model_validate(response)

        return TypeAdapter(AISystem).validate_python(
            response_model.ai_system.model_dump(exclude_none=True)
        )


class AsyncAISystems(AsyncAPIResource):
    prefix: str = "/ai_systems"

    async def create(
        self,
        name: str,
        api_key: str | None = None,
        model_id: str | None = None,
        provider: ThirdPartyProvider | None = None,
        self_hosted_config: SelfHostedConfig | None = None,
        system_config: Dict[str, Any] | None = None,
        system_prompt: str | None = None,
    ) -> AISystem:
        """Create a new AI system.

        Args:
            name: Name of the AI system
            api_key: API key for third-party systems
            model_id: Model ID for third-party systems
            provider: Provider for third-party systems
            self_hosted_config: Self-hosted configuration
            system_config: System configuration
            system_prompt: System prompt

        Returns:
            Details about the AI system
        """
        if api_key:
            provider_secrets = LLMProviderSecrets(api_key=api_key)
        else:
            provider_secrets = None

        if self_hosted_config and provider:
            raise ValueError(
                "Only one of self_hosted_config or provider can be provided"
            )

        if self_hosted_config:
            request = CreateSelfHostedAISystemRequest(
                self_hosted_config=self_hosted_config,
                provider_secrets=provider_secrets,
                ai_system_type=AISystemType.SELF_HOSTED,
                name=name,
                system_config=system_config,
                system_prompt=system_prompt,
            )
        else:
            if not provider:
                raise ValueError("Provider is required for third-party AI systems")
            if not model_id:
                raise ValueError("Model ID is required for third-party AI systems")
            request = CreateThirdPartyAISystemRequest(
                ai_system_type=AISystemType.THIRD_PARTY,
                name=name,
                provider=provider,
                model_id=model_id,
                provider_secrets=provider_secrets,
                system_config=system_config,
                system_prompt=system_prompt,
            )

        response = await self._client.post(f"{self.prefix}", json=request.model_dump())
        create_response = CreateAISystemResponse.model_validate(response)
        # Fetch the full AI system after creation
        return await self.get(create_response.id)

    async def get(self, ai_system_id: str) -> AISystem:
        """Get an AI system by ID.

        Args:
            ai_system_id: ID of the AI system

        Returns:
            Details about the AI system
        """
        response = await self._client.get(f"{self.prefix}/{ai_system_id}")

        response_model = GetAISystemResponse.model_validate(response)
        ai_system_dict = response_model.ai_system.model_dump(exclude_none=True)
        return TypeAdapter(AISystem).validate_python(ai_system_dict)

    async def update(
        self,
        ai_system_id: str,
        name: str | None = None,
        api_key: str | None = None,
        description: str | None = None,
        system_prompt: str | None = None,
        model_id: str | None = None,
        self_hosted_config: SelfHostedConfig | None = None,
        delete_key: bool = False,
        provider: ThirdPartyProvider | None = None,
    ) -> AISystem:
        """Update an AI system.

        Args:
            ai_system_id: ID of the AI system
            name: New name for the AI system
            api_key: New API key
            description: New description
            system_prompt: New system prompt
            model_id: New model ID
            self_hosted_config: New self-hosted configuration
            delete_key: Whether to delete the API key
            provider: New provider

        Returns:
            Updated Details about the AI system
        """
        if api_key:
            provider_secrets = LLMProviderSecrets(api_key=api_key)
        else:
            provider_secrets = None
        if provider:
            request = UpdateThirdPartyAISystemRequest(
                name=name,
                provider=provider,
                provider_secrets=provider_secrets,
                description=description,
                system_prompt=system_prompt,
                delete_key=delete_key,
                model_id=model_id,
            )
        else:
            request = UpdateSelfHostedAISystemRequest(
                name=name,
                self_hosted_config=self_hosted_config,
                provider_secrets=provider_secrets,
                description=description,
                system_prompt=system_prompt,
                delete_key=delete_key,
            )
        response = await self._client.post(
            f"{self.prefix}/{ai_system_id}/update", json=request.model_dump()
        )
        response_model = GetAISystemResponse.model_validate(response)
        ai_system_dict = response_model.ai_system.model_dump(exclude_none=True)
        return TypeAdapter(AISystem).validate_python(ai_system_dict)

    async def upsert_by_name(
        self,
        name: str,
        api_key: str | None = None,
        model_id: str | None = None,
        provider: ThirdPartyProvider | None = None,
        self_hosted_config: SelfHostedConfig | None = None,
        system_config: Dict[str, Any] | None = None,
        system_prompt: str | None = None,
    ) -> AISystem:
        """Get or create an AI system by name.

        Args:
            name: Name of the AI system
            api_key: API key for third-party systems
            model_id: Model ID for third-party systems
            provider: Provider for third-party systems
            self_hosted_config: Self-hosted configuration
            system_config: System configuration
            system_prompt: System prompt

        Returns:
            Details about the AI system
        """
        if api_key:
            provider_secrets = LLMProviderSecrets(api_key=api_key)
        else:
            provider_secrets = None

        if self_hosted_config and provider:
            raise ValueError(
                "Only one of self_hosted_config or provider can be provided"
            )

        if self_hosted_config:
            request = CreateSelfHostedAISystemRequest(
                self_hosted_config=self_hosted_config,
                provider_secrets=provider_secrets,
                ai_system_type=AISystemType.SELF_HOSTED,
                name=name,
                system_config=system_config,
                system_prompt=system_prompt,
            )
        else:
            if not provider:
                raise ValueError("Provider is required for third-party AI systems")
            if not model_id:
                raise ValueError("Model ID is required for third-party AI systems")
            request = CreateThirdPartyAISystemRequest(
                ai_system_type=AISystemType.THIRD_PARTY,
                name=name,
                provider=provider,
                model_id=model_id,
                provider_secrets=provider_secrets,
                system_config=system_config,
                system_prompt=system_prompt,
            )

        response = await self._client.post(
            f"{self.prefix}/upsert_by_name", json=request.model_dump()
        )
        response_model = UpdateAISystemResponse.model_validate(response)

        return TypeAdapter(AISystem).validate_python(
            response_model.ai_system.model_dump(exclude_none=True)
        )

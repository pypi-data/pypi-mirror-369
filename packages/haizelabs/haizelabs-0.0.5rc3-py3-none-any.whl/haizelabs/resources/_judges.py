from __future__ import annotations

import logging
import string
from typing import Optional

from haizelabs._resource import AsyncAPIResource, SyncAPIResource
from haizelabs.models import (
    Judge,
    JudgeType,
    PromptTemplate,
)
from haizelabs.models.judges import (
    GetJudgeResponse,
    JudgeOutputFormat,
    UpsertExactMatchJudgeRequest,
    UpsertJudgeResponse,
    UpsertRegexMatchJudgeRequest,
    UpsertStaticPromptJudgeRequest,
)
from haizelabs.models.label_types import LabelType
from haizelabs.models.prompt_templates import PromptTemplateType

log = logging.getLogger(__name__)


def validate_judge_prompt_template(prompt_template: str) -> None:
    formatter = string.Formatter()
    field_names = [
        field_name
        for _, field_name, _, _ in formatter.parse(prompt_template)
        if field_name
    ]
    if "system_output" not in field_names:
        raise ValueError(
            f"Template must contain '{{system_output}}', but placeholders found were: {field_names}"
        )


class SyncJudges(SyncAPIResource):
    prefix: str = "/judges"

    def create(
        self,
        name: str,
        label_type: LabelType,
        judge_type: JudgeType,
        system_prompt: str | None = None,
        ai_system_id: str | None = None,
        prompt_template: str | None = None,
        description: str | None = None,
        output_format: JudgeOutputFormat = JudgeOutputFormat.STRUCTURED_OUTPUT,
        provides_rationale: bool = False,
        default_match_value: str | None = None,
        default_regex_pattern: str | None = None,
        column_name: str | None = None,
    ) -> UpsertJudgeResponse:
        """Create a new judge.

        Args:
            name: Name of the judge
            label_type: Type of label (ContinuousLabelType or EnumLabelType)
            judge_type: Type of judge (STATIC_PROMPT, EXACT_MATCH, REGEX_MATCH)
            system_prompt: System prompt for STATIC_PROMPT judges
            ai_system_id: AI system ID for STATIC_PROMPT judges
            prompt_template: Template for STATIC_PROMPT judges (must contain {system_output})
            description: Description of the judge
            output_format: Output format for the judge
            provides_rationale: Whether judge provides rationale
            default_match_value: Column to match for EXACT_MATCH judges
            default_regex_pattern: Regex pattern for REGEX_MATCH judges
            column_name: Column name for match judges

        Returns:
            Details about the judge
        """
        if judge_type == JudgeType.STATIC_PROMPT:
            if not system_prompt:
                raise ValueError("system_prompt is required for static prompt judge")
            if not ai_system_id:
                raise ValueError("ai_system_id is required for static prompt judge")
            if not prompt_template:
                raise ValueError("prompt_template is required for static prompt judge")

            validate_judge_prompt_template(prompt_template)

            prompt_template_obj = PromptTemplate(
                prompt_template_type=PromptTemplateType.JUDGE,
                template=prompt_template,
            )

            request_body = UpsertStaticPromptJudgeRequest(
                name=name,
                description=description,
                judge_type=judge_type,
                label_type=label_type,
                ai_system_id=ai_system_id,
                prompt_template=prompt_template_obj,
                system_prompt=system_prompt,
                output_format=output_format,
                provides_rationale=provides_rationale,
            )
        elif judge_type == JudgeType.EXACT_MATCH:
            if not default_match_value:
                raise ValueError(
                    "default_match_value is required for exact match judge"
                )

            request_body = UpsertExactMatchJudgeRequest(
                name=name,
                description=description,
                judge_type=judge_type,
                label_type=label_type,
                default_match_value=default_match_value,
                column_name=column_name,
            )
        elif judge_type == JudgeType.REGEX_MATCH:
            if not default_regex_pattern:
                raise ValueError(
                    "default_regex_pattern is required for regex match judge"
                )

            request_body = UpsertRegexMatchJudgeRequest(
                name=name,
                description=description,
                judge_type=judge_type,
                label_type=label_type,
                default_regex_pattern=default_regex_pattern,
                column_name=column_name,
            )
        else:
            raise NotImplementedError(f"Judge type {judge_type} not supported")

        response = self._client.post(
            f"{self.prefix}/create", json=request_body.model_dump(mode="json")
        )

        return UpsertJudgeResponse.model_validate(response)

    def get(self, judge_id: str, version: Optional[int] = None) -> Judge:
        """Get a judge by ID.

        Args:
            judge_id: ID of the judge
            version: Specific version to retrieve (latest if None)

        Returns:
            Details about the judge
        """
        if not version:
            response = self._client.get(f"{self.prefix}/{judge_id}/latest")
        else:
            response = self._client.get(f"{self.prefix}/{judge_id}/{version}")

        _response = GetJudgeResponse.model_validate(response)
        return _response.judge


class AsyncJudges(AsyncAPIResource):
    prefix: str = "/judges"

    async def create(
        self,
        name: str,
        label_type: LabelType,
        judge_type: JudgeType,
        system_prompt: str | None = None,
        ai_system_id: str | None = None,
        prompt_template: str | None = None,
        description: str | None = None,
        output_format: JudgeOutputFormat = JudgeOutputFormat.STRUCTURED_OUTPUT,
        provides_rationale: bool = False,
        default_match_value: str | None = None,
        default_regex_pattern: str | None = None,
        column_name: str | None = None,
    ) -> UpsertJudgeResponse:
        """Create a new judge.

        Args:
            name: Name of the judge
            label_type: Type of label (ContinuousLabelType or EnumLabelType)
            judge_type: Type of judge (STATIC_PROMPT, EXACT_MATCH, REGEX_MATCH)
            system_prompt: System prompt for STATIC_PROMPT judges
            ai_system_id: AI system ID for STATIC_PROMPT judges
            prompt_template: Template for STATIC_PROMPT judges (must contain {system_output})
            description: Description of the judge
            output_format: Output format for the judge
            provides_rationale: Whether judge provides rationale
            default_match_value: Column to match for EXACT_MATCH judges
            default_regex_pattern: Regex pattern for REGEX_MATCH judges
            column_name: Column name for match judges

        Returns:
            Details about the judge
        """
        if judge_type == JudgeType.STATIC_PROMPT:
            if not system_prompt:
                raise ValueError("system_prompt is required for static prompt judge")
            if not ai_system_id:
                raise ValueError("ai_system_id is required for static prompt judge")
            if not prompt_template:
                raise ValueError("prompt_template is required for static prompt judge")

            validate_judge_prompt_template(prompt_template)

            prompt_template_obj = PromptTemplate(
                prompt_template_type=PromptTemplateType.JUDGE,
                template=prompt_template,
            )

            request_body = UpsertStaticPromptJudgeRequest(
                name=name,
                description=description,
                judge_type=judge_type,
                label_type=label_type,
                ai_system_id=ai_system_id,
                prompt_template=prompt_template_obj,
                system_prompt=system_prompt,
                output_format=output_format,
                provides_rationale=provides_rationale,
            )
        elif judge_type == JudgeType.EXACT_MATCH:
            if not default_match_value:
                raise ValueError(
                    "default_match_value is required for exact match judge"
                )

            request_body = UpsertExactMatchJudgeRequest(
                name=name,
                description=description,
                judge_type=judge_type,
                label_type=label_type,
                default_match_value=default_match_value,
                column_name=column_name,
            )
        elif judge_type == JudgeType.REGEX_MATCH:
            if not default_regex_pattern:
                raise ValueError(
                    "default_regex_pattern is required for regex match judge"
                )

            request_body = UpsertRegexMatchJudgeRequest(
                name=name,
                description=description,
                judge_type=judge_type,
                label_type=label_type,
                default_regex_pattern=default_regex_pattern,
                column_name=column_name,
            )
        else:
            raise NotImplementedError(f"Judge type {judge_type} not supported")

        response = await self._client.post(
            f"{self.prefix}/create", json=request_body.model_dump(mode="json")
        )

        return UpsertJudgeResponse.model_validate(response)

    async def get(self, judge_id: str, version: Optional[int] = None) -> Judge:
        """Get a judge by ID.

        Args:
            judge_id: ID of the judge
            version: Specific version to retrieve (latest if None)

        Returns:
            Details about the judge
        """
        if not version:
            response = await self._client.get(f"{self.prefix}/{judge_id}/latest")
        else:
            response = await self._client.get(f"{self.prefix}/{judge_id}/{version}")

        _response = GetJudgeResponse.model_validate(response)
        return _response.judge

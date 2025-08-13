"""
How to:
1. Create different types of judges
2. Read/retrieve judges
3. Update judges
"""

import asyncio
import logging

from haizelabs import AsyncHaize
from haizelabs.models.ai_system import ThirdPartyProvider
from haizelabs.models.judges import JudgeType
from haizelabs.models.label_types import ContinuousLabelType, EnumLabelType

logging.basicConfig(level=logging.INFO)
logging.getLogger("haizelabs").setLevel(logging.DEBUG)


async def main():
    haize = AsyncHaize()

    # First create an AI system that will power the judge
    ai_system = await haize.ai_systems.upsert_by_name(
        name="judge_ai_system",
        model_id="gpt-4o-mini",
        provider=ThirdPartyProvider.OPENAI,
    )

    # Static Prompt Judge - uses an LLM to evaluate based on a prompt
    static_prompt_judge = await haize.judges.create(
        name="quality_judge",
        system_prompt="Rate the quality of this response from 1 to 10",
        prompt_template="Rate the quality of this response from 1 to 10: {system_output}",
        label_type=ContinuousLabelType(min_value=1, max_value=10),
        judge_type=JudgeType.STATIC_PROMPT,
        ai_system_id=ai_system.id,
    )
    print(
        f"Created static prompt judge:\n{static_prompt_judge.model_dump_json(indent=2)}"
    )

    # Exact Match Judge - checks if output exactly matches a value
    exact_match_judge = await haize.judges.create(
        name="exact_answer_judge",
        label_type=EnumLabelType(options=["correct", "incorrect"]),
        judge_type=JudgeType.EXACT_MATCH,
        default_match_value="Paris",
        description="Checks if the answer is exactly 'Paris'",
    )
    print(f"Created exact match judge:\n{exact_match_judge.model_dump_json(indent=2)}")

    # Regex Match Judge - checks if output matches a regex pattern
    regex_match_judge = await haize.judges.create(
        name="email_format_judge",
        label_type=EnumLabelType(options=["valid", "invalid"]),
        judge_type=JudgeType.REGEX_MATCH,
        default_regex_pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        description="Validates email format using regex",
    )
    print(f"Created regex match judge:\n{regex_match_judge.model_dump_json(indent=2)}")

    retrieved_judge = await haize.judges.get(static_prompt_judge.id)
    print(f"Retrieved judge:\n{retrieved_judge.model_dump_json(indent=2)}")

    await haize.close()


if __name__ == "__main__":
    asyncio.run(main())

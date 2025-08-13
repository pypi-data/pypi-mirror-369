import os

import pytest
import pytest_asyncio
import vcr

from haizelabs import AsyncHaize, Haize
from haizelabs.models.ai_system import ThirdPartyProvider
from haizelabs.models.judges import JudgeType
from haizelabs.models.label_types import ContinuousLabelType


@pytest.fixture
def api_key() -> str:
    return os.environ.get("HAIZE_API_KEY", "test_api_key")


@pytest.fixture
def request_vcr():
    return vcr.VCR(
        cassette_library_dir=os.path.join(os.path.dirname(__file__), "cassettes"),
        record_mode="once",
        match_on=["path"],
        filter_headers=["authorization", "x-api-key", "api-key", "x-haize-api-key"],
    )


@pytest_asyncio.fixture
@pytest.mark.asyncio
async def async_haize(api_key: str) -> AsyncHaize:
    client = AsyncHaize(api_key=api_key, base_url="http://api.haizelabs-staging.com/v1")
    yield client
    await client.close()


@pytest.fixture
def haize(api_key: str) -> Haize:
    client = Haize(api_key=api_key, base_url="http://api.haizelabs-staging.com/v1")
    yield client
    client.close()


@pytest.fixture
def ai_system(haize: Haize, request_vcr):
    with request_vcr.use_cassette("upsert_ai_system.yaml"):
        ai_system = haize.ai_systems.upsert_by_name(
            name="corporate_assistant_v1",
            model_id="gpt-4o-mini",
            provider=ThirdPartyProvider.OPENAI,
        )
        return ai_system


@pytest.fixture
def judge(haize: Haize, ai_system, request_vcr):
    with request_vcr.use_cassette("create_judge.yaml"):
        judge = haize.judges.create(
            name="test_judge_fixture",
            system_prompt="Evaluate safety.",
            prompt_template="Evaluate this output: {system_output}",
            label_type=ContinuousLabelType(min_value=1, max_value=10),
            judge_type=JudgeType.STATIC_PROMPT,
            ai_system_id=ai_system.id,
        )
        return judge


@pytest.fixture
def coc(haize: Haize, request_vcr):
    with request_vcr.use_cassette("create_coc.yaml"):
        coc = haize.code_of_conduct.create(
            name="test_coc_fixture", description="Test code of conduct"
        )
        return coc


@pytest.fixture
def policy(haize: Haize, coc, request_vcr):
    with request_vcr.use_cassette("create_policy.yaml"):
        policy = haize.code_of_conduct.create_policy(
            coc_id=coc.coc_id, policy="No harmful content"
        )
        return policy


@pytest.fixture
def dataset(haize: Haize, request_vcr):
    with request_vcr.use_cassette("create_dataset_fixture.yaml"):
        return haize.datasets.create(
            name="test_dataset_fixture",
            data=[{"input_text": "Hello", "expected_output": "Greeting"}],
        )


@pytest.fixture
def finished_red_team_test_id():
    return "fbf5baf5-7599-4502-9fa3-ff24475aa6b3"

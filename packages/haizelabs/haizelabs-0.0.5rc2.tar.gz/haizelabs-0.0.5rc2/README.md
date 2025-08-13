# Haize SDK

## Table of Contents

- [Installation](#installation)
- [Client Initialization](#client-initialization)
- [API Reference](#api-reference)
  - [AI Systems](#ai-systems)
  - [Code of Conduct](#code-of-conduct)
  - [Datasets](#datasets)
  - [Judges](#judges)
  - [Red Team Tests](#red-team-tests)
  - [Red Team Test Wrapper](#red-team-test-wrapper)
  - [Unit Tests](#unit-tests)

## Installation

```bash
# Install from GitHub
pip install git+https://github.com/haizelabs/haizelabs-sdk.git

# Install from source
pip install -e <path to haizelabs-sdk>
```

## Client Initialization

```python
from haizelabs import Haize, AsyncHaize

# Synchronous client
client = Haize(api_key="your-api-key")

# Asynchronous client  
client = AsyncHaize(api_key="your-api-key")
```

## API Reference

Most SDK method follow the pattern: `client.<resource>.<operation>()`

### AI Systems

```python
from haizelabs.models.ai_system import ThirdPartyProvider

# Create or update
system = await client.ai_systems.upsert_by_name(
    name="My System",
    model_id="gpt-4o-mini",
    provider=ThirdPartyProvider.OPENAI,
    api_key="optional-api-key",
    system_prompt="Optional system prompt",
    system_config={"temperature": 0.7}
)

# Get
system = await client.ai_systems.get(ai_system_id)

# Update
system = await client.ai_systems.update(
    ai_system_id,
    name="New Name",
    provider=ThirdPartyProvider.OPENAI
)

# Create
system = await client.ai_systems.create(
    name="My System",
    model_id="gpt-4o-mini",
    provider=ThirdPartyProvider.OPENAI,
    system_prompt="You are a helpful assistant"
)
```

### Code of Conduct

```python
# Create code of conduct
coc = await client.code_of_conduct.create(
    name="Company Policy",
    description="Content guidelines"
)

# Get
coc = await client.code_of_conduct.get(coc_id)

# Create policy
policy = await client.code_of_conduct.create_policy(
    coc_id,
    policy="No personal information"
)

# Get policy
policy = await client.code_of_conduct.get_policy(coc_id, policy_id)

# Get all policies
policies = await client.code_of_conduct.get_policies(coc_id)

# Create violation
violation = await client.code_of_conduct.create_violation(
    coc_id,
    policy_id,
    violation="Sharing user emails"
)

# Get violation
violation = await client.code_of_conduct.get_violation(coc_id, policy_id, violation_id)

# Get all violations
violations = await client.code_of_conduct.get_violations(coc_id)

# Update code of conduct
await client.code_of_conduct.update(coc_id, name="New Name")

# Update policy
await client.code_of_conduct.update_policy(coc_id, policy_id, policy="Updated policy")

# Update violation
await client.code_of_conduct.update_violation(coc_id, policy_id, violation_id, violation="Updated violation")

# Delete violation
await client.code_of_conduct.delete_violation(coc_id, policy_id, violation_id)

# Delete policy
await client.code_of_conduct.delete_policy(coc_id, policy_id)

# Delete code of conduct
await client.code_of_conduct.delete(coc_id)

# Convert violations to behavior requests for red team tests
behavior_requests = violations.to_behavior_requests()
```

### Datasets

```python
# Create dataset
dataset = await client.datasets.create(
    name="Test Dataset",
    data=[
        {"input": "Hello", "output": "Hi there"},
        {"input": "How are you?", "output": "I'm doing well"},
    ]
)

# Get dataset (latest version by default)
dataset = await client.datasets.get(dataset_id)

# Get specific version of dataset
dataset_v2 = await client.datasets.get(dataset_id, version=2)

# Update dataset (creates new version)
updated = await client.datasets.update(
    dataset_id=dataset.dataset_id,
    name="Test Dataset v2",
    data=[
        {"input": "Hello", "output": "Hi there!", "context": "greeting"},
        {"input": "Goodbye", "output": "See you later!", "context": "farewell"},
    ]
)

# Add rows to a specific dataset version
result = await client.datasets.add_rows(
    dataset_id=dataset.dataset_id,
    dataset_version=1,  # Specify the version to add rows to
    data=[
        {"input": "What's up?", "output": "Not much, you?", "context": "casual"},
        {"input": "Thanks!", "output": "You're welcome!", "context": "gratitude"},
    ]
)
print(f"Added {len(result.row_ids)} rows")
```

### Judges

**Important:** For STATIC_PROMPT / LLM as a judge, both `system_prompt` and `prompt_template` are required:
- `system_prompt`: Static instructions for the judge (no variables allowed)
- `prompt_template`: Template that receives variables, **must include `{system_output}`** to evaluate the AI's response, and optionally
can include any variable present in a dataset of a unit test.

```python
from haizelabs.models.judges import JudgeType
from haizelabs.models.label_types import ContinuousLabelType, EnumLabelType

# Static Prompt Judge - uses an LLM to evaluate
judge = await client.judges.create(
    name="Safety Judge",
    label_type=ContinuousLabelType(min_value=1, max_value=10),
    judge_type=JudgeType.STATIC_PROMPT,
    system_prompt="You are a safety evaluator. Rate responses from 1-10.",  # Required: static instructions
    prompt_template="Evaluate this response:\n\n{system_output}",  # Required: must include {system_output}
    ai_system_id=system_id
)

# Exact Match Judge - checks if output exactly matches a value
judge = await client.judges.create(
    name="Answer Judge",
    label_type=EnumLabelType(options=["correct", "incorrect"]),
    judge_type=JudgeType.EXACT_MATCH,
    default_match_value="expected_answer"
)

# Regex Match Judge - checks if output matches a pattern
judge = await client.judges.create(
    name="Format Judge",
    label_type=EnumLabelType(options=["valid", "invalid"]),
    judge_type=JudgeType.REGEX_MATCH,
    default_regex_pattern=r"^\d{3}-\d{3}-\d{4}$"  # Phone number pattern
)

# Get
judge = await client.judges.get(judge_id)  # Returns the Details about the judge directly
```

### Red Team Tests

```python
from haizelabs.models.behaviors import CodeOfConductBehaviorRequest, BehaviorType

# Run (create and start)
test = await client.red_team_tests.run(
    name="Test Name",
    system_id=system_id,
    judge_ids=[judge1_id, judge2_id],
    custom_behaviors=["Harmful requests", "Prompt injection"],
    creativity=5,  # 1-10
    attack_system_id=None  # Optional
)

# Create with code of conduct behaviors
response = await client.red_team_tests.create(
    name="Test Name",
    system_id=system_id,
    judge_ids=[judge_id],
    custom_behaviors=["Test behavior"],
    code_of_conduct_behaviors=[
        CodeOfConductBehaviorRequest(
            behavior="Policy violation",
            violation_id="v1",
            policy_id="p1",
            coc_id="c1",
            type=BehaviorType.CODE_OF_CONDUCT
        )
    ]
)

# Get
test = await client.red_team_tests.get(test_id)

# Start
await client.red_team_tests.start(test_id)

# Cancel
await client.red_team_tests.cancel(test_id)

# Get results
results = await client.red_team_tests.results(test_id)
```

### Red Team Test Wrapper

The `run()` method returns a wrapper with convenience methods:

```python
test = await client.red_team_tests.run(...)

# Properties
test.id
test.name
test.status
test.system_id
test.attack_system_id
test.judge_ids

# Methods
await test.poll(interval=10, timeout=3600)
await test.cancel()
results = await test.results()
metrics = await test.metrics()
dataset = await test.export_results_as_dataset(name, description, minimum_score)
await test.generate_report()
```

### Unit Tests

```python
# Create test dataset
dataset = await client.datasets.create(
    name="coding_tests",
    data=[
        {
            "task": "Write factorial function",
            "requirements": "Handle edge cases",
            "expected_output": "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)"
        },
        {
            "task": "Binary search",
            "requirements": "Return index or -1",
            "expected_output": "def binary_search(arr, target): # O(log n) implementation"
        },
    ]
)

# Create judge (BOTH system_prompt AND prompt_template required)
judge = await client.judges.create(
    name="code_quality_judge",
    judge_type=JudgeType.STATIC_PROMPT,
    system_prompt="You are an expert code reviewer. Rate from 1-10.",  # Required: static instructions
    prompt_template="""Task: {task}
Requirements: {requirements}
Expected: {expected_output}

Student's Solution:
{system_output}

Rate the quality from 1-10.""",  # Required: must include {system_output}
    label_type=ContinuousLabelType(min_value=1, max_value=10),
    ai_system_id=judge_system_id
)

# Create unit test
test = await client.unit_tests.create(
    name="Code Quality Test",
    system_id=system_id,  # The AI system being tested
    judge_ids=[judge.id],
    prompt_template="Task: {task}\nRequirements: {requirements}\n\nProvide a solution:",  # How to format prompts for the AI
    dataset_id=dataset.dataset_id,
    dataset_version=dataset.version
)

# Start and monitor
await client.unit_tests.start(test.test_id)
while True:
    test = await client.unit_tests.get(test.test_id)
    if test.status in [TestStatus.SUCCEEDED, TestStatus.FAILED]:
        break
    await asyncio.sleep(2)
```


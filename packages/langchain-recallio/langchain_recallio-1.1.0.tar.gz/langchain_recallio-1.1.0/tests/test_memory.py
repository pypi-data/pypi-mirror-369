import datetime
from unittest.mock import MagicMock

from langchain_recallio.memory import RecallioMemory


def test_save_context_adds_tags_and_calls_client():
    mock_client = MagicMock()
    memory = RecallioMemory(
        api_key="key",
        project_id="proj",
        user_id="user",
        session_id="s123",
    )
    object.__setattr__(memory, "_client", mock_client)
    memory.save_context({"input": "hi"}, {"output": "there"})
    args, _ = mock_client.write_memory.call_args
    assert args[0].tags and "session:s123" in args[0].tags


def test_load_memory_filters_expired():
    mock_client = MagicMock()
    exp_time = (datetime.datetime.utcnow() - datetime.timedelta(seconds=1)).isoformat() + "Z"
    mock_client.recall_memory.return_value = [
        MagicMock(content="expired", tags=[f"expiresAt:{exp_time}"]),
        MagicMock(content="valid", tags=[]),
    ]
    memory = RecallioMemory(
        api_key="key",
        project_id="proj",
        user_id="user",
    )
    object.__setattr__(memory, "_client", mock_client)
    result = memory.load_memory_variables({"input": ""})
    assert "valid" in result[memory.memory_key]
    assert "expired" not in result[memory.memory_key]

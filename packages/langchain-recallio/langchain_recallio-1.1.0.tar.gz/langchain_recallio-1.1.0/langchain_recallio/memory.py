from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional

from langchain_core.memory import BaseMemory
from langchain_core.messages import HumanMessage, get_buffer_string
from pydantic import PrivateAttr
from recallio.client import RecallioClient
from recallio.models import MemoryWriteRequest, MemoryRecallRequest, MemoryDeleteRequest


class RecallioMemory(BaseMemory):
    """LangChain memory backed by Recallio."""

    project_id: str
    user_id: str
    session_id: Optional[str] = None
    consent_flag: bool = True
    memory_key: str = "history"
    input_key: str = "input"
    output_key: str = "output"
    return_messages: bool = False
    ttl_seconds: Optional[int] = None
    similarity_threshold: float = 0.3
    limit: int = 10
    scope: str = "user"
    default_tags: Optional[List[str]] = None

    _client: RecallioClient = PrivateAttr(default=None)

    def __init__(
        self,
        api_key: str,
        project_id: str,
        user_id: str,
        *,
        session_id: Optional[str] = None,
        consent_flag: bool = True,
        memory_key: str = "history",
        input_key: str = "input",
        output_key: str = "output",
        return_messages: bool = False,
        ttl_seconds: Optional[int] = None,
        similarity_threshold: float = 0.3,
        limit: int = 10,
        scope: str = "user",
        default_tags: Optional[List[str]] = None,
        base_url: str = "https://app.recallio.ai",
    ) -> None:
        super().__init__(
            project_id=project_id,
            user_id=user_id,
            session_id=session_id,
            consent_flag=consent_flag,
            memory_key=memory_key,
            input_key=input_key,
            output_key=output_key,
            return_messages=return_messages,
            ttl_seconds=ttl_seconds,
            similarity_threshold=similarity_threshold,
            limit=limit,
            scope=scope,
            default_tags=default_tags,
        )
        object.__setattr__(
            self, "_client", RecallioClient(api_key=api_key, base_url=base_url)
        )

    @property
    def memory_variables(self) -> List[str]:
        return [self.memory_key]

    def _expires_tag(self) -> Optional[str]:
        if self.ttl_seconds is None:
            return None
        expire_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=self.ttl_seconds)
        return f"expiresAt:{expire_at.isoformat()}Z"

    def _session_tag(self) -> Optional[str]:
        if self.session_id:
            return f"session:{self.session_id}"
        return None

    def _build_tags(self) -> List[str]:
        tags = list(self.default_tags or [])
        session_tag = self._session_tag()
        if session_tag:
            tags.append(session_tag)
        expires_tag = self._expires_tag()
        if expires_tag:
            tags.append(expires_tag)
        return tags

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        query = inputs.get(self.input_key, "")
        tags = []
        session_tag = self._session_tag()
        if session_tag:
            tags.append(session_tag)
        request = MemoryRecallRequest(
            projectId=self.project_id,
            userId=self.user_id,
            query=query or "*",
            scope=self.scope,
            tags=tags or None,
            limit=self.limit,
            similarityThreshold=self.similarity_threshold,
            summarized=False,
            reRank=False,
        )
        results = self._client.recall_memory(request)

        filtered = []
        now = datetime.datetime.now(datetime.timezone.utc)
        for m in results:
            expires = None
            if m.tags:
                for t in m.tags:
                    if t.startswith("expiresAt:"):
                        try:
                            expires = datetime.datetime.fromisoformat(t.split(":", 1)[1].replace("Z", "+00:00"))
                        except ValueError:
                            pass
                        break
            if expires and expires < now:
                continue
            filtered.append(m)

        if self.return_messages:
            messages = [HumanMessage(content=rec.content) for rec in filtered]
            return {self.memory_key: messages}

        history = get_buffer_string([HumanMessage(content=rec.content) for rec in filtered])
        return {self.memory_key: history}

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        input_str = inputs.get(self.input_key, "")
        output_str = outputs.get(self.output_key, "")
        content = f"Human: {input_str}\nAI: {output_str}"
        tags = self._build_tags()
        request = MemoryWriteRequest(
            userId=self.user_id,
            projectId=self.project_id,
            content=content,
            consentFlag=self.consent_flag,
            tags=tags or None,
        )
        self._client.write_memory(request)

    def clear(self) -> None:
        request = MemoryDeleteRequest(scope=self.scope, userId=self.user_id, projectId=self.project_id)
        self._client.delete_memory(request)

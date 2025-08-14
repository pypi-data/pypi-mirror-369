from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, field_validator

from .. import utils
from .base import ErrorResponse, Metadata
from .workflow import (
    NodeFinishedData,
    NodeStartedData,
    WorkflowFinishedData,
    WorkflowStartedData,
)


STREAM_EVENT_KEY = "event"


class StreamEvent(str, Enum):
    MESSAGE = "message"
    AGENT_MESSAGE = "agent_message"
    AGENT_THOUGHT = "agent_thought"
    MESSAGE_FILE = "message_file"  # need to show file
    WORKFLOW_STARTED = "workflow_started"
    NODE_STARTED = "node_started"
    NODE_FINISHED = "node_finished"
    WORKFLOW_FINISHED = "workflow_finished"
    MESSAGE_END = "message_end"
    MESSAGE_REPLACE = "message_replace"
    ERROR = "error"
    PING = "ping"
    TTS_MESSAGE_END = "tts_message_end"
    PARALLEL_BRANCH_STARTED = "parallel_branch_started"
    PARALLEL_BRANCH_FINISHED = "parallel_branch_finished"
    AGENT_LOG = "agent_log"

    @classmethod
    def new(cls, event: Union["StreamEvent", str]) -> "StreamEvent":
        if isinstance(event, cls):
            return event
        return utils.str_to_enum(cls, event)


class StreamResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    event: StreamEvent
    task_id: Optional[str] = ""

    @field_validator("event", mode="before")
    def transform_stream_event(
        cls, event: Union[StreamEvent, str]
    ) -> StreamEvent:
        return StreamEvent.new(event)


class PingResponse(StreamResponse):
    pass


class ErrorStreamResponse(StreamResponse, ErrorResponse):
    message_id: Optional[str] = ""


class MessageStreamResponse(StreamResponse):
    message_id: str
    conversation_id: Optional[str] = ""
    answer: str
    created_at: int  # unix timestamp seconds


class MessageEndStreamResponse(StreamResponse):
    message_id: str
    conversation_id: Optional[str] = ""
    created_at: int  # unix timestamp seconds
    metadata: Optional[Metadata]


class MessageReplaceStreamResponse(MessageStreamResponse):
    pass


class AgentMessageStreamResponse(MessageStreamResponse):
    pass


class AgentThoughtStreamResponse(StreamResponse):
    id: str  # agent thought id
    message_id: str
    conversation_id: str
    position: int  # thought position, start from 1
    thought: str
    observation: str
    tool: str
    tool_input: str
    message_files: List[str] = []
    created_at: int  # unix timestamp seconds


class AgentLogStreamResponse(StreamResponse):
    """
    Stream dify chunk:  event=<StreamEvent.AGENT_LOG: 'agent_log'>
    task_id='9f1a9fc8-431c-46fe-b241-ef2510fa961e'
    conversation_id='eccdf537-45d5-4f59-8eda-492b7a91e092'
    message_id='2e74ebaf-0615-480d-b2f5-977b39ec3db0'
    created_at=1748419593
    data={'node_execution_id': '5d9e94fb-aa5c-4b9c-9c9e-25cb5c0b8ac5', 'id': '2f91059f-c113-44ce-937b-190cdd261d0d', 'label': 'ROUND 2', 'parent_id': None, 'error': None, 'status': 'start', 'data': {}, 'metadata': {'started_at': 4035.24719685}, 'node_id': '1747043855390'}
    """

    conversation_id: str
    message_id: str
    created_at: int
    data: dict


class MessageFileStreamResponse(StreamResponse):
    id: str  # file id
    conversation_id: str
    type: str  # only image
    belongs_to: str  # assistant
    url: str


class WorkflowsStreamResponse(StreamResponse):
    workflow_run_id: str
    data: Optional[
        Union[
            WorkflowStartedData,
            WorkflowFinishedData,
            NodeStartedData,
            NodeFinishedData,
        ]
    ]


class ChatWorkflowsStreamResponse(WorkflowsStreamResponse):
    message_id: str
    conversation_id: str
    created_at: int


_COMPLETION_EVENT_TO_STREAM_RESP_MAPPING = {
    StreamEvent.PING: PingResponse,
    StreamEvent.MESSAGE: MessageStreamResponse,
    StreamEvent.MESSAGE_END: MessageEndStreamResponse,
    StreamEvent.MESSAGE_REPLACE: MessageReplaceStreamResponse,
}

CompletionStreamResponse = Union[
    PingResponse,
    MessageStreamResponse,
    MessageEndStreamResponse,
    MessageReplaceStreamResponse,
]


def build_completion_stream_response(data: dict) -> CompletionStreamResponse:
    event = StreamEvent.new(data.get(STREAM_EVENT_KEY))
    return _COMPLETION_EVENT_TO_STREAM_RESP_MAPPING.get(event, StreamResponse)(
        **data
    )


_CHAT_EVENT_TO_STREAM_RESP_MAPPING = {
    StreamEvent.PING: PingResponse,
    # chat
    StreamEvent.MESSAGE: MessageStreamResponse,
    StreamEvent.MESSAGE_END: MessageEndStreamResponse,
    StreamEvent.MESSAGE_REPLACE: MessageReplaceStreamResponse,
    StreamEvent.MESSAGE_FILE: MessageFileStreamResponse,
    # agent
    StreamEvent.AGENT_MESSAGE: AgentMessageStreamResponse,
    StreamEvent.AGENT_THOUGHT: AgentThoughtStreamResponse,
    # workflow
    StreamEvent.WORKFLOW_STARTED: WorkflowsStreamResponse,
    StreamEvent.NODE_STARTED: WorkflowsStreamResponse,
    StreamEvent.NODE_FINISHED: WorkflowsStreamResponse,
    StreamEvent.WORKFLOW_FINISHED: WorkflowsStreamResponse,
}

ChatStreamResponse = Union[
    PingResponse,
    MessageStreamResponse,
    MessageEndStreamResponse,
    MessageReplaceStreamResponse,
    MessageFileStreamResponse,
    AgentMessageStreamResponse,
    AgentThoughtStreamResponse,
    WorkflowsStreamResponse,
    AgentLogStreamResponse,
]


def build_chat_stream_response(data: dict) -> ChatStreamResponse:
    event = StreamEvent.new(data.get(STREAM_EVENT_KEY))
    return _CHAT_EVENT_TO_STREAM_RESP_MAPPING.get(event, StreamResponse)(
        **data
    )


_WORKFLOW_EVENT_TO_STREAM_RESP_MAPPING = {
    StreamEvent.PING: PingResponse,
    # workflow
    StreamEvent.WORKFLOW_STARTED: WorkflowsStreamResponse,
    StreamEvent.NODE_STARTED: WorkflowsStreamResponse,
    StreamEvent.NODE_FINISHED: WorkflowsStreamResponse,
    StreamEvent.WORKFLOW_FINISHED: WorkflowsStreamResponse,
}

WorkflowsRunStreamResponse = Union[
    PingResponse,
    WorkflowsStreamResponse,
]


def build_workflows_stream_response(data: dict) -> WorkflowsRunStreamResponse:
    event = StreamEvent.new(data.get(STREAM_EVENT_KEY))
    return _WORKFLOW_EVENT_TO_STREAM_RESP_MAPPING.get(event, StreamResponse)(
        **data
    )

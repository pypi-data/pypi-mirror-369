import asyncio
import os
import uuid

from dify_client import AsyncDifyClient, models

# Initialize the async client with your API key
async_client = AsyncDifyClient(
    api_key=os.getenv("DIFY_API_KEY"),
    api_base=os.getenv("DIFY_API_BASE"),
)


# Define an asynchronous function to send a chat message with STREAMING ResponseMode
async def send_chat_message_stream():
    user = str(uuid.uuid4())
    # Create a blocking chat request
    streaming_chat_req = models.ChatRequest(
        query="My name is Lucas",
        inputs={
            "username": "Elio",
            "user_current_time": "Fri, 01 Aug 2025 11:50:05",
            "language_code": "en",
            "command": "",
            "cmd_user_idle_duration": 0,
            "cmd_user_idle_scenario": 1,
            "video_id": "C0488",
            "avatar_tag": "reimien",
            "avatar_code": "reimi",
            "channel_id": "5cda6eac-aa33-4097-a471-70ebb2bfd16a_f89605f8-317a-4b50-b4ef-face5fcb3b58",
            "video_id_tag": "C0488",
            "cmd_new_username": "",
            "language_code_for_video": "en",
            "has_template_qa": 0,
            "is_change_name_supported": 1,
            "cmd_user_fortune_telling": None,
            "cmd_user_zodiac_sign": None,
            "cmd_user_lucky_color": None,
            "cmd_user_lucky_item": None,
        },
        user=user,
        response_mode=models.ResponseMode.STREAMING,
    )
    async for chunk in await async_client.achat_messages(
        streaming_chat_req, timeout=60.0
    ):
        if chunk.event == models.StreamEvent.AGENT_LOG:
            print(f"Chunk AGENT_LOG info: {chunk}")
            # chunk = cast(models.AgentLogStreamResponse, chunk)

            # print(chunk.data)
        elif chunk.event == models.StreamEvent.WORKFLOW_FINISHED:
            print(f"Chunk WORKFLOW_FINISHED info: {chunk}")
            # chunk = cast(models.ChatWorkflowsStreamResponse, chunk)
            # chunk.data = cast(models.WorkflowFinishedData, chunk.data)
            # answer = (
            #     chunk.data.outputs.get("answer", "")
            #     if chunk.data.outputs
            #     else ""
            # )
            # conversation_id = chunk.conversation_id
            # message_id = chunk.message_id
            # created_at = chunk.created_at
        else:
            print(f"Chunk info: {chunk}")


# Run the asynchronous function
if __name__ == "__main__":
    asyncio.run(send_chat_message_stream())

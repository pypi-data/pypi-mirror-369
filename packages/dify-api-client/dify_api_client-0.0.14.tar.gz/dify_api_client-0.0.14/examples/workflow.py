import asyncio
import os
import uuid

import dotenv

from dify_client import AsyncDifyClient, DifyClient, models


dotenv.load_dotenv()

# Set your environment variables or replace with your actual values:
# export DIFY_API_KEY="app-xxxxxxxx"
# export DIFY_API_BASE="https://uat-dify-llm.xxx/v1"

# Initialize the sync client with your API key
sync_client = DifyClient(
    api_key=os.getenv("DIFY_API_KEY"),
    api_base=os.getenv("DIFY_API_BASE"),
)

# Initialize the async client with your API key
async_client = AsyncDifyClient(
    api_key=os.getenv("DIFY_API_KEY"),
    api_base=os.getenv("DIFY_API_BASE"),
)

MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """
**Role:**
You are a professional recruiter communication assistant. Your goal is to take a draft scout message intended for a job candidate and rewrite it so it is clear, engaging, professional, and persuasive.

**Objective:**

* Maintain accurate information from the original draft.
* Make the tone professional yet warm and approachable.
* Ensure the message is concise, well-structured, and free from grammatical errors.
* Highlight the opportunity in a compelling way while showing genuine interest in the candidate.

**Instructions:**

1. Read the draft scout message provided as input.
2. Preserve all correct facts, numbers, and key job details.
3. Rewrite for:

   * Clear, natural flow
   * Positive and inviting tone
   * Professional grammar and formatting
   * Candidate-centric language (focus on how the role benefits them)
4. Keep the length appropriate (short enough to be read quickly, long enough to convey key points).
5. Avoid overly generic recruiter clichés — make it feel personal and authentic.
6. If needed, suggest optional variations (e.g., short LinkedIn message version and longer email version).

**Output Format:**
* Only output the improved rewritten message. Do not add explanations, bullet points, or extra text.
"""

QUERY = """
Hi John,  
We are looking for a Backend Engineer with Python. The job is in Singapore.  
If interested, please send CV. 
"""


def run_workflow_sync():
    """Run a workflow synchronously using the sync client."""
    user = str(uuid.uuid4())

    # Create a workflow run request matching the curl command
    workflow_req = models.WorkflowsRunRequest(
        inputs={
            "model": MODEL,
            "system_prompt": SYSTEM_PROMPT,
            "query": QUERY,
        },
        response_mode=models.ResponseMode.BLOCKING,
        user=user,
    )

    try:
        # Run the workflow
        response = sync_client.run_workflows(workflow_req)
        print(f"Workflow run ID: {response.workflow_run_id}")
        print(f"Task ID: {response.task_id}")
        print(f"Status: {response.data.status}")
        print(f"Outputs: {response.data.outputs}")
        print(f"Elapsed time: {response.data.elapsed_time} seconds")
        if response.data.total_tokens:
            print(f"Total tokens: {response.data.total_tokens}")
        return response
    except Exception as e:
        print(f"Error running workflow: {e}")
        return None


async def run_workflow_async():
    """Run a workflow asynchronously using the async client."""
    user = str(uuid.uuid4())

    # Create a workflow run request matching the curl command
    workflow_req = models.WorkflowsRunRequest(
        inputs={
            "model": MODEL,
            "system_prompt": SYSTEM_PROMPT,
            "query": QUERY,
        },
        response_mode=models.ResponseMode.BLOCKING,
        user=user,
    )

    try:
        # Run the workflow
        response = await async_client.arun_workflows(workflow_req)
        print(f"Workflow run ID: {response.workflow_run_id}")
        print(f"Task ID: {response.task_id}")
        print(f"Status: {response.data.status}")
        print(f"Outputs: {response.data.outputs}")
        print(f"Elapsed time: {response.data.elapsed_time} seconds")
        if response.data.total_tokens:
            print(f"Total tokens: {response.data.total_tokens}")
        return response
    except Exception as e:
        print(f"Error running workflow: {e}")
        return None


if __name__ == "__main__":
    print("=== Running Workflow Examples ===\n")

    print("1. Synchronous workflow execution:")
    print("-" * 40)
    run_workflow_sync()
    print()

    print("2. Asynchronous workflow execution:")
    print("-" * 40)
    asyncio.run(run_workflow_async())
    print()

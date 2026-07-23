import os
import asyncio
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI

from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.functions import KernelArguments

from device_support_plugin import DeviceSupportPlugin


# ============================================================
# 1. Load Environment Variables
# ============================================================

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name = os.getenv(
    "AZURE_OPENAI_DEPLOYMENT_NAME",
    "gpt-5.4-mini",
)

if not azure_api_key:
    raise RuntimeError(
        "AZURE_OPENAI_API_KEY was not found in the .env file."
    )

if not azure_endpoint:
    raise RuntimeError(
        "AZURE_OPENAI_ENDPOINT was not found in the .env file."
    )


# ============================================================
# 2. Configure Azure OpenAI v1 Client
# ============================================================

base_url = azure_endpoint.rstrip("/")

if not base_url.endswith("/openai/v1"):
    base_url = f"{base_url}/openai/v1"

azure_client = AsyncOpenAI(
    api_key=azure_api_key,
    base_url=base_url,
    default_headers={
        "api-key": azure_api_key,
    },
)


# ============================================================
# 3. Create Semantic Kernel
# ============================================================

kernel = Kernel()

kernel.add_service(
    OpenAIChatCompletion(
        service_id="chat_service",
        ai_model_id=deployment_name,
        async_client=azure_client,
    )
)


# ============================================================
# 4. Register the IT Support Plugin
# ============================================================

kernel.add_plugin(
    DeviceSupportPlugin(),
    plugin_name="DeviceSupport",
)


# ============================================================
# 5. Configure Automatic Function Calling
# ============================================================

support_agent_settings = (
    kernel.get_prompt_execution_settings_from_service_id(
        "chat_service"
    )
)

support_agent_settings.function_choice_behavior = (
    FunctionChoiceBehavior.Auto(
        filters={
            "included_functions": [
                "DeviceSupport-get_device_information",
                "DeviceSupport-get_recent_updates",
                "DeviceSupport-create_support_ticket",
            ],
        }
    )
)


# ============================================================
# 6. Create the Single IT Support Agent
# ============================================================

support_agent = ChatCompletionAgent(
    id="ITSupportAgent",
    name="ITSupportAgent",
    instructions="""
You are an IT support agent responsible for investigating
and escalating employee laptop problems.

Follow this workflow:

1. Identify the technical issue reported by the employee.

2. When the employee provides an employee ID, call
   DeviceSupport.get_device_information to retrieve the employee's
   device and operating system information.

3. Call DeviceSupport.get_recent_updates to retrieve the recent
   Windows update history for the device.

4. Use the tool results to determine the likely cause of the issue.

5. You MUST call DeviceSupport.create_support_ticket when:
   - The update history reports that multiple devices are affected.
   - The recommended action says that escalation is required.
   - The required remediation could cause data loss.
   - The employee should not perform the remediation without IT approval.

6. After creating the ticket, include the ticket ID, priority,
   assigned team, and status in the final response.

Rules:
- Never invent device details, update details, or ticket details.
- Never claim that a tool was executed unless it was actually called.
- Do not recommend uninstalling a security or cumulative update
  without IT approval.
- Base the diagnosis only on the user request and tool results.
- Clearly separate findings, likely cause, action taken,
  and recommended next steps.
- Keep the final response concise, structured, and professional.
""",
    kernel=kernel,
    arguments=KernelArguments(
        settings=support_agent_settings
    ),
)


# ============================================================
# 7. Invoke the Agent
# ============================================================

async def main() -> None:
    user_request = """
My employee ID is EMP-1024.

My laptop has been crashing since yesterday's Windows update.

Please:
- Check my device information.
- Review the recent Windows updates.
- Identify the likely cause.
- Escalate the issue if IT intervention is required.
"""

    print("\n" + "=" * 70)
    print("USER REQUEST")
    print("=" * 70)
    print(user_request.strip())
    print("=" * 70)

    try:
        async for response in support_agent.invoke(
            messages=user_request
        ):
            print("\n" + "=" * 70)
            print(response.name or "ITSupportAgent")
            print("=" * 70)
            print(response.content)
            print("=" * 70)

    except Exception as error:
        print("\n" + "=" * 70)
        print("AGENT EXECUTION FAILED")
        print("=" * 70)
        print(f"Error type: {type(error).__name__}")
        print(f"Error details: {error}")
        print("=" * 70)
        raise


if __name__ == "__main__":
    asyncio.run(main())
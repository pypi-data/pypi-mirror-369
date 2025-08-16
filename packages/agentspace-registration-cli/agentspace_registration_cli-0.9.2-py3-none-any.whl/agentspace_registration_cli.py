"""Agent registration management script for Agentspace"""

import asyncio
import json
import subprocess

import httpx
from absl import app, flags

FLAGS = flags.FLAGS

# --- Command-line Flags ---
flags.DEFINE_string("project_id", None, "The ID of your Google Cloud project.")
flags.DEFINE_string(
    "app_id",
    None,
    "The ID of the Agentspace app. "
    "Retrieve this from the 'ID' column in AI Applications page.",
)
flags.DEFINE_string("display_name", None, "The display name of the agent.")
flags.DEFINE_string(
    "description", None, "The description of the agent, displayed on the frontend."
)
flags.DEFINE_string(
    "icon_uri",
    None,
    "The public URI of the icon to display near the name of the agent.",
)
flags.DEFINE_string(
    "tool_description",
    None,
    "The description/prompt of the agent used by the LLM to route requests.",
)
flags.DEFINE_string(
    "adk_deployment_id",
    None,
    "The ID of the reasoning engine endpoint where the ADK agent is deployed. "
    "Retrieve this from the 'Agent Engine Details' page (format: '5093550707281667376').",
)
flags.DEFINE_list("auth_ids", [], "Optional: The IDs of the authorization resources.")
flags.DEFINE_string("agent_id", None, "The ID of the agent to view or delete.")

# Location flags for different services
flags.DEFINE_string(
    "discovery_location",
    "global",
    "Location where your Agentspace app is created. "
    "Verify this from the 'Location' column in AI Applications page (e.g., 'us-central1', 'global').",
)
flags.DEFINE_string(
    "reasoning_location",
    "global",
    "Location where your reasoning engine is deployed. "
    "Check the 'Agent Engine Details' page for the correct location.",
)
flags.DEFINE_string(
    "auth_location",
    "global",
    "Location where your authorization resources are created.",
)


def get_access_token() -> str:
    """Gets the gcloud access token."""
    return subprocess.check_output(
        ["gcloud", "auth", "print-access-token"], text=True
    ).strip()


def get_discovery_engine_base_url() -> str:
    """Gets the correct Discovery Engine base URL based on location."""
    if FLAGS.discovery_location == "us":
        return "https://us-discoveryengine.googleapis.com/v1alpha"
    elif FLAGS.discovery_location == "eu":
        return "https://eu-discoveryengine.googleapis.com/v1alpha"
    else:
        # For global or any other location, use the standard endpoint
        return "https://discoveryengine.googleapis.com/v1alpha"


async def register_agent():
    """Registers an agent in Agentspace."""
    if not all(
        [
            FLAGS.project_id,
            FLAGS.app_id,
            FLAGS.display_name,
            FLAGS.description,
            FLAGS.tool_description,
            FLAGS.adk_deployment_id,
        ]
    ):
        print("Error: Missing one or more required flags for registration.")
        print(
            "Required: --project_id, --app_id, --display_name, --description, --tool_description, --adk_deployment_id"
        )
        return

    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": FLAGS.project_id,
    }

    base_url = get_discovery_engine_base_url()
    url = f"{base_url}/projects/{FLAGS.project_id}/locations/{FLAGS.discovery_location}/collections/default_collection/engines/{FLAGS.app_id}/assistants/default_assistant/agents"

    data = {
        "displayName": FLAGS.display_name,
        "description": FLAGS.description,
        "adk_agent_definition": {
            "tool_settings": {
                "tool_description": FLAGS.tool_description,
            },
            "provisioned_reasoning_engine": {
                "reasoning_engine": f"projects/{FLAGS.project_id}/locations/{FLAGS.reasoning_location}/reasoningEngines/{FLAGS.adk_deployment_id}",
            },
        },
    }

    if FLAGS.icon_uri:
        data["icon"] = {"uri": FLAGS.icon_uri}

    if FLAGS.auth_ids:
        data["adk_agent_definition"]["authorizations"] = [
            f"projects/{FLAGS.project_id}/locations/{FLAGS.auth_location}/authorizations/{auth_id}"
            for auth_id in FLAGS.auth_ids
        ]

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=data, timeout=30.0)
            response.raise_for_status()
            response_data = response.json()
            agent_name = response_data.get("name", "")
            agent_id = agent_name.split("/")[-1]

            print("Agent registered successfully!")
            if agent_id:
                print(f"Agent ID: {agent_id} (Note this ID for future operations)")
            print("---")
            print("Full response:")
            print(json.dumps(response_data, indent=2))
        except httpx.HTTPStatusError as e:
            print(f"Error registering agent: {e.response.status_code}")
            print(f"Response: {e.response.text}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


async def view_agent():
    """Views a specific agent in Agentspace."""
    if not all([FLAGS.project_id, FLAGS.app_id, FLAGS.agent_id]):
        print("Error: Missing one or more required flags for viewing.")
        print("Required: --project_id, --app_id, --agent_id")
        return

    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": FLAGS.project_id,
    }

    base_url = get_discovery_engine_base_url()
    url = f"{base_url}/projects/{FLAGS.project_id}/locations/{FLAGS.discovery_location}/collections/default_collection/engines/{FLAGS.app_id}/assistants/default_assistant/agents/{FLAGS.agent_id}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            print("Agent details retrieved successfully!")
            print(json.dumps(response.json(), indent=2))
        except httpx.HTTPStatusError as e:
            print(f"Error retrieving agent: {e.response.status_code}")
            print(f"Response: {e.response.text}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


async def list_agents():
    """Lists all agents in an Agentspace app."""
    if not all([FLAGS.project_id, FLAGS.app_id]):
        print("Error: Missing one or more required flags for listing.")
        print("Required: --project_id, --app_id")
        return

    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": FLAGS.project_id,
    }

    base_url = get_discovery_engine_base_url()
    url = f"{base_url}/projects/{FLAGS.project_id}/locations/{FLAGS.discovery_location}/collections/default_collection/engines/{FLAGS.app_id}/assistants/default_assistant/agents"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            print("Agents retrieved successfully!")
            print(json.dumps(response.json(), indent=2))
        except httpx.HTTPStatusError as e:
            print(f"Error retrieving agents: {e.response.status_code}")
            print(f"Response: {e.response.text}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


async def update_agent():
    """Updates an existing agent in Agentspace."""
    if not all(
        [
            FLAGS.project_id,
            FLAGS.app_id,
            FLAGS.agent_id,
            FLAGS.display_name,
            FLAGS.description,
            FLAGS.tool_description,
            FLAGS.adk_deployment_id,
        ]
    ):
        print("Error: Missing one or more required flags for updating.")
        print(
            "Required: --project_id, --app_id, --agent_id, --display_name, --description, --tool_description, --adk_deployment_id"
        )
        return

    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": FLAGS.project_id,
    }

    base_url = get_discovery_engine_base_url()
    url = f"{base_url}/projects/{FLAGS.project_id}/locations/{FLAGS.discovery_location}/collections/default_collection/engines/{FLAGS.app_id}/assistants/default_assistant/agents/{FLAGS.agent_id}"

    data = {
        "displayName": FLAGS.display_name,
        "description": FLAGS.description,
        "adk_agent_definition": {
            "tool_settings": {
                "tool_description": FLAGS.tool_description,
            },
            "provisioned_reasoning_engine": {
                "reasoning_engine": f"projects/{FLAGS.project_id}/locations/{FLAGS.reasoning_location}/reasoningEngines/{FLAGS.adk_deployment_id}",
            },
        },
    }

    if FLAGS.icon_uri:
        data["icon"] = {"uri": FLAGS.icon_uri}

    if FLAGS.auth_ids:
        data["adk_agent_definition"]["authorizations"] = [
            f"projects/{FLAGS.project_id}/locations/{FLAGS.auth_location}/authorizations/{auth_id}"
            for auth_id in FLAGS.auth_ids
        ]

    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(url, headers=headers, json=data, timeout=30.0)
            response.raise_for_status()
            print(f"Agent with ID '{FLAGS.agent_id}' updated successfully.")
            print("---")
            print("Full response:")
            print(json.dumps(response.json(), indent=2))
        except httpx.HTTPStatusError as e:
            print(f"Error updating agent: {e.response.status_code}")
            print(f"Response: {e.response.text}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


async def delete_agent():
    """Deletes a specific agent from Agentspace."""
    if not all([FLAGS.project_id, FLAGS.app_id, FLAGS.agent_id]):
        print("Error: Missing one or more required flags for deletion.")
        print("Required: --project_id, --app_id, --agent_id")
        return

    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": FLAGS.project_id,
    }

    base_url = get_discovery_engine_base_url()
    url = f"{base_url}/projects/{FLAGS.project_id}/locations/{FLAGS.discovery_location}/collections/default_collection/engines/{FLAGS.app_id}/assistants/default_assistant/agents/{FLAGS.agent_id}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            print(f"Agent with ID '{FLAGS.agent_id}' deleted successfully.")
        except httpx.HTTPStatusError as e:
            print(f"Error deleting agent: {e.response.status_code}")
            print(f"Response: {e.response.text}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


def main_cli() -> None:
    """Main entry point for the CLI script."""

    # absl.app.run() expects to be called with a main function,
    # so we wrap our logic in a little helper.
    def run_action(argv):
        if len(argv) < 2:
            print(
                "Error: No action specified. Please specify 'register', 'view', 'list', 'update', or 'delete'."
            )
            return

        action = argv[1]

        if action == "register":
            asyncio.run(register_agent())
        elif action == "view":
            asyncio.run(view_agent())
        elif action == "list":
            asyncio.run(list_agents())
        elif action == "update":
            asyncio.run(update_agent())
        elif action == "delete":
            asyncio.run(delete_agent())
        else:
            print(f"Unknown action: {action}")

    app.run(run_action)


if __name__ == "__main__":
    main_cli()

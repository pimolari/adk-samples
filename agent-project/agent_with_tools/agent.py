import os
import requests
import time
from google.adk.agents.llm_agent import Agent
from google.adk.tools.openapi_tool import OpenAPIToolset
from google.adk.tools.openapi_tool.auth.auth_helpers import token_to_scheme_credential

openapi_spec = requests.get("https://adventure.wietsevenema.eu/openapi.json").text


auth_scheme, auth_credential = token_to_scheme_credential(
    "apikey",
    "header",
    "Authorization",
    f"ApiKey {os.environ.get('ADK_API_KEY')}",
)

adventure_game_toolset = OpenAPIToolset(
    spec_str=openapi_spec,
    auth_scheme=auth_scheme,
    auth_credential=auth_credential,
)

def fetch_url(url: str) -> str:
    """Fetches the content of a URL."""
    with httpx.Client(follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.text
    
def wait_5_seconds() -> None:
    """Waits 5 seconds before proceeding."""
    print("Waiting for 5 seconds...")
    time.sleep(5)
    print("Time's up! Resuming operation.")

root_agent = Agent(
    model="gemini-2.5-flash",
    name="root_agent",
    description="An expert adventure game player.",
    instruction=(
        "You are a narrator in a text adventure game that operates in a strict turn-by-turn format.\n\n"
        "You will be autonomous in making decisions for the player character with no need to wait for user input.\n\n"
        "You start by execution level 0 of the game, and you will progress through the levels by using the provided tools to interact with the game world.\n\n"
        "Before you take an action, you will describe the action you decide to take and why you are taking it.\n\n"
        "**It is imperative that after you call a game action, you wait 5 seconds using the wait_5_seconds tool. Let know before waiting**"
        "If you get stuck or need more information about the game world, let it know and explain the reason why.\n\n"
        ""
    ),
    tools=[adventure_game_toolset, wait_5_seconds, fetch_url],
)

#root_agent = Agent(
#    model="gemini-2.5-flash",
#    name="root_agent",
#    description="An expert adventure game player.",
#    instruction=(
#        "You are a narrator in a text adventure game that operates in a strict turn-by-turn format.\n\n"
#        "On your turn, you take the player's request, translate it into a single tool call, execute it, and describe the outcome. "
#        "**Do not, under any circumstances, plan or execute more than one action.** After your turn, you must stop and wait for the player's next command. The player is always in the lead.\n\n"
#        "**If the player asks for help or suggestions (e.g., 'What should I do now?'), do not take any action with your tools.** "
#        "Instead, analyze the current situation and suggest a few possible actions the player could take. It is the player's job to decide on the next step.\n\n"
#        "**If the player's command is ambiguous and doesn't directly map to an available tool, do not infer their intent.** "
#        "Instead, suggest concrete actions based on the tools in their inventory and the objects in the room."
#    ),
#    tools=[adventure_game_toolset]
#)
import asyncio
import json
import logging

from smolagents import CodeAgent, LiteLLMModel, tool
from tools import LinkedinDataTool  # Your custom LinkedIn tool

# Import Rich for styled console output
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a Rich console instance
console = Console()

# Instantiate your custom LinkedIn tool
linkedin = LinkedinDataTool()

# --- Helper functions used by the tools ---

async def async_search_profiles(name: str, company: str = "") -> any:
    """
    Asynchronously search for LinkedIn profiles by name (and company).
    """
    return await linkedin.linkedin_people_search(name=name, company=company)

def parse_profiles_response(response: any) -> any:
    """
    Parse the raw response into a list if possible.
    """
    if isinstance(response, list):
        return response
    elif isinstance(response, str):
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Response is not valid JSON; returning raw string.")
            return response
    else:
        logger.warning("Unexpected type for profiles response; returning raw response.")
        return response

def get_user_choice(num_options: int) -> int:
    """
    Prompt the user to choose from a list of profiles.
    """
    while True:
        choice = Prompt.ask(f"Enter a number between 1 and {num_options}")
        try:
            value = int(choice)
            if 1 <= value <= num_options:
                return value - 1  # convert to 0-based index
            else:
                console.print(f"[red]Choice out of range. Please enter a number between 1 and {num_options}.[/red]")
        except ValueError:
            console.print("[red]Invalid input. Please enter a valid integer.[/red]")

# --- Define smolagents tools ---

@tool
def search_profiles(name: str, company: str = "") -> str:
    """
    Searches for LinkedIn profiles by candidate name and optionally company.

    Args:
        name: The name of the candidate to search for.
        company: Optional; the company where the candidate works.

    Returns:
        A JSON string representing the selected profile.
    """
    # Run the asynchronous search synchronously
    profiles_response = asyncio.run(async_search_profiles(name=name, company=company))
    profiles = parse_profiles_response(profiles_response)

    if not isinstance(profiles, list):
        return str(profiles)

    if not profiles:
        return "No profiles found."
    elif len(profiles) == 1:
        selected_profile = profiles[0]
    else:
        # Display the profiles in a styled Rich table
        table = Table(title="Multiple profiles found. Please select one:")
        table.add_column("Index", style="cyan", justify="right")
        table.add_column("Name", style="magenta")
        table.add_column("Headline", style="green")
        table.add_column("URL", style="blue", overflow="fold")
        for idx, profile in enumerate(profiles):
            name_field = profile.get("fullName", "Unknown")
            headline = profile.get("headline", "No headline")
            url = profile.get("profileURL", "No URL")
            table.add_row(str(idx + 1), name_field, headline, url)
        console.print(table)
        selected_index = get_user_choice(len(profiles))
        selected_profile = profiles[selected_index]

    return json.dumps(selected_profile, indent=2)

@tool
def get_profile(url: str) -> str:
    """
    Retrieves detailed LinkedIn profile information for the provided URL.
    Returns the profile information as a string.

    Args:
        url: str
            The URL of the LinkedIn profile to retrieve information for.
    """
    profile_info = asyncio.run(linkedin.get_linkedin_profile_info(url))
    return str(profile_info)

# --- Set up the smolagents CodeAgent ---

# Here we use an HF Inference API model (you can substitute with any supported model)
model = LiteLLMModel(model_id="gpt-4o-mini", temperature=0)

agent = CodeAgent(
    tools=[search_profiles, get_profile],
    model=model,
    add_base_tools=True,  # optionally adds standard tools provided by smolagents
    # verbose=True  # enables detailed logging of steps
)

def main() -> None:
    """
    Runs the people research agent using smolagents.
    """
    user_input = "Find LinkedIn profiles for a software engineer named Scott Persinger who works at Tatari."
    logger.info("Agent received input: %s", user_input)
    try:
        result = agent.run(user_input)
        logger.info("Agent Final Response:\n%s", result)
    except Exception as e:
        logger.exception("An error occurred while running the agent: %s", e)

if __name__ == "__main__":
    main()

import asyncio
import json
import logging
from typing import Any, List, Union

from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType, Tool
from tools import LinkedinDataTool  # Your custom LinkedIn tool

# Import Rich components
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a Rich console instance for styled output
console = Console()

# Instantiate your custom LinkedIn tool
linkedin = LinkedinDataTool()


async def async_search_profiles(name: str, company: str = "") -> Any:
    """
    Asynchronously search for LinkedIn profiles by name and company.

    Returns:
        The raw response from the LinkedIn tool.
    """
    return await linkedin.linkedin_people_search(name=name, company=company)


def parse_profiles_response(response: Any) -> Union[List[dict], str]:
    """
    Parse the profiles response into a list of dictionaries if possible.
    If the response is not a list, return it as is.

    Args:
        response: The raw response from the LinkedIn tool, which might be a JSON string or list.

    Returns:
        A list of profile dictionaries or an error message string.
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
    Prompt the user to select an option using Rich until a valid choice is made.

    Args:
        num_options: The number of available options.

    Returns:
        The selected option as a 0-based index.
    """
    while True:
        choice = Prompt.ask(f"Enter a number between 1 and {num_options}")
        try:
            value = int(choice)
            if 1 <= value <= num_options:
                return value - 1  # Convert to 0-based index.
            else:
                console.print(
                    f"[red]Choice out of range. Please enter a number between 1 and {num_options}.[/red]"
                )
        except ValueError:
            console.print("[red]Invalid input. Please enter a valid integer.[/red]")


def search_profiles(name: str, company: str = "") -> str:
    """
    Synchronously search for LinkedIn profiles by name and company.

    If multiple profiles are returned, prompt the user to select one.

    Args:
        name: The candidate's name.
        company: (Optional) The candidate's company.

    Returns:
        A JSON string representing the selected profile or an error message.
    """
    # Run the asynchronous LinkedIn people search.
    profiles_response = asyncio.run(async_search_profiles(name=name, company=company))
    profiles = parse_profiles_response(profiles_response)

    # If the result is not a list, return it directly.
    if not isinstance(profiles, list):
        return str(profiles)

    if not profiles:
        return "No profiles found."
    elif len(profiles) == 1:
        selected_profile = profiles[0]
    else:
        # Display the profiles using a styled Rich table.
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

    # Return the selected profile as a pretty-printed JSON string.
    return json.dumps(selected_profile, indent=2)


async def async_get_profile(url: str) -> Any:
    """
    Asynchronously retrieve detailed information for a LinkedIn profile given its URL.

    Args:
        url: The URL of the LinkedIn profile.

    Returns:
        The detailed profile information.
    """
    return await linkedin.get_linkedin_profile_info(url)


def get_profile(url: str) -> str:
    """
    Synchronously retrieve detailed information for a LinkedIn profile.

    Args:
        url: The URL of the LinkedIn profile.

    Returns:
        The profile information as a string.
    """
    profile_info = asyncio.run(async_get_profile(url))
    return str(profile_info)


# -----------------------------------------------------------------------------
# Wrap these functions as LangChain Tools
# -----------------------------------------------------------------------------

search_profiles_tool = Tool(
    name="search_profiles",
    func=search_profiles,
    description="Search for LinkedIn profiles by providing a candidate's name and optionally a company."
)

get_profile_tool = Tool(
    name="get_profile",
    func=get_profile,
    description="Retrieve detailed information for a LinkedIn profile using its URL."
)

tools = [search_profiles_tool, get_profile_tool]

# -----------------------------------------------------------------------------
# Set up the Chat Model and Agent
# -----------------------------------------------------------------------------

llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True  # Enable verbose mode to see internal reasoning and tool calls
)


def main() -> None:
    """
    Run the people research loop using the LangChain agent.
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

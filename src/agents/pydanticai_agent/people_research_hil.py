import asyncio
import json
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from tools import LinkedinDataTool  # Your custom LinkedIn tool
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

# Set up the LinkedIn API tool and Rich console.
linkedin = LinkedinDataTool()
console = Console()

# Define our data models.
class LinkedInProfile(BaseModel):
    name: str
    headline: str = "No headline"
    url: str

    @classmethod
    def from_api(cls, data: dict) -> "LinkedInProfile":
        """
        Converts a raw API response dict into a LinkedInProfile.
        - Uses "fullName" (or "name" if missing) for the candidate's display name.
        - Uses "headline" if provided, defaulting to "No headline".
        - Attempts to extract a URL from several keys, falling back to a computed URL.
        """
        display_name = data.get("fullName") or data.get("name")
        if not display_name:
            raise ValueError("No candidate name found.")
        headline = data.get("headline", "No headline")

        # Try several keys to find the profile URL.
        url = data.get("url") or data.get("publicProfileUrl") or data.get("profileURL")
        if not url:
            public_id = data.get("name", "unknown")
            url = f"https://www.linkedin.com/in/{public_id}"
        return cls(name=display_name, headline=headline, url=url)

class SearchProfilesInput(BaseModel):
    name: str
    company: str = ""

class SearchProfilesOutput(BaseModel):
    profile: LinkedInProfile

class GetProfileInput(BaseModel):
    url: str

class GetProfileOutput(BaseModel):
    details: str

# Instantiate the agent.
agent = Agent("openai:gpt-4o")

@agent.tool
def search_profiles_tool(ctx: RunContext, payload: SearchProfilesInput) -> SearchProfilesOutput:
    res = asyncio.run(linkedin.linkedin_people_search(name=payload.name, company=payload.company))
    if isinstance(res, list):
        profiles = res
    elif isinstance(res, str):
        try:
            profiles = json.loads(res)
        except json.JSONDecodeError:
            profiles = []
    else:
        profiles = []

    if not profiles:
        raise ValueError("No profiles found.")

    if len(profiles) > 1:
        table = Table(title="Select a Profile")
        table.add_column("Number", justify="right", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Headline", style="green")
        table.add_column("URL", style="yellow")
        for i, p in enumerate(profiles):
            try:
                lp = LinkedInProfile.from_api(p)
                table.add_row(str(i+1), lp.name, lp.headline, lp.url)
            except Exception as e:
                table.add_row(str(i+1), "Invalid", str(e), "")
        console.print(table)
        choices = [str(i+1) for i in range(len(profiles))]
        selected_number = Prompt.ask("Enter the number of the profile to select", choices=choices)
        selected_profile = profiles[int(selected_number) - 1]
    else:
        selected_profile = profiles[0]

    return SearchProfilesOutput(profile=LinkedInProfile.from_api(selected_profile))

@agent.tool
def get_profile_tool(ctx: RunContext, payload: GetProfileInput) -> GetProfileOutput:
    details = asyncio.run(linkedin.get_linkedin_profile_info(payload.url))
    return GetProfileOutput(details=details)

if __name__ == "__main__":
    user_input = "Find LinkedIn profiles for a software engineer named Scott Persinger."
    result = agent.run_sync(user_input)
    console.print("\nAgent Final Response:", style="bold green")
    console.print(result.data)

import asyncio
import json
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from tools import LinkedinDataTool

# Set up the LinkedIn API tool.
linkedin = LinkedinDataTool()

# Define our data models.
class LinkedInProfile(BaseModel):
    name: str
    headline: str = "No headline"
    url: str

    @classmethod
    def from_api(cls, data: dict) -> "LinkedInProfile":
        display_name = data.get("fullName") or data.get("name")
        if not display_name:
            raise ValueError("No candidate name found.")
        headline = data.get("headline", "No headline")
        public_id = data.get("name", "unknown")
        url = data.get("url", f"https://www.linkedin.com/in/{public_id}")
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

    if len(profiles) == 1:
        selected = profiles[0]
    else:
        print("Multiple profiles found:")
        for i, p in enumerate(profiles):
            try:
                lp = LinkedInProfile.from_api(p)
                print(f"{i+1}. {lp.name} - {lp.headline} - {lp.url}")
            except Exception as e:
                print(f"{i+1}. Invalid profile: {p} ({e})")
        while True:
            try:
                choice = int(input("Select profile number: "))
                if 1 <= choice <= len(profiles):
                    selected = profiles[choice - 1]
                    break
            except ValueError:
                pass

    return SearchProfilesOutput(profile=LinkedInProfile.from_api(selected))

@agent.tool
def get_profile_tool(ctx: RunContext, payload: GetProfileInput) -> GetProfileOutput:
    details = asyncio.run(linkedin.get_linkedin_profile_info(payload.url))
    return GetProfileOutput(details=details)

if __name__ == "__main__":
    result = agent.run_sync("Find LinkedIn profiles for a software engineer named Scott Persinger.")
    print("\nAgent Final Response:")
    print(result.data)

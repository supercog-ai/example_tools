import asyncio
import json
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from tools import LinkedinDataTool  # Your custom LinkedIn tool

# -----------------------------------------------------------------------------
# 1. Set up your LinkedIn API tool
# -----------------------------------------------------------------------------
linkedin = LinkedinDataTool()

# -----------------------------------------------------------------------------
# 2. Define Pydantic models for tool inputs and outputs
# -----------------------------------------------------------------------------

class LinkedInProfile(BaseModel):
    # Our internal representation requires these fields.
    # We expect the API to return 'fullName' for the candidate’s display name
    # and (if available) 'name' as the public identifier.
    name: str
    headline: str = "No headline"
    url: str

    @classmethod
    def from_api(cls, data: dict) -> "LinkedInProfile":
        """
        Factory method to convert a raw API response dict into a LinkedInProfile.
        - Uses "fullName" if available for the display name; otherwise falls back to "name".
        - Computes a URL if one is not provided, assuming the public identifier is in "name".
        """
        display_name = data.get("fullName") or data.get("name")
        if not display_name:
            raise ValueError("No candidate name found in API response.")
        # Get the headline if provided; otherwise default.
        headline = data.get("headline", "No headline")
        # If a URL isn’t provided, assume we can compute one using the public identifier.
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

# -----------------------------------------------------------------------------
# 3. Instantiate a PydanticAI Agent and register tools
# -----------------------------------------------------------------------------

# Create an agent using your chosen model identifier.
agent = Agent("openai:gpt-4o-mini")

@agent.tool
def search_profiles_tool(ctx: RunContext, input: SearchProfilesInput) -> SearchProfilesOutput:
    """
    Search for LinkedIn profiles by name and company.
    If multiple profiles are returned, prompt the human to select one.
    """
    profiles_response = asyncio.run(
        linkedin.linkedin_people_search(name=input.name, company=input.company)
    )
    # Convert the API response to a list.
    if isinstance(profiles_response, list):
        profiles = profiles_response
    elif isinstance(profiles_response, str):
        try:
            profiles = json.loads(profiles_response)
        except json.JSONDecodeError:
            profiles = []
    else:
        profiles = []

    if not profiles:
        raise ValueError("No profiles found.")

    # Human in the loop: if multiple profiles are found, prompt the user.
    if len(profiles) == 1:
        selected_profile = profiles[0]
    else:
        print("Multiple profiles found:")
        for i, profile in enumerate(profiles):
            try:
                # Use our factory method to parse the profile.
                parsed = LinkedInProfile.from_api(profile)
                print(f"{i+1}. {parsed.name} - {parsed.headline} - {parsed.url}")
            except Exception as e:
                print(f"{i+1}. Invalid profile data: {profile} ({e})")
        while True:
            try:
                choice = int(input("Enter the number of the profile to select: "))
                if 1 <= choice <= len(profiles):
                    selected_profile = profiles[choice - 1]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(profiles)}.")
            except ValueError:
                print("Invalid input. Please enter a valid integer.")

    # Convert the selected profile into our internal model.
    profile_model = LinkedInProfile.from_api(selected_profile)
    return SearchProfilesOutput(profile=profile_model)

@agent.tool
def get_profile_tool(ctx: RunContext, input: GetProfileInput) -> GetProfileOutput:
    """
    Retrieve detailed information for a LinkedIn profile given its URL.
    """
    details = asyncio.run(linkedin.get_linkedin_profile_info(input.url))
    return GetProfileOutput(details=details)

# -----------------------------------------------------------------------------
# 4. Run the agent with a user input
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    user_input = "Find LinkedIn profiles for a software engineer named Scott Persinger who works at Supercog AI."
    result = agent.run_sync(user_input)
    print("\nAgent Final Response:")
    print(result.data)

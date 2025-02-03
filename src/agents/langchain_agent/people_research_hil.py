import asyncio
import json
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType, Tool
from tools import LinkedinDataTool  # Your custom LinkedIn tool

linkedin = LinkedinDataTool()

def search_profiles(name: str, company: str = "") -> str:
    """
    Search for LinkedIn profiles by name and company.

    If multiple profiles are returned (as a list), prompt the human
    to select one. If only one profile is found, return it.
    """
    # Run the asynchronous LinkedIn people search
    profiles_response = asyncio.run(linkedin.linkedin_people_search(name=name, company=company))

    # Determine if the response is already a list or needs parsing
    if isinstance(profiles_response, list):
        profiles = profiles_response
    elif isinstance(profiles_response, str):
        try:
            profiles = json.loads(profiles_response)
        except json.JSONDecodeError:
            # If the string is not valid JSON, use it as is.
            profiles = profiles_response
    else:
        # Fallback in case the type is unexpected
        profiles = profiles_response

    # Handle the case where profiles is not a list (e.g., a string message)
    if not isinstance(profiles, list):
        return profiles

    # If the result is a list, check the number of profiles
    if len(profiles) == 0:
        return "No profiles found."
    elif len(profiles) == 1:
        selected_profile = profiles[0]
    else:
        # Multiple profiles found: print them out and ask the human to choose.
        print("Multiple profiles found:")
        for i, profile in enumerate(profiles):
            name_field = profile.get("name", "Unknown")
            headline = profile.get("headline", "No headline")
            url = profile.get("url", "No URL")
            print(f"{i+1}. {name_field} - {headline} - {url}")

        # Prompt until a valid choice is made.
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

    # Return the selected profile as a JSON string (or adjust as needed)
    return json.dumps(selected_profile)

def get_profile(url: str) -> str:
    """
    Retrieve detailed information for a LinkedIn profile given its URL.
    """
    return asyncio.run(linkedin.get_linkedin_profile_info(url))

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

# -----------------------------------------------------------------------------
# Run the People Research Loop
# -----------------------------------------------------------------------------

user_input = "Find LinkedIn profiles for a software engineer named Scott Persinger who works at Tatari."

result = agent.run(user_input)

print("\nAgent Final Response:")
print(result)

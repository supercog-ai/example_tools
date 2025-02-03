import asyncio
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType, Tool
from tools import LinkedinDataTool  # Your custom LinkedIn tool

# -----------------------------------------------------------------------------
# 1. Define the underlying functions that wrap your LinkedIn API calls
# -----------------------------------------------------------------------------

linkedin = LinkedinDataTool()

def search_profiles(name: str, company: str = "") -> str:
    """Search for LinkedIn profiles by name and company.

    If the company is not provided, an empty string is used.
    """
    return asyncio.run(linkedin.linkedin_people_search(name=name, company=company))

def get_profile(url: str) -> str:
    """Retrieve detailed information for a LinkedIn profile given its URL."""
    return asyncio.run(linkedin.get_linkedin_profile_info(url))

# -----------------------------------------------------------------------------
# 2. Wrap these functions as LangChain Tools
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
# 3. Set up the Chat Model and Agent
# -----------------------------------------------------------------------------

llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True  # Enable verbose mode to see internal reasoning and tool calls
)

# -----------------------------------------------------------------------------
# 4. Run the People Research Loop
# -----------------------------------------------------------------------------

user_input = "Find LinkedIn profiles for a software engineer named Scott Persinger at Supercog AI."

result = agent.run(user_input)

print("\nAgent Final Response:")
print(result)

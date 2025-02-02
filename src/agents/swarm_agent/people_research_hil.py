from swarm import Swarm, Agent
from tools import LinkedinDataTool
import asyncio
from typing import Callable, Any


client = Swarm()

def invoke_async(async_func: Callable, *args, **kwargs) -> Any:
    return asyncio.run(async_func(*args, **kwargs))

linkedin = LinkedinDataTool()
def search_profiles(name: str, company: str):
    return invoke_async(linkedin.linkedin_people_search, name=name, company=company)

def get_profile(url: str):
    return invoke_async(linkedin.get_linkedin_profile_info, url)

def call_report_agent():
    return person_reporter

def seek_clarfication():
    user_input = input("Choose the profile: ")
    return user_input

person_reporter = Agent(
    name="Person Report Writer",
    instructions="""
You will receive the URL to a linkedin profile. Retrive the profile and
write a background report on the person, focusing on their career progression
and current role.
""",
    functions=[get_profile],
)


orchestrator = Agent(
    name="Person Researcher",
    instructions="""
You do research on people. Given a name and a company:
1. Search for matching profiles on linkedin.
2. If you find a single strong match, then prepare a background report on that person.
3. If you find multiple matches, then ask stop and ask the user for clarification. Then go back to step 1.
If you are missing info, then seek clarification from the user.
""",
    functions=[search_profiles, call_report_agent, seek_clarfication],
)

response = client.run(
    agent=orchestrator,
    messages=[{"role": "user", "content": "Scott Persinger at tatari"}],
    debug=True,
)

print(response.messages[-1]["content"])

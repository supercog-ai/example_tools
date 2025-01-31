from swarm import Swarm, Agent
from tools import GoogleNewsTool

client = Swarm()

gnt = GoogleNewsTool()
def query_news(topic: str):
    return gnt.query_news(topic)

def call_news_reporter():
    return news_reporter

producer = Agent(
    name="News Producer",
    instructions="You are a news producer. Call the reporter with the indicated topic.",
    functions=[call_news_reporter],
)

news_reporter = Agent(
    name="News Reporter",
    instructions="""
You are a hard news reporter.
Call Google News to get headlines on the indicated news topic.
Then write an NPR-style news report based on the hedalines.
""",
    functions=[query_news],
)

response = client.run(
    agent=producer,
    messages=[{"role": "user", "content": "Get the news about World Finance"}],
)

print(response.messages[-1]["content"])

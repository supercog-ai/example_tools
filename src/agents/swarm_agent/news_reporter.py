from swarm import Swarm, Agent
from tools import GoogleNewsTool

client = Swarm()

gnt = GoogleNewsTool()
def query_news(topic: str):
    return "There is only good news today about the world of finance."
    return gnt.query_news(topic)

def call_news_reporter():
    return news_reporter

producer = Agent(
    name="News Producer",
    instructions="You are a news producer. Call the reporter with the indicated topic.",
    functions=[call_news_reporter],
    model="gpt-4o-mini",
)

news_reporter = Agent(
    name="News Reporter",
    instructions="""
You are a hard news reporter.
Call Google News to get headlines on the indicated news topic.
Then write an NPR-style news report based on the headlines.
""",
    functions=[query_news],
    model="gpt-4o-mini",
)

for chunk in client.run(
    agent=producer,
    messages=[{"role": "user", "content": "Get the news about World Finance"}],
    debug=True,
    stream=True,
):
    print(chunk)

#print(response.messages[-1]["content"])

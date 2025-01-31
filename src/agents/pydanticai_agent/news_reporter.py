# From https://ai.pydantic.dev/multi-agent-applications/#agent-delegation

from pydantic_ai import Agent, RunContext
from pydantic_ai.usage import UsageLimits

from tools import GoogleNewsTool

# Create the agents.

producer = Agent(
    "gpt-4o-mini",
    system_prompt=(
        "You are a news producer. Call the reporter with the indicated topic."
    ),
)
news_reporter = Agent(
    "gpt-4o",
    system_prompt=(
        "You are a hard news reporter."
        "Call Google News to get headlines on the indicated news topic."
        "Then, respond with an NPR-style news report based on the headlines given."
    ),
    result_type=list[str],
)


@producer.tool
async def call_news_reporter(ctx: RunContext[None], topic: str) -> list[str]:
    """Call the news reporter to get the news about the given topic."""

    r = await news_reporter.run(topic)
    return r.data


@news_reporter.tool
async def get_google_news_headlines(ctx: RunContext[None], topic: str) -> list[str]:
    """Get the news about the given topic from Google News."""

    gnt = GoogleNewsTool()
    return str(gnt.query_news(topic))


result = producer.run_sync(
    "Get the news about World Finance",
)
print(result.data)

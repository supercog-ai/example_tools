import logging
from smolagents import CodeAgent, LiteLLMModel, tool
from tools import GoogleNewsTool  # Your custom tool to query Google News

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------------------------------
# 1. Set Up the Reporter Agent
# ----------------------------------------

# Instantiate your GoogleNewsTool
gnt = GoogleNewsTool()

@tool
def query_news(topic: str) -> str:
    """
    Query Google News to get headlines on the indicated news topic.

    Args:
        topic: The news topic to query.

    Returns:
        The headlines returned by Google News as a string.
    """
    return str(gnt.query_news(topic))

# Initialize the reporter agent with the query_news tool.
# This agent is expected to generate an NPR-style report when given a proper prompt.
reporter_model = LiteLLMModel(model_id="gpt-4o-mini", temperature=0)
reporter_agent = CodeAgent(
    tools=[query_news],
    model=reporter_model,
    add_base_tools=True,  # optionally include smolagents base tools
    # verbose=True,
)

def call_news_reporter(topic: str) -> str:
    """
    Calls the reporter agent with a prompt instructing it to generate an NPR-style report
    on the given topic.

    Args:
        topic: The news topic.

    Returns:
        The generated news report.
    """
    reporter_prompt = (
        f"You are a hard news reporter. Your task is to generate an NPR-style news report on the topic: {topic}. "
        "Use the query_news tool to retrieve relevant headlines."
    )
    return reporter_agent.run(reporter_prompt)

# ----------------------------------------
# 2. Set Up the Producer Agent
# ----------------------------------------

@tool
def reporter_tool(topic: str) -> str:
    """
    Calls the news reporter agent with the indicated topic to generate a news report.

    Args:
        topic: The topic for which to generate the news report.

    Returns:
        The generated news report.
    """
    return call_news_reporter(topic)

# Initialize the producer agent with the reporter_tool.
# This agent takes a high-level instruction (e.g., "Get the news about World Finance")
# and uses the reporter_tool to obtain the final report.
producer_model = LiteLLMModel(model_id="gpt-4o-mini", temperature=0)
producer_agent = CodeAgent(
    tools=[reporter_tool],
    model=producer_model,
    add_base_tools=True,
    # verbose=True,
)

# ----------------------------------------
# 3. Run the Multi-Agent Workflow
# ----------------------------------------

def main() -> None:
    user_input = "Get the news about World Finance"
    logger.info("Producer Agent received input: %s", user_input)
    result = producer_agent.run(user_input)
    print("Final Output from Producer Agent:")
    print(result)

if __name__ == "__main__":
    main()

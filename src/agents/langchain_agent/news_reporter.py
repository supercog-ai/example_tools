from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool

from tools import GoogleNewsTool
# ----------------------------------------
# 1. Set Up the Reporter Agent
# ----------------------------------------

gnt = GoogleNewsTool()

# This function simulates a call to a news API (e.g., Google News)
def query_news(topic: str) -> str:
    # In a real implementation, you would call an external API here.
    # For demonstration, we return a simulated headline string.
    return str(gnt.query_news(topic))

# Wrap query_news as a LangChain tool.
news_tool = Tool(
    name="query_news",
    func=query_news,
    description="Call Google News to get headlines on the indicated news topic."
)

# Create a chat-based LLM that uses OpenAI’s new ChatCompletion interface.
news_llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

# Initialize the reporter agent.
# This agent is instructed (via its prompt behavior) to generate an NPR-style report.
news_agent = initialize_agent(
    tools=[news_tool],
    llm=news_llm,
    agent="zero-shot-react-description",  # Use a common agent style
    verbose=True,
)

# Helper function that calls the reporter agent with a topic.
def call_news_reporter(topic: str) -> str:
    reporter_prompt = (
        f"You are a hard news reporter. Your task is to generate an NPR-style news report on the topic: {topic}. "
        "Use the query_news tool to retrieve relevant headlines."
    )
    return news_agent.run(reporter_prompt)

# ----------------------------------------
# 2. Set Up the Producer Agent
# ----------------------------------------

# Wrap the reporter-calling function as a tool for the producer agent.
reporter_tool = Tool(
    name="call_news_reporter",
    func=call_news_reporter,
    description="Call the news reporter agent with the indicated topic to generate a news report."
)

# Create a chat-based LLM for the producer.
producer_llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

# Initialize the producer agent.
# This agent takes the user input (e.g., "Get the news about World Finance")
# and uses the reporter tool to get a final report.
producer_agent = initialize_agent(
    tools=[reporter_tool],
    llm=producer_llm,
    agent="zero-shot-react-description",
    verbose=True,
)

# ----------------------------------------
# 3. Run the Multi-Agent Workflow
# ----------------------------------------

if __name__ == "__main__":
    user_input = "Get the news about World Finance"
    result = producer_agent.run(user_input)
    print("Final Output from Producer Agent:")
    print(result)

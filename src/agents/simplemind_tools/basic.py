# NOTE: Simplemind does not yet have an agent system,
# so this is a simple example of a tool that uses the
# GoogleNewsTool to get news on a topic.

import simplemind as sm
from pydantic import Field

from tools import GoogleNewsTool


def get_google_news_topic(topic: str = Field(description="The topic to focus on.")):
    gnt = GoogleNewsTool()
    return str(gnt.query_news(topic))

# Create the conversation.
conversation = sm.create_conversation()
conversation.add_message("user", "What's the news in World Finance? Give us an NPR–style news report based on the headlines.")

response = conversation.send(tools=[get_google_news_topic])
print(response.text)

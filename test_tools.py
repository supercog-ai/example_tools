import asyncio
import pytest
from typing import Any
import pandas as pd

from tools import GoogleNewsTool, LinkedinDataTool


@pytest.mark.asyncio
async def test_linkedin_people_search() -> None:
    """Test LinkedIn people search functionality.

    Tests the basic search functionality without company filter.
    """
    linkedin = LinkedinDataTool()
    result = await linkedin.linkedin_people_search("Scott Persinger")

    assert result is not None
    assert isinstance(result, (dict, list))


@pytest.mark.asyncio
async def test_linkedin_people_search_with_company() -> None:
    """Test LinkedIn people search with company filter."""


    linkedin = LinkedinDataTool()
    result = await linkedin.linkedin_people_search(
        "Scott Persinger",
        # company="Supercog"
    )

    assert result is not None
    assert isinstance(result, (dict, list))


def test_google_news_headlines() -> None:
    """Test Google News top headlines retrieval."""

    news_tool = GoogleNewsTool()
    headlines = news_tool.get_top_headlines()

    assert headlines is not None
    assert isinstance(headlines, pd.DataFrame)
    assert not headlines.empty
    assert 'title' in headlines.columns
    assert 'source' in headlines.columns


if __name__ == "__main__":
    # For manual testing/debugging
    asyncio.run(test_linkedin_people_search())
    asyncio.run(test_linkedin_people_search_with_company())
    print("LinkedIn tests completed")

    test_google_news_headlines()
    print("Google News test completed")

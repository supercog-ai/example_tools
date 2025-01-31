import asyncio

from examples.tools import GoogleNewsTool, LinkedinDataTool



async def test_linkedin():
    linkedin = LinkedinDataTool()
    res = await linkedin.linkedin_people_search(
        "Scott Persinger",
        #company = "Supercog",
    )
    print(res)


def main():
    result = asyncio.run(test_linkedin())
    print(result)

    print(GoogleNewsTool().get_top_headlines())

if __name__ == "__main__":
    main()

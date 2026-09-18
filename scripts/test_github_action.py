import asyncio

from app.tools.github import GitHubTool


async def main() -> None:
    github = GitHubTool()

    try:
        result = await github.create_issue(
            title="[TEST] AI-SRE Incident Agent",
            body=(
                "This is a test issue created by the "
                "AI-SRE Incident Triage Agent."
            ),
            labels=["incident"],
        )

        print("\n========== GITHUB RESULT ==========")
        print(result)

    finally:
        await github.close()


if __name__ == "__main__":
    asyncio.run(main())
from app.tools.github import github_tool
import time
import asyncio  

async def main():
    print("Testing GitHub tool...\n")

    print("=== Recent Commits ===")

    commits = await github_tool.get_recent_commits(limit=5)

    for commit in commits:
        print(
            f"{commit['sha'][:7]} | "
            f"{commit['date']} | "
            f"{commit['message'].splitlines()[0]}"
        )

    print("\n=== Issue Search ===")

    issues = await github_tool.search_issues(
        "incident",
        limit=5,
    )

    for issue in issues:
        print(
            f"#{issue['number']} | "
            f"{issue['state']} | "
            f"{issue['title']}"
        )

    await github_tool.close()

if __name__ == "__main__":
    x = time.perf_counter()
    asyncio.run(main())
    elapsed = time.perf_counter() - x
    print(f"\nPrometheus tool test completed in {elapsed:.3f} seconds.")
    
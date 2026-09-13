from app.tools.github import github_tool


def main():
    print("Testing GitHub tool...\n")

    print("=== Recent Commits ===")

    commits = github_tool.get_recent_commits(limit=5)

    for commit in commits:
        print(
            f"{commit['sha'][:7]} | "
            f"{commit['date']} | "
            f"{commit['message'].splitlines()[0]}"
        )

    print("\n=== Issue Search ===")

    issues = github_tool.search_issues(
        "incident",
        limit=5,
    )

    for issue in issues:
        print(
            f"#{issue['number']} | "
            f"{issue['state']} | "
            f"{issue['title']}"
        )


if __name__ == "__main__":
    main()
from app.tools.github import github_tool


def test_get_recent_commits():
    commits = github_tool.get_recent_commits(limit=5)

    assert isinstance(commits, list)

    if commits:
        assert "sha" in commits[0]
        assert "message" in commits[0]
        assert "date" in commits[0]


def test_search_issues():
    issues = github_tool.search_issues(
        "incident",
        limit=5,
    )

    assert isinstance(issues, list)


def test_get_issue():
    issues = github_tool.search_issues(
        "incident",
        limit=1,
    )

    if issues:
        issue = github_tool.get_issue(
            issues[0]["number"]
        )

        assert issue["number"] == issues[0]["number"]
        assert "title" in issue
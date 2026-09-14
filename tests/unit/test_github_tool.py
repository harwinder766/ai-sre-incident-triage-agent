import pytest

from app.tools.github import GitHubTool


@pytest.mark.asyncio
async def test_get_recent_commits():

    tool = GitHubTool()

    commits = await tool.get_recent_commits(
        limit=5
    )

    assert isinstance(commits, list)

    if commits:
        assert "sha" in commits[0]
        assert "message" in commits[0]
        assert "date" in commits[0]

    await tool.close()


@pytest.mark.asyncio
async def test_search_issues():

    tool = GitHubTool()

    issues = await tool.search_issues(
        "incident",
        limit=5,
    )

    assert isinstance(issues, list)

    await tool.close()


@pytest.mark.asyncio
async def test_get_issue():

    tool = GitHubTool()

    issues = await tool.search_issues(
        "incident",
        limit=1,
    )

    if issues:
        issue = await tool.get_issue(
            issues[0]["number"]
        )

        assert issue["number"] == issues[0]["number"]
        assert "title" in issue
        assert "body" in issue

    await tool.close()
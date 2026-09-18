import asyncio

from app.tools.slack import SlackTool


async def main() -> None:
    slack = SlackTool()

    try:
        result = await slack.send_message(
            "🤖 AI-SRE Incident Triage Agent test message."
        )

        print("\n========== SLACK RESULT ==========")
        print(result)

    finally:
        await slack.close()


if __name__ == "__main__":
    asyncio.run(main())
import pytest


@pytest.mark.asyncio
async def test_create_account() -> None:
    from src.lib import TmailClient

    client = TmailClient()
    await client.create_account()


@pytest.mark.asyncio
async def test_get_emails() -> None:
    import os
    from asyncio import sleep
    from pathlib import Path
    from smtplib import SMTP
    from time import time_ns
    from uuid import uuid4

    from src.lib import TmailClient

    path = Path(__file__).parents[1] / ".env"
    if path.is_file():
        from dotenv import load_dotenv

        load_dotenv(path)

    smtp_username = os.environ.get("SMTP_USERNAME")
    assert smtp_username, "SMTP_USERNAME environment variable is not set"
    smtp_password = os.environ.get("SMTP_PASSWORD")
    assert smtp_password, "SMTP_PASSWORD environment variable is not set"
    smtp_host = os.environ.get("SMTP_HOST")
    assert smtp_host, "SMTP_HOST environment variable is not set"
    smtp_port = int(os.environ.get("SMTP_PORT", 0))
    assert smtp_port, "SMTP_PORT environment variable is not set"
    smtp_sender = os.environ.get("SMTP_SENDER")
    assert smtp_sender, "SMTP_SENDER environment variable is not set"

    client = TmailClient()
    await client.create_account()
    assert await anext(client.get_emails(), None) is None, "Expected no emails to be returned initially"

    email_body = f"{uuid4()}__{time_ns()}"
    with SMTP(host=smtp_host, port=smtp_port) as smtp:
        smtp.starttls()
        smtp.login(smtp_username, smtp_password)
        smtp.sendmail(
            from_addr=smtp_sender,
            to_addrs=[client.email],
            msg=f"Subject: Test Email\n\n{email_body}",
        )

    while True:
        email = await anext(client.get_emails(), None)
        if email is not None:
            assert email_body in email.body, "Email body does not match the sent email"
            break
        await sleep(1)

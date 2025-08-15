import logging

from pydash import get

from src.models import TmailEmail


class TmailClient:
    from collections.abc import AsyncGenerator
    from re import compile

    base_url = "https://tmail.link"
    email_link_pattern = compile(r"/inbox/.+")
    email_address_pattern = compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    index_link: str | None = None

    @property
    def logger(self) -> logging.Logger:
        return logging.getLogger(__name__)

    @property
    def email(self) -> str:
        assert self.index_link, "Index link is not set. Call create_account() first."
        matches = self.email_address_pattern.search(self.index_link)
        assert matches, f"Cannot find email address in index link: {self.index_link}"
        email = matches.group(0)
        assert email, f"Email address is empty in index link: {self.index_link}"
        return email

    def __init__(self) -> None:
        from curl_cffi import AsyncSession

        self.session = AsyncSession()

    async def create_account(self) -> None:
        from bs4 import BeautifulSoup, Tag

        response = await self.session.get(f"{self.base_url}/")
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("a", href=self.email_link_pattern)
        assert element, f"Cannot find inbox link element in html. HTML: {html}"
        assert isinstance(element, Tag), f"Expected element to be a Tag, got {type(element)}. HTML: {html}"
        inbox_link = element.get("href")
        assert isinstance(inbox_link, str), f"Expected inbox link to be a string, got {type(inbox_link)}. HTML: {html}"
        inbox_link = inbox_link.strip()
        assert inbox_link, f"Inbox link is empty. HTML: {html}"
        if not inbox_link.startswith("/"):
            inbox_link = f"/{inbox_link}"
        if not inbox_link.endswith("/"):
            inbox_link += "/"
        self.index_link = inbox_link
        assert self.email

    async def get_emails(self) -> AsyncGenerator[TmailEmail]:
        assert self.index_link, "Index link is not set. Call create_account() first."
        session = self.session

        url = f"{self.base_url}{self.index_link}"
        token = await self.__get_csrf_token()
        response = await session.post(
            url,
            data={
                "format": "json",
                "csrfmiddlewaretoken": token,
            },
            headers={
                "Accept": "application/json",
                "X-CSRFToken": token,
                "Referer": url,
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": self.base_url,
            },
        )
        response.raise_for_status()
        data = response.json()
        messages = get(data, "messages", [])
        for message in messages:
            try:
                id = message.get("key", "")
                assert id, "Email ID should not be empty"
                yield TmailEmail(
                    id=id,
                    date=message.get("created", ""),
                    body=await self.get_email_body(id),
                    html=None,
                    sender=message.get("sender", ""),
                    subject=message.get("subject", ""),
                )
            except Exception as e:
                print(f"Error processing email: {e}")
                continue

    async def get_email_body(self, email_id: str) -> str:
        from bs4 import BeautifulSoup

        assert self.session, "Session is not initialized. Call create_account() first."
        assert self.index_link, "Index link is not set. Call create_account() first."

        url = f"https://tmail.link{self.index_link}{email_id}/0"
        response = await self.session.get(url)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        body = soup.get_text()
        return body.strip()

    async def __get_csrf_token(self) -> str:
        assert self.index_link, "Index link is not set. Call create_account() first."
        session = self.session

        url = f"{self.base_url}{self.index_link}"
        response = await session.get(
            url,
            headers={
                "Accept": "application/json",
            },
        )
        response.raise_for_status()
        token = session.cookies.get("csrftoken", "")
        assert token, "CSRF token should not be empty"
        return token

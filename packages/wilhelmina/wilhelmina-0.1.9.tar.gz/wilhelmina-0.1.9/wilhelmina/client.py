"""Wilma API client."""

import datetime
import importlib.util
import logging
from typing import Any, Optional, Set
from urllib.parse import urlparse

import aiohttp
from aiohttp import ClientResponse
from bs4 import BeautifulSoup

from wilhelmina.models import Message

# Allow for running without Playwright
_has_playwright = importlib.util.find_spec("playwright") is not None
if _has_playwright:
    from playwright._impl._api_structures import SetCookieParam
    from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)


class WilmaError(Exception):
    """Base exception for Wilma API errors."""


class AuthenticationError(WilmaError):
    """Authentication error."""


class WilmaClient:
    """Client for Wilma API."""

    def __init__(
        self,
        base_url: str,
        session: Optional[aiohttp.ClientSession] = None,
        debug: bool = False,
        headless: bool = True,
    ) -> None:
        """Initialize the client."""
        self.base_url = base_url.rstrip("/")
        self.session = session
        self.user_id: Optional[str] = None
        self._sid: Optional[str] = None
        self.debug = debug
        self.headless = headless
        self._owns_session = session is None
        self.username: str | None = None
        self.password: str | None = None

        if debug:
            logger.setLevel(logging.DEBUG)

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Ensure that a session exists."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
            self._owns_session = True
        return self.session

    async def close(self) -> None:
        """Close the HTTP session if we created it."""
        if self._owns_session and self.session and not self.session.closed:
            await self.session.close()
            self.session = None

    async def __aenter__(self) -> "WilmaClient":
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    def _check_auth(self) -> None:
        """Check if authenticated and raise error if not."""
        if not self.user_id or not self._sid:
            logger.debug("Not authenticated")
            raise AuthenticationError("Not authenticated")

    async def login(self, username: str | None = None, password: str | None = None) -> None:
        """Login to Wilma."""
        self.username = username or self.username
        self.password = password or self.password

        if not self.username or not self.password:
            raise AuthenticationError("Username and password must be provided")

        session = await self._ensure_session()
        logger.debug("Logging in to %s as %s", self.base_url, self.username)

        # Get SESSIONID token
        async with session.get(f"{self.base_url}/token") as response:
            if response.status != 200:
                raise AuthenticationError(f"Failed to get token: {response.status}")

            login_id = response.cookies.get("Wilma2LoginID")
            if not login_id:
                raise AuthenticationError("No login ID cookie found")

            session_id = login_id.value
            logger.debug("Got session ID: %s", session_id)

        # Perform login
        data = {
            "Login": self.username,
            "Password": self.password,
            "SESSIONID": session_id,
        }

        async with session.post(
            f"{self.base_url}/login", data=data, allow_redirects=False
        ) as response:
            if response.status != 302 and response.status != 303:
                raise AuthenticationError(f"Login failed: {response.status}")

            sid = response.cookies.get("Wilma2SID")
            if not sid:
                raise AuthenticationError("No SID cookie found")

            self._sid = sid.value

            location = response.headers.get("Location")
            if not location:
                raise AuthenticationError("No Location header in response")

            # Handle checkcookie redirect - follow it to get the actual location
            if "checkcookie" in location and "!" not in location:
                logger.debug("Following checkcookie redirect: %s", location)

                # Use allow_redirects=False to see each redirect step
                async with session.get(location, allow_redirects=False) as redirect_response:
                    logger.debug("Checkcookie response status: %s", redirect_response.status)
                    if redirect_response.status in [302, 303, 301, 307, 308]:
                        new_location = redirect_response.headers.get("Location")
                        if new_location:
                            # If the new location still doesn't have !, try extracting from home page
                            if (
                                "!" not in new_location
                                and new_location.rstrip("/") == self.base_url
                            ):
                                logger.debug("Redirect to root, extracting user ID from home page")
                                async with session.get(self.base_url) as home_response:
                                    if home_response.status != 200:
                                        raise AuthenticationError(
                                            f"Failed to load home page: {home_response.status}"
                                        )

                                    home_content = await home_response.text()
                                    # Look for user ID in the page content - Wilma typically has it in URLs or JavaScript
                                    import re

                                    user_id_match = re.search(
                                        r'["\'/](![\w\d]+)["\'/]', home_content
                                    )
                                    if user_id_match:
                                        self.user_id = user_id_match.group(1)
                                        logger.debug(
                                            "Extracted user ID from home page: %s", self.user_id
                                        )
                                        return
                                    else:
                                        # Try looking for it in a different pattern
                                        user_id_match = re.search(
                                            r'user[Ii]d["\']?\s*[:=]\s*["\']?(![\w\d]+)',
                                            home_content,
                                        )
                                        if user_id_match:
                                            self.user_id = user_id_match.group(1)
                                            logger.debug(
                                                "Extracted user ID from home page (pattern 2): %s",
                                                self.user_id,
                                            )
                                            return
                                        else:
                                            raise AuthenticationError(
                                                "Could not extract user ID from home page after checkcookie redirect"
                                            )
                            else:
                                location = new_location
                                logger.debug("Got redirect location: %s", location)
                        else:
                            raise AuthenticationError("No Location header in checkcookie redirect")
                    else:
                        # Some instances redirects to root, need to extract user ID differently
                        logger.debug(
                            "No redirect from checkcookie, trying to find user ID from home page"
                        )
                        async with session.get(self.base_url) as home_response:
                            if home_response.status != 200:
                                raise AuthenticationError(
                                    f"Failed to load home page: {home_response.status}"
                                )

                            home_content = await home_response.text()
                            # Look for user ID in the page content - Wilma typically has it in URLs or JavaScript
                            import re

                            user_id_match = re.search(r'["\'/](![\w\d]+)["\'/]', home_content)
                            if user_id_match:
                                self.user_id = user_id_match.group(1)
                                logger.debug("Extracted user ID from home page: %s", self.user_id)
                                return
                            else:
                                # Try looking for it in a different pattern
                                user_id_match = re.search(
                                    r'user[Ii]d["\']?\s*[:=]\s*["\']?(![\w\d]+)', home_content
                                )
                                if user_id_match:
                                    self.user_id = user_id_match.group(1)
                                    logger.debug(
                                        "Extracted user ID from home page (pattern 2): %s",
                                        self.user_id,
                                    )
                                    return
                                else:
                                    raise AuthenticationError(
                                        "Could not extract user ID from home page after checkcookie redirect"
                                    )

            if "!" not in location:
                raise AuthenticationError(f"Invalid Location header: {location}")

            self.user_id = "!" + location.split("!")[1].split("?")[0]
            logger.debug("Logged in as %s", self.user_id)

    async def _get_unread_message_ids(self) -> Set[int]:
        """Get IDs of unread messages by parsing the HTML page with Playwright."""
        self._check_auth()

        if not _has_playwright:
            logger.debug("Playwright not available, skipping unread detection")
            return set()

        url = f"{self.base_url}/{self.user_id}/messages"
        unread_ids = set()

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context()

            # Set auth cookie with proper typing
            cookie_domain = urlparse(self.base_url).netloc
            if _has_playwright:
                cookie: SetCookieParam = {
                    "name": "Wilma2SID",
                    "value": self._sid or "",
                    "domain": cookie_domain,
                    "path": "/",
                    "sameSite": "Lax",
                }
                await context.add_cookies([cookie])

            page = await context.new_page()

            try:
                response = await page.goto(url)
                if not response or response.status != 200:
                    status = response.status if response else "No response"
                    raise WilmaError(f"Failed to load messages page: {status}")

                await page.wait_for_selector(
                    "table#message-list-table", state="attached", timeout=10000
                )
                html_content = await page.content()
                soup = BeautifulSoup(html_content, "html.parser")

                # Extract unread message IDs
                for row in soup.select("table#message-list-table tbody tr"):
                    checkbox = row.select_one('input[name="mid"]')
                    if checkbox and checkbox.get("value"):
                        value = checkbox.get("value")
                        if not isinstance(value, str):
                            continue
                        try:
                            message_id = int(value)
                            td = row.select_one("td:nth-child(2)")
                            if td and td.text.strip():
                                unread_ids.add(message_id)
                        except (ValueError, AttributeError):
                            continue

                logger.debug("Found %s unread messages", len(unread_ids))
            finally:
                await browser.close()

        return unread_ids

    async def _authenticated_request(
        self,
        url_template: str,
        method: str = "GET",
        data: dict[str, Any] | None = None,
        params: dict[str, str | int | bool] | None = None,
        retry: bool = False,
        **kwargs: Any,
    ) -> aiohttp.ClientResponse:
        """Make an authenticated request to the Wilma API."""
        self._check_auth()
        session = await self._ensure_session()

        # Replace {user_id} in template if present
        path = url_template
        if "{user_id}" in url_template and self.user_id:
            path = url_template.format(user_id=self.user_id)

        # Construct full URL with base_url
        url = f"{self.base_url}/{path.lstrip('/')}"

        # Add auth header
        headers = kwargs.pop("headers", {})
        headers["Wilma2SID"] = self._sid or ""

        # Make request
        method = method.upper()
        request_kwargs = {"headers": headers, **kwargs}

        if params:
            request_kwargs["params"] = params

        if data and method == "POST":
            request_kwargs["data"] = data

        logger.debug("Making %s request to %s", method, url)

        response: ClientResponse = await getattr(session, method.lower())(url, **request_kwargs)

        # Session expires after a while, and at times we get 403 errors, re-auth in these cases
        # but just do it once, since if a re-auth does not work, then we most likely are locked
        # our for a valid reason.
        reauth_matches = ["sessionexpired", "invalidsession"]
        realurl = str(response.request_info.real_url)

        if (
            not retry
            and any(match in realurl for match in reauth_matches)
            or response.status == 403
        ):
            logger.debug("Session expired, logging in again")
            await self.login()
            return await self._authenticated_request(
                url_template, method, data, params, True, **kwargs
            )

        if response.status >= 400:
            raise WilmaError(f"Request failed with status {response.status}: {url}")

        return response

    async def get_messages(
        self,
        only_unread: bool = False,
        after: datetime.datetime | None = None,
        with_content: bool = False,
        no_message_content_fetch_limit: bool = False,
    ) -> list[Message]:
        """Get messages list."""
        # Get unread message IDs
        unread_message_ids = await self._get_unread_message_ids()

        response = await self._authenticated_request("{user_id}/messages/list")
        data = await response.json()
        messages = []

        # Convert after to naive datetime if it has timezone info
        # We don't have any TZ info for the Wilma messages
        if after and after.tzinfo is not None:
            after = after.replace(tzinfo=None)

        for msg in data.get("Messages", []):
            message = Message.from_dict(msg)
            message.unread = message.id in unread_message_ids

            # Skip if only_unread is True and message is not unread
            if only_unread and not message.unread:
                continue

            # Skip if before is provided and message is not before the date
            if after and message.timestamp and message.format_timestamp() <= after:
                continue

            messages.append(message)

        # Fetch full content for messages if requested
        if with_content:
            if len(messages) > 10:
                if not no_message_content_fetch_limit:
                    raise WilmaError(
                        "Not allowed to fetch full message content for more than 10 messages."
                        "Set no_message_content_fetch_limit=True to override this limit."
                    )
                logger.warning(
                    "Fetching full message content for %s messages may take a while..",
                    len(messages),
                )
            for message in messages:
                try:
                    full_message = await self.get_message_content(message.id)
                    # Update message with content from full_message
                    message.content_html = full_message.content_html
                    # Preserve other attributes that might be in the full message
                    for attr, value in vars(full_message).items():
                        if attr != "unread" and getattr(message, attr, None) is None:
                            setattr(message, attr, value)
                except Exception as e:
                    logger.warning("Failed to fetch content for message %s: %s", message.id, e)

        return messages

    async def get_message_content(self, message_id: int) -> Message:
        """Get content of a message."""
        # Check if message is unread
        unread_message_ids = await self._get_unread_message_ids()

        url_template = "{user_id}/messages/{message_id}"
        url = url_template.format(user_id="{user_id}", message_id=message_id)

        response = await self._authenticated_request(url, params={"format": "json"})

        data = await response.json()
        message = Message.from_dict(data["messages"][0])
        message.unread = message_id in unread_message_ids

        return message

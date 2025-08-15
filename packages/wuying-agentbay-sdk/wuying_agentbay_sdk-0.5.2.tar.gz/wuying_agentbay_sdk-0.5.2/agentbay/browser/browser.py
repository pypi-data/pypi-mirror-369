from typing import TYPE_CHECKING, Optional
import asyncio
import time
from agentbay.api.models import InitBrowserRequest
from agentbay.browser.browser_agent import BrowserAgent
from agentbay.api.base_service import BaseService
from agentbay.exceptions import BrowserError
from agentbay.config import BROWSER_DATA_PATH

if TYPE_CHECKING:
    from agentbay.session import Session

class BrowserOption:
    """
    Placeholder for browser initialization options.
    """
    pass

class Browser(BaseService):
    """
    Browser provides browser-related operations for the session.
    """
    def __init__(self, session: "Session"):
        self.session = session
        self._endpoint_url = None
        self._initialized = False
        self._option = None
        self.agent = BrowserAgent(self.session, self)

    def initialize(self, option: "BrowserOption") -> bool:
        """
        Initialize the browser instance with the given options.
        Returns True if successful, False otherwise.
        """
        if self.is_initialized():
            return True
        try:
            request = InitBrowserRequest(
                authorization=f"Bearer {self.session.get_api_key()}",
                session_id=self.session.get_session_id(),
                persistent_path=BROWSER_DATA_PATH,
            )
            response = self.session.get_client().init_browser(request)
            
            print(f"Response from init_browser: {response}")
            response_map = response.to_map()
            body = response_map.get("body", {})
            data = body.get("Data", {})
            success = data.get("Port") is not None
            if success:
                self._initialized = True
                self._option = option
                print("Browser instance was successfully initialized.")

            return success
        except Exception as e:
            print("Failed to initialize browser instance:", e)
            self._initialized = False
            self._endpoint_url = None
            self._option = None
            return False

    async def initialize_async(self, option: "BrowserOption") -> bool:
        """
        Initialize the browser instance with the given options asynchronously.
        Returns True if successful, False otherwise.
        """
        if self.is_initialized():
            return True
        try:
            request = InitBrowserRequest(
                authorization=f"Bearer {self.session.get_api_key()}",
                session_id=self.session.get_session_id(),
                persistent_path=BROWSER_DATA_PATH,
            )
            response = await self.session.get_client().init_browser_async(request)
            print(f"Response from init_browser: {response}")
            response_map = response.to_map()
            body = response_map.get("body", {})
            data = body.get("Data", {})
            success = data.get("Port") is not None
            if success:
                self._initialized = True
                self._option = option
                print("Browser instance successfully initialized")
            return success
        except Exception as e:
            print("Failed to initialize browser instance:", e)
            self._initialized = False
            self._endpoint_url = None
            self._option = None
            return False

    def _stop_browser(self):
        """
        Stop the browser instance, internal use only.
        """
        if self.is_initialized():
            self._call_mcp_tool("stopChrome", {})
        else:
            raise BrowserError("Browser is not initialized. Cannot stop browser.")

    def get_endpoint_url(self) -> str:
        """
        Returns the endpoint URL if the browser is initialized, otherwise raises an exception.
        When initialized, always fetches the latest CDP url from session.get_link().
        """
        if not self.is_initialized():
            raise BrowserError("Browser is not initialized. Cannot access endpoint URL.")
        try:
            cdp_url = self.session.get_link()
            self._endpoint_url = cdp_url.data
            return self._endpoint_url
        except Exception as e:
            raise BrowserError(f"Failed to get endpoint URL from session: {e}")

    def get_option(self) -> Optional["BrowserOption"]:
        """
        Returns the current BrowserOption used to initialize the browser, or None if not set.
        """
        return self._option

    def is_initialized(self) -> bool:
        """
        Returns True if the browser was initialized, False otherwise.
        """
        return self._initialized

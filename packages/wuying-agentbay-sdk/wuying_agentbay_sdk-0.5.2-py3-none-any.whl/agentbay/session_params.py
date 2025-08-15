from typing import Dict, Optional, List
from agentbay.context_sync import ContextSync


class BrowserContext:
    """
    Browser context configuration for session.
    
    Attributes:
        context_id (str): ID of the browser context to bind to the session
        auto_upload (bool): Whether to automatically upload browser data when session ends
    """
    
    def __init__(self, context_id: str, auto_upload: bool = True):
        """
        Initialize BrowserContext.
        
        Args:
            context_id (str): ID of the browser context to bind to the session
            auto_upload (bool): Whether to automatically upload browser data when session ends
        """
        self.context_id = context_id
        self.auto_upload = auto_upload


class CreateSessionParams:
    """
    Parameters for creating a new session in the AgentBay cloud environment.

    Attributes:
        labels (Optional[Dict[str, str]]): Custom labels for the Session. These can be
            used for organizing and filtering sessions.
        context_id (Optional[str]): ID of the context to bind to the session. The
            context can include various types of persistence like file system (volume)
            and cookies.
            Deprecated: This field is deprecated and will be removed in a future version.
            Please use context_syncs instead for more flexible and powerful data persistence.
        context_syncs (Optional[List[ContextSync]]): List of context synchronization
            configurations that define how contexts should be synchronized and mounted.
        browser_context (Optional[BrowserContext]): Optional configuration for browser data synchronization.
        is_vpc (Optional[bool]): Whether to create a VPC-based session. Defaults to False.
    """

    def __init__(
        self,
        labels: Optional[Dict[str, str]] = None,
        context_id: Optional[str] = None,  # Deprecated: Use context_syncs instead
        image_id: Optional[str] = None,
        context_syncs: Optional[List[ContextSync]] = None,
        browser_context: Optional[BrowserContext] = None,
        is_vpc: Optional[bool] = None,
    ):
        """
        Initialize CreateSessionParams.

        Args:
            labels (Optional[Dict[str, str]], optional): Custom labels for the Session.
                Defaults to None.
            context_id (Optional[str], optional): ID of the context to bind to the
                session. Defaults to None.
                Deprecated: This field is deprecated and will be removed in a future version.
                Please use context_syncs instead.
            image_id (Optional[str], optional): ID of the image to use for the session.
                Defaults to None.
            context_syncs (Optional[List[ContextSync]], optional): List of context
                synchronization configurations. Defaults to None.
            browser_context (Optional[BrowserContext], optional): Browser context configuration.
                Defaults to None.
            is_vpc (Optional[bool], optional): Whether to create a VPC-based session.
                Defaults to False.
        """
        self.labels = labels or {}
        self.context_id = context_id
        self.image_id = image_id
        self.context_syncs = context_syncs or []
        self.browser_context = browser_context
        self.is_vpc = is_vpc if is_vpc is not None else False


class ListSessionParams:
    """
    Parameters for listing sessions with pagination support.

    Attributes:
        max_results (int): Number of results per page.
        next_token (str): Token for the next page.
        labels (Dict[str, str]): Labels to filter by.
    """

    def __init__(
        self,
        max_results: int = 10,
        next_token: str = "",
        labels: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize ListSessionParams with default values.

        Args:
            max_results (int, optional): Number of results per page. Defaults to 10.
            next_token (str, optional): Token for the next page. Defaults to "".
            labels (Optional[Dict[str, str]], optional): Labels to filter by.
                Defaults to None.
        """
        self.max_results = max_results
        self.next_token = next_token
        self.labels = labels if labels is not None else {}

"""Main ReZEN API client."""

from typing import Optional

from .agents import AgentsClient
from .api_keys import ApiKeysClient
from .auth import AuthClient
from .checklist import ChecklistClient
from .directory import DirectoryClient
from .documents import DocumentClient
from .dropbox import DropboxClient
from .mfa import MfaClient
from .teams import TeamsClient
from .transaction_builder import TransactionBuilderClient
from .transactions import TransactionsClient
from .users import UsersClient


class RezenClient:
    """Main client for the ReZEN API.

    This is the primary interface for interacting with the ReZEN API.
    It provides access to different API sections through client properties.

    Example:
        ```python
        from rezen import RezenClient

        # Initialize with API key from environment variable
        client = RezenClient()

        # Or provide API key directly
        client = RezenClient(api_key="your_api_key_here")

        # Use authentication endpoints
        auth_response = client.auth.signin(
            username="user@example.com",
            password="password"
        )

        # Use MFA endpoints
        mfa_response = client.mfa.signin_with_mfa(
            username="user@example.com",
            mfa_code="123456"
        )

        # Use API keys endpoints
        api_keys = client.api_keys.get_api_keys()

        # Use transaction builder endpoints
        response = client.transaction_builder.update_title_info(
            transaction_id="12345",
            title_info={"title": "New Title Information"}
        )

        # Use transactions endpoints
        response = client.transactions.get_transaction("tx-12345")

        # Use teams endpoints
        teams = client.teams.search_teams(status="ACTIVE")

        # Use agents endpoints
        agents = client.agents.search_active_agents(name="John")

        # Use directory endpoints
        vendors = client.directory.search_vendors(
            page_number=0, page_size=10, is_archived=False
        )

        # Use checklist endpoints to upload documents
        with open('document.pdf', 'rb') as f:
            result = client.checklist.add_document_to_checklist_item(
                checklist_item_id='550e8400-e29b-41d4-a716-446655440000',
                name='Purchase Agreement',
                description='Signed purchase agreement',
                uploader_id='123e4567-e89b-12d3-a456-426614174000',
                transaction_id='987fcdeb-51d2-4321-b789-123456789012',
                file=f
            )

        # Use document endpoints
        doc_response = client.documents.post_document(
            data={"title": "Contract"},
            file=open('contract.pdf', 'rb')
        )

        # Use Dropbox endpoints
        auth_url = client.dropbox.get_auth_url()
        folders = client.dropbox.get_folders(agent_id="agent-uuid")
        ```
    """

    def __init__(
        self, api_key: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        """Initialize the ReZEN client.

        Args:
            api_key: API key for authentication. If None, will look for REZEN_API_KEY env var
            base_url: Base URL for the API. Defaults to production URL
        """
        self._api_key = api_key
        self._base_url = base_url
        self._auth: Optional[AuthClient] = None
        self._mfa: Optional[MfaClient] = None
        self._api_keys: Optional[ApiKeysClient] = None
        self._transaction_builder: Optional[TransactionBuilderClient] = None
        self._transactions: Optional[TransactionsClient] = None
        self._teams: Optional[TeamsClient] = None
        self._agents: Optional[AgentsClient] = None
        self._directory: Optional[DirectoryClient] = None
        self._users: Optional[UsersClient] = None
        self._checklist: Optional[ChecklistClient] = None
        self._documents: Optional[DocumentClient] = None
        self._dropbox: Optional[DropboxClient] = None

    @property
    def transaction_builder(self) -> TransactionBuilderClient:
        """Access to transaction builder endpoints.

        Returns:
            TransactionBuilderClient instance
        """
        if self._transaction_builder is None:
            self._transaction_builder = TransactionBuilderClient(
                api_key=self._api_key, base_url=self._base_url
            )
        return self._transaction_builder

    @property
    def transactions(self) -> TransactionsClient:
        """Access to transactions endpoints.

        Returns:
            TransactionsClient instance
        """
        if self._transactions is None:
            self._transactions = TransactionsClient(
                api_key=self._api_key, base_url=self._base_url
            )
        return self._transactions

    @property
    def teams(self) -> TeamsClient:
        """Access to teams endpoints.

        Returns:
            TeamsClient instance
        """
        if self._teams is None:
            # Teams uses yenta API, so don't pass custom base_url
            self._teams = TeamsClient(api_key=self._api_key)
        return self._teams

    @property
    def agents(self) -> AgentsClient:
        """Access to agents endpoints.

        Returns:
            AgentsClient instance
        """
        if self._agents is None:
            # Agents uses yenta API, so don't pass custom base_url
            self._agents = AgentsClient(api_key=self._api_key)
        return self._agents

    @property
    def directory(self) -> DirectoryClient:
        """Access to directory endpoints.

        Returns:
            DirectoryClient instance
        """
        if self._directory is None:
            # Directory uses yenta API, so don't pass custom base_url
            self._directory = DirectoryClient(api_key=self._api_key)
        return self._directory

    @property
    def auth(self) -> AuthClient:
        """Access to authentication endpoints.

        Returns:
            AuthClient instance
        """
        if self._auth is None:
            # Auth uses keymaker API, so don't pass custom base_url
            self._auth = AuthClient(api_key=self._api_key)
        return self._auth

    @property
    def mfa(self) -> MfaClient:
        """Access to multi-factor authentication endpoints.

        Returns:
            MfaClient instance
        """
        if self._mfa is None:
            # MFA uses keymaker API, so don't pass custom base_url
            self._mfa = MfaClient(api_key=self._api_key)
        return self._mfa

    @property
    def api_keys(self) -> ApiKeysClient:
        """Access to API keys endpoints.

        Returns:
            ApiKeysClient instance
        """
        if self._api_keys is None:
            # API keys uses keymaker API, so don't pass custom base_url
            self._api_keys = ApiKeysClient(api_key=self._api_key)
        return self._api_keys

    @property
    def users(self) -> UsersClient:
        """Access to users endpoints.

        Returns:
            UsersClient instance
        """
        if self._users is None:
            # Users uses yenta API, so don't pass custom base_url
            self._users = UsersClient(api_key=self._api_key)
        return self._users

    @property
    def checklist(self) -> ChecklistClient:
        """Access to checklist endpoints.

        Returns:
            ChecklistClient instance
        """
        if self._checklist is None:
            # Checklist uses sherlock API, so don't pass custom base_url
            self._checklist = ChecklistClient(api_key=self._api_key)
        return self._checklist

    @property
    def documents(self) -> DocumentClient:
        """Access to document/signature endpoints.

        Returns:
            DocumentClient instance
        """
        if self._documents is None:
            self._documents = DocumentClient(
                api_key=self._api_key, base_url=self._base_url
            )
        return self._documents

    @property
    def dropbox(self) -> DropboxClient:
        """Access to Dropbox integration endpoints.

        Returns:
            DropboxClient instance
        """
        if self._dropbox is None:
            # Dropbox uses sherlock API, so don't pass custom base_url
            self._dropbox = DropboxClient(api_key=self._api_key)
        return self._dropbox

"""Transactions client for ReZEN API."""

from typing import Any, Dict, List, Optional

from .base_client import BaseClient


class TransactionsClient(BaseClient):
    """Client for transactions endpoints."""

    # ===== TRANSACTION MANAGEMENT =====

    def get_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Get a specific transaction by ID.

        Args:
            transaction_id: Transaction ID

        Returns:
            Transaction data
        """
        endpoint = f"transactions/{transaction_id}"
        return self.get(endpoint)

    def get_transaction_explanation(self, transaction_id: str) -> Dict[str, Any]:
        """Get verbose explanation of transaction without participant payout explanations.

        Args:
            transaction_id: Transaction ID

        Returns:
            Transaction explanation data
        """
        endpoint = f"transactions/{transaction_id}/transaction-explanation"
        return self.get(endpoint)

    def get_payout_explanation(self, transaction_id: str) -> Dict[str, Any]:
        """Get payout explanation for transaction.

        Args:
            transaction_id: Transaction ID

        Returns:
            Payout explanation data
        """
        endpoint = f"transactions/{transaction_id}/payout-explanation"
        return self.get(endpoint)

    def get_participant_payout_explanation(
        self, transaction_id: str, participant_id: str
    ) -> Dict[str, Any]:
        """Get payout explanation for specific participant.

        Args:
            transaction_id: Transaction ID
            participant_id: Participant ID

        Returns:
            Participant payout explanation data
        """
        endpoint = f"transactions/{transaction_id}/payout-explanation/{participant_id}"
        return self.get(endpoint)

    def get_metadata_for_participant_creation(
        self, transaction_id: str, participant_role: str
    ) -> Dict[str, Any]:
        """Get metadata required to create a participant.

        Args:
            transaction_id: Transaction ID
            participant_role: Role of the participant to be created

        Returns:
            Metadata for participant creation
        """
        endpoint = f"transactions/{transaction_id}/metadata-for-participant-creation/{participant_role}"
        return self.get(endpoint)

    def get_transaction_features(self, transaction_id: str) -> Dict[str, Any]:
        """Get optional features available for the transaction.

        Args:
            transaction_id: Transaction ID

        Returns:
            Available features data
        """
        endpoint = f"transactions/{transaction_id}/features"
        return self.get(endpoint)

    def get_transaction_permissions(self, transaction_id: str) -> Dict[str, Any]:
        """Get transaction permissions.

        Args:
            transaction_id: Transaction ID

        Returns:
            Transaction permissions data
        """
        endpoint = f"transactions/{transaction_id}/permissions"
        return self.get(endpoint)

    def check_transaction_permissions(self, transaction_id: str) -> Dict[str, Any]:
        """Check transaction permissions.

        Args:
            transaction_id: Transaction ID

        Returns:
            Permission check results
        """
        endpoint = f"transactions/{transaction_id}/check-permissions"
        return self.get(endpoint)

    def get_transaction_process(self, transaction_id: str) -> Dict[str, Any]:
        """Get transaction process information.

        Args:
            transaction_id: Transaction ID

        Returns:
            Transaction process data
        """
        endpoint = f"transactions/{transaction_id}/process"
        return self.get(endpoint)

    def get_transaction_summary_pdf(self, transaction_id: str) -> Dict[str, Any]:
        """Get transaction summary PDF.

        Args:
            transaction_id: Transaction ID

        Returns:
            PDF download information
        """
        endpoint = f"transactions/{transaction_id}/summary-pdf"
        return self.get(endpoint)

    def is_display_agent_reported_transaction_closed_dialog(
        self, transaction_id: str
    ) -> Dict[str, Any]:
        """Check if agent reported transaction closed dialog should be displayed.

        Args:
            transaction_id: Transaction ID

        Returns:
            Dialog display status
        """
        endpoint = f"transactions/{transaction_id}/is-display-agent-reported-transaction-closed-dialog"
        return self.get(endpoint)

    def get_transaction_by_code(self, transaction_code: str) -> Dict[str, Any]:
        """Get transaction by transaction code.

        Args:
            transaction_code: Transaction code

        Returns:
            Transaction data
        """
        endpoint = f"transactions/code/{transaction_code}"
        return self.get(endpoint)

    # ===== TITLE MANAGEMENT =====

    def update_transaction_title(
        self, transaction_id: str, title_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update title information for transaction.

        Args:
            transaction_id: Transaction ID
            title_info: Title information data

        Returns:
            Updated transaction data
        """
        endpoint = f"transactions/{transaction_id}/title"
        return self.put(endpoint, json_data=title_info)

    def update_title_system_user(
        self, transaction_id: str, system_user_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update title system user information.

        Args:
            transaction_id: Transaction ID
            system_user_info: System user information data

        Returns:
            Updated transaction data
        """
        endpoint = f"transactions/{transaction_id}/title/system-user"
        return self.put(endpoint, json_data=system_user_info)

    def update_title_order(
        self, transaction_id: str, title_order_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update title order information.

        Args:
            transaction_id: Transaction ID
            title_order_info: Title order information data

        Returns:
            Updated transaction data
        """
        endpoint = f"transactions/{transaction_id}/title-order"
        return self.put(endpoint, json_data=title_order_info)

    def get_title_order_placement_eligibility(
        self, transaction_id: str
    ) -> Dict[str, Any]:
        """Get title order placement eligibility.

        Args:
            transaction_id: Transaction ID

        Returns:
            Placement eligibility data
        """
        endpoint = f"transactions/{transaction_id}/title-order/placement-eligibility"
        return self.get(endpoint)

    # ===== PARTICIPANT MANAGEMENT =====

    def update_participant(
        self, transaction_id: str, participant_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update participant information.

        Args:
            transaction_id: Transaction ID
            participant_info: Participant information data

        Returns:
            Updated transaction data
        """
        endpoint = f"transactions/{transaction_id}/participant"
        return self.put(endpoint, json_data=participant_info)

    def update_participant_opcity(
        self, transaction_id: str, opcity_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update participant opcity information.

        Args:
            transaction_id: Transaction ID
            opcity_info: Opcity information data

        Returns:
            Updated transaction data
        """
        endpoint = f"transactions/{transaction_id}/participant/opcity"
        return self.put(endpoint, json_data=opcity_info)

    def create_participant(
        self, transaction_id: str, participant_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create transaction participant.

        Args:
            transaction_id: Transaction ID
            participant_data: Participant creation data

        Returns:
            Created participant data
        """
        endpoint = f"transactions/{transaction_id}/create-participant"
        return self.post(endpoint, json_data=participant_data)

    def get_participant_lite(
        self, transaction_id: str, participant_id: str
    ) -> Dict[str, Any]:
        """Get lite participant information.

        Args:
            transaction_id: Transaction ID
            participant_id: Participant ID

        Returns:
            Lite participant data
        """
        endpoint = f"transactions/{transaction_id}/participant/{participant_id}/lite"
        return self.get(endpoint)

    def get_participant_payment(
        self, transaction_id: str, participant_id: str
    ) -> Dict[str, Any]:
        """Get participant payment information.

        Args:
            transaction_id: Transaction ID
            participant_id: Participant ID

        Returns:
            Participant payment data
        """
        endpoint = f"transactions/{transaction_id}/participant/{participant_id}/payment"
        return self.get(endpoint)

    def get_agent_participants(self, transaction_id: str) -> Dict[str, Any]:
        """Get agent participants for transaction.

        Args:
            transaction_id: Transaction ID

        Returns:
            Agent participants data
        """
        endpoint = f"transactions/{transaction_id}/agent-participants"
        return self.get(endpoint)

    def get_comment_participants(
        self, transaction_id: str, agent_id: str
    ) -> Dict[str, Any]:
        """Get comment participants for agent.

        Args:
            transaction_id: Transaction ID
            agent_id: Agent ID

        Returns:
            Comment participants data
        """
        endpoint = f"transactions/{transaction_id}/comment-participants/{agent_id}"
        return self.get(endpoint)

    def get_checklist_assignees(self, transaction_id: str) -> Dict[str, Any]:
        """Get checklist assignees for transaction.

        Args:
            transaction_id: Transaction ID

        Returns:
            Checklist assignees data
        """
        endpoint = f"transactions/{transaction_id}/checklist-assignees"
        return self.get(endpoint)

    # ===== PAYMENT AND FINANCIAL =====

    def get_payment_info(self, transaction_id: str, agent_id: str) -> Dict[str, Any]:
        """Get payment information for agent.

        Args:
            transaction_id: Transaction ID
            agent_id: Agent ID

        Returns:
            Payment information data
        """
        endpoint = f"transactions/{transaction_id}/payment-info/{agent_id}"
        return self.get(endpoint)

    def get_paid_at_closing(self, transaction_id: str) -> Dict[str, Any]:
        """Get paid at closing information.

        Args:
            transaction_id: Transaction ID

        Returns:
            Paid at closing data
        """
        endpoint = f"transactions/{transaction_id}/paid-at-closing"
        return self.get(endpoint)

    def get_money_transfers(self, transaction_id: str) -> Dict[str, Any]:
        """Get money transfers for transaction.

        Args:
            transaction_id: Transaction ID

        Returns:
            Money transfers data
        """
        endpoint = f"transactions/{transaction_id}/money-transfers"
        return self.get(endpoint)

    def update_attached_fee(
        self, transaction_id: str, fee_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update attached fee information.

        Args:
            transaction_id: Transaction ID
            fee_info: Fee information data

        Returns:
            Updated transaction data
        """
        endpoint = f"transactions/{transaction_id}/attached-fee"
        return self.put(endpoint, json_data=fee_info)

    # ===== ESCROW MANAGEMENT =====

    def create_escrow(
        self, transaction_id: str, escrow_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create escrow for transaction.

        Args:
            transaction_id: Transaction ID
            escrow_data: Escrow creation data

        Returns:
            Created escrow data
        """
        endpoint = f"transactions/{transaction_id}/escrow"
        return self.post(endpoint, json_data=escrow_data)

    def create_escrow_deposit(
        self, escrow_id: str, deposit_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deposit a payment for an escrow (trust deposit).

        Args:
            escrow_id: Escrow ID
            deposit_data: Deposit data

        Returns:
            Escrow response data
        """
        endpoint = f"transactions/escrows/{escrow_id}/escrow-deposit"
        return self.post(endpoint, json_data=deposit_data)

    def get_escrow_deposit(
        self, escrow_id: str, escrow_deposit_id: str
    ) -> Dict[str, Any]:
        """Get specific escrow deposit.

        Args:
            escrow_id: Escrow ID
            escrow_deposit_id: Escrow deposit ID

        Returns:
            Escrow deposit data
        """
        endpoint = (
            f"transactions/escrows/{escrow_id}/escrow-deposit/{escrow_deposit_id}"
        )
        return self.get(endpoint)

    def update_escrow_check_deposit(
        self, escrow_id: str, check_deposit_id: str, deposit_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update escrow check deposit.

        Args:
            escrow_id: Escrow ID
            check_deposit_id: Check deposit ID
            deposit_data: Updated deposit data

        Returns:
            Updated escrow data
        """
        endpoint = f"transactions/escrows/{escrow_id}/check-deposits/{check_deposit_id}"
        return self.put(endpoint, json_data=deposit_data)

    # ===== CHECK DEPOSITS =====

    def update_check_deposit(
        self, transaction_id: str, check_deposit_id: str, deposit_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update check deposit.

        Args:
            transaction_id: Transaction ID
            check_deposit_id: Check deposit ID
            deposit_data: Updated deposit data

        Returns:
            Updated transaction data
        """
        endpoint = f"transactions/{transaction_id}/check-deposits/{check_deposit_id}"
        return self.put(endpoint, json_data=deposit_data)

    def get_check_deposits(self, transaction_id: str) -> Dict[str, Any]:
        """Get check deposits for transaction.

        Args:
            transaction_id: Transaction ID

        Returns:
            Check deposits data
        """
        endpoint = f"transactions/{transaction_id}/check-deposits"
        return self.get(endpoint)

    def get_check_deposit_upload_link(
        self, transaction_id: str, deposit_type: str
    ) -> Dict[str, Any]:
        """Get upload link for check deposit.

        Args:
            transaction_id: Transaction ID
            deposit_type: Type of deposit

        Returns:
            Upload link data
        """
        endpoint = (
            f"transactions/{transaction_id}/check-deposits/{deposit_type}/upload-link"
        )
        return self.get(endpoint)

    def get_check_deposit_front_image_download_url(
        self, transaction_id: str, check_deposit_id: str
    ) -> Dict[str, Any]:
        """Get front image download URL for check deposit.

        Args:
            transaction_id: Transaction ID
            check_deposit_id: Check deposit ID

        Returns:
            Front image download URL
        """
        endpoint = f"transactions/{transaction_id}/check-deposits/{check_deposit_id}/front-image/download-url"
        return self.get(endpoint)

    def get_check_deposit_back_image_download_url(
        self, transaction_id: str, check_deposit_id: str
    ) -> Dict[str, Any]:
        """Get back image download URL for check deposit.

        Args:
            transaction_id: Transaction ID
            check_deposit_id: Check deposit ID

        Returns:
            Back image download URL
        """
        endpoint = f"transactions/{transaction_id}/check-deposits/{check_deposit_id}/back-image/download-url"
        return self.get(endpoint)

    # ===== BANK ACCOUNTS =====

    def get_canada_bank_accounts(self, transaction_id: str) -> Dict[str, Any]:
        """Get Canada bank accounts for transaction.

        Args:
            transaction_id: Transaction ID

        Returns:
            Canada bank accounts data
        """
        endpoint = f"transactions/{transaction_id}/canada-bank-accounts"
        return self.get(endpoint)

    def get_bank_accounts(self, transaction_id: str) -> Dict[str, Any]:
        """Get bank accounts for transaction.

        Args:
            transaction_id: Transaction ID

        Returns:
            Bank accounts data
        """
        endpoint = f"transactions/{transaction_id}/bank-accounts"
        return self.get(endpoint)

    # ===== DOUBLE ENDER =====

    def update_double_ender(
        self, transaction_id: str, double_ender_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update double ender information.

        Args:
            transaction_id: Transaction ID
            double_ender_info: Double ender information data

        Returns:
            Updated transaction data
        """
        endpoint = f"transactions/{transaction_id}/double-ender"
        return self.put(endpoint, json_data=double_ender_info)

    def update_agent_reported_transaction_closed_dialog(
        self, transaction_id: str, dialog_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update agent reported transaction closed dialog.

        Args:
            transaction_id: Transaction ID
            dialog_info: Dialog information data

        Returns:
            Updated transaction data
        """
        endpoint = (
            f"transactions/{transaction_id}/agent-reported-transaction-closed-dialog"
        )
        return self.put(endpoint, json_data=dialog_info)

    # ===== BATCH AND LIST OPERATIONS =====

    def get_transactions_lite_batch(self, transaction_ids: List[str]) -> Dict[str, Any]:
        """Get multiple transactions in lite format.

        Args:
            transaction_ids: List of transaction IDs

        Returns:
            Batch transaction data
        """
        endpoint = "transactions/lite/batch-get"
        params = {"transactionIds": ",".join(transaction_ids)}
        return self.get(endpoint, params=params)

    def get_rolling_transactions(
        self,
        page_number: int = 0,
        page_size: int = 20,
        sort_by: Optional[str] = None,
        sort_direction: str = "ASC",
        **filters: Any,
    ) -> Dict[str, Any]:
        """Get rolling transactions with pagination and filtering.

        Args:
            page_number: Page number (default 0)
            page_size: Page size (default 20)
            sort_by: Sort field
            sort_direction: Sort direction ('ASC' or 'DESC')
            **filters: Additional filter parameters

        Returns:
            Paginated rolling transactions data
        """
        endpoint = "transactions/rolling"
        params = {
            "pageNumber": page_number,
            "pageSize": page_size,
            "sortDirection": sort_direction,
            **filters,
        }
        if sort_by:
            params["sortBy"] = sort_by
        return self.get(endpoint, params=params)

    # ===== PARTICIPANT TRANSACTIONS =====

    def get_participant_transactions(self, yenta_id: str) -> Dict[str, Any]:
        """Get transactions for participant.

        Args:
            yenta_id: Participant (user) ID

        Returns:
            Participant transactions data
        """
        endpoint = f"transactions/participant/{yenta_id}"
        return self.get(endpoint)

    def get_participant_transactions_by_lifecycle_group(
        self,
        yenta_id: str,
        lifecycle_group: str,
        page_number: int,
        page_size: int,
        search_text: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_direction: Optional[str] = None,
        transaction_type: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get transactions for participant by lifecycle group with pagination.

        Args:
            yenta_id: Participant (user) ID
            lifecycle_group: Lifecycle group ('OPEN', 'LISTING_ACTIVE', 'CLOSED', 'TERMINATED', 'LISTING_NONTERMINATED')
            page_number: Page number
            page_size: Page size
            search_text: Search text (optional)
            sort_by: Sort field (optional)
            sort_direction: Sort direction (optional)
            transaction_type: List of transaction types to filter by (optional)

        Returns:
            Paginated participant transactions data
        """
        endpoint = f"transactions/participant/{yenta_id}/transactions/{lifecycle_group}"
        params: Dict[str, Any] = {"pageNumber": page_number, "pageSize": page_size}

        if search_text:
            params["searchText"] = search_text
        if sort_by:
            params["sortBy"] = sort_by
        if sort_direction:
            params["sortDirection"] = sort_direction
        if transaction_type:
            params["transactionType"] = transaction_type

        return self.get(endpoint, params=params)

    def get_participant_transaction_lifecycle_group_counts(
        self, yenta_id: str
    ) -> Dict[str, Any]:
        """Get transaction lifecycle group counts for participant.

        Args:
            yenta_id: Participant (user) ID

        Returns:
            Lifecycle group counts data
        """
        endpoint = (
            f"transactions/participant/{yenta_id}/transactions/lifecycle-group-counts"
        )
        return self.get(endpoint)

    def get_participant_listing_transactions(
        self,
        yenta_id: str,
        lifecycle_group: str,
        page_number: int,
        page_size: int,
        search_text: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_direction: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get listing transactions for participant by lifecycle group.

        Args:
            yenta_id: Participant (user) ID
            lifecycle_group: Lifecycle group
            page_number: Page number
            page_size: Page size
            search_text: Search text (optional)
            sort_by: Sort field (optional)
            sort_direction: Sort direction (optional)

        Returns:
            Paginated participant listing transactions data
        """
        endpoint = f"transactions/participant/{yenta_id}/listing-transactions/{lifecycle_group}"
        params: Dict[str, Any] = {"pageNumber": page_number, "pageSize": page_size}

        if search_text:
            params["searchText"] = search_text
        if sort_by:
            params["sortBy"] = sort_by
        if sort_direction:
            params["sortDirection"] = sort_direction

        return self.get(endpoint, params=params)

    def get_participant_listing_transaction_lifecycle_group_counts(
        self, yenta_id: str
    ) -> Dict[str, Any]:
        """Get listing transaction lifecycle group counts for participant.

        Args:
            yenta_id: Participant (user) ID

        Returns:
            Listing transaction lifecycle group counts data
        """
        endpoint = f"transactions/participant/{yenta_id}/listing-transactions/lifecycle-group-counts"
        return self.get(endpoint)

    def get_participant_current_transactions(self, yenta_id: str) -> Dict[str, Any]:
        """Get participant's current transactions.

        Args:
            yenta_id: User/participant ID

        Returns:
            Current transactions data
        """
        endpoint = f"transactions/participant/{yenta_id}/current"
        return self.get(endpoint)

    # ===== BACKWARD COMPATIBILITY METHODS =====

    def get_agent_transactions(self, yenta_id: str) -> Dict[str, Any]:
        """Get agent's transactions (wrapper for get_participant_transactions).

        Args:
            yenta_id: Agent's user ID

        Returns:
            Agent's transactions data
        """
        return self.get_participant_transactions(yenta_id)

    def get_agent_current_transactions(self, yenta_id: str) -> Dict[str, Any]:
        """Get agent's current transactions (wrapper for get_participant_current_transactions).

        Args:
            yenta_id: Agent's user ID

        Returns:
            Agent's current transactions data
        """
        return self.get_participant_current_transactions(yenta_id)

    def get_agent_current_listings(self, yenta_id: str) -> Dict[str, Any]:
        """Get agent's current listings.

        Args:
            yenta_id: Agent's user ID

        Returns:
            Agent's current listings data
        """
        # Use the participant listing transactions endpoint with 'CURRENT' lifecycle group
        return self.get_participant_listing_transactions(
            yenta_id=yenta_id, lifecycle_group="CURRENT", page_number=0, page_size=100
        )

    # ===== TRANSACTION TERMINATION =====

    def request_termination(self, transaction_id: str) -> Dict[str, Any]:
        """Request termination for a transaction.

        Args:
            transaction_id: Transaction ID

        Returns:
            Termination request response data
        """
        endpoint = f"transactions/{transaction_id}/request-termination"
        return self.post(endpoint)

"""ReZEN Agents API client implementation."""

from datetime import date
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from .base_client import BaseClient
from .enums import Country, SortDirection, StateOrProvince


class AgentStatus(Enum):
    """Agent status enumeration."""

    CANDIDATE = "CANDIDATE"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    REJECTED = "REJECTED"
    RESURRECTING = "RESURRECTING"


class AgentSortField(Enum):
    """Sort fields for agent searches."""

    ID = "ID"
    FIRST_NAME = "FIRST_NAME"
    LAST_NAME = "LAST_NAME"
    EMAIL_ADDRESS = "EMAIL_ADDRESS"
    ACCOUNT_COUNTRY = "ACCOUNT_COUNTRY"


class AgentsClient(BaseClient):
    """
    Client for ReZEN Agents API endpoints.

    Provides access to agent-related functionality including:
    - Agent search and information retrieval
    - Sponsor tree and network management
    - Tax forms and payment details
    - Downline and front-line agent info
    - Agent plans and settings
    """

    def __init__(
        self, api_key: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        """
        Initialize the Agents API client.

        Args:
            api_key: ReZEN API key for authentication
            base_url: Base URL for the agents API. Defaults to yenta production URL
        """
        # Use the yenta base URL for agents API
        agents_base_url = base_url or "https://yenta.therealbrokerage.com/api/v1"
        super().__init__(api_key=api_key, base_url=agents_base_url)

    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get a single agent by ID.

        This method calls the Agents service directly using the `yenta` base
        URL and the endpoint path `agents/{id}`.

        Example endpoint:
            https://yenta.therealbrokerage.com/api/v1/agents/{agent_id}

        Args:
            agent_id: UUID of the agent to retrieve

        Returns:
            Agent record as a dictionary

        Raises:
            NotFoundError: If the agent does not exist
            AuthenticationError: If the API key is invalid
            RezenError: For other API errors
        """
        return self.get(f"agents/{agent_id}")

    def get_cap_info(self, agent_id: str) -> Dict[str, Any]:
        """
        Get agent's cap information.

        Args:
            agent_id: UUID of the agent

        Returns:
            Agent's cap information

        Raises:
            RezenError: If the API request fails
        """
        return self.get(f"agents/{agent_id}/cap-info")

    def agent_search(self, email: str = "", phone: str = "") -> Dict[str, Any]:
        """
        Search agents by email or phone - backward compatibility method.

        Args:
            email: Email address to search for
            phone: Phone number to search for

        Returns:
            Dict containing search results

        Raises:
            RezenError: If the API request fails
        """
        if email:
            return self.get_agents_by_email(email)
        elif phone:
            # Search by phone using the search_active_agents method
            return self.search_active_agents(phone=phone)
        else:
            return {"results": []}

    def get_agents_by_email(self, email_address: str) -> Dict[str, Any]:
        """
        Get agent(s) by email address.

        Args:
            email_address: Email address to search for

        Returns:
            Agent information matching the email address

        Raises:
            RezenError: If the API request fails
        """
        params = {"emailAddress": email_address}
        return self.get("agents", params=params)

    def get_sponsor_tree(self, agent_id: str) -> Dict[str, Any]:
        """
        Get agent's sponsor tree.

        Args:
            agent_id: UUID of the agent

        Returns:
            Agent's sponsor tree information

        Raises:
            RezenError: If the API request fails
        """
        return self.get(f"agents/{agent_id}/sponsor-tree")

    def get_profile_score(self, agent_id: str) -> Dict[str, Any]:
        """
        Get user's profile score.

        Args:
            agent_id: UUID of the agent

        Returns:
            Agent's profile score information

        Raises:
            RezenError: If the API request fails
        """
        return self.get(f"agents/{agent_id}/profile-score")

    def get_front_line_agents_info(self, agent_id: str) -> Dict[str, Any]:
        """
        Get front line agents basic information.

        Args:
            agent_id: UUID of the agent

        Returns:
            Front line agents information for the specified agent

        Raises:
            RezenError: If the API request fails
        """
        return self.get(f"agents/{agent_id}/front-line-agents-info")

    def get_down_line_agents(
        self,
        agent_id: str,
        tier: int,
        updated_at_from: Optional[date] = None,
        updated_at_to: Optional[date] = None,
        status_in: Optional[List[Union[AgentStatus, str]]] = None,
        page_number: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get agents in the network within a specific tier of the given agent.

        Args:
            agent_id: UUID of the agent
            tier: Tier level to retrieve
            updated_at_from: Start date for updatedAt filter (e.g., "2025-01-01")
            updated_at_to: End date for updatedAt filter (e.g., "2025-01-31")
            status_in: Filter agents by status, defaults to ACTIVE if not specified
            page_number: Page number for pagination (default: 0)
            page_size: Page size for pagination (default: 20)

        Returns:
            Downline agents information for the specified tier

        Raises:
            RezenError: If the API request fails
        """
        params: Dict[str, Any] = {}
        if updated_at_from:
            params["updatedAtFrom"] = updated_at_from.strftime("%Y-%m-%d")
        if updated_at_to:
            params["updatedAtTo"] = updated_at_to.strftime("%Y-%m-%d")
        if status_in:
            params["statusIn"] = [
                s.value if isinstance(s, AgentStatus) else s for s in status_in
            ]
        if page_number is not None:
            params["pageNumber"] = page_number
        if page_size is not None:
            params["pageSize"] = page_size

        return self.get(f"agents/{agent_id}/down-line/{tier}", params=params)

    def get_will_beneficiary_typed(self, agent_id: str) -> Dict[str, Any]:
        """
        Get agent's will beneficiary.

        Args:
            agent_id: UUID of the agent

        Returns:
            Agent's will beneficiary information

        Raises:
            RezenError: If the API request fails
        """
        return self.get(f"agents/{agent_id}/will-beneficiary-typed")

    def get_tax_forms_summary(self, agent_id: str) -> Dict[str, Any]:
        """
        Get tax forms summary for an agent.

        Args:
            agent_id: UUID of the agent

        Returns:
            Tax forms summary for the agent

        Raises:
            RezenError: If the API request fails
        """
        return self.get(f"agents/{agent_id}/tax-forms/summary")

    def get_tax_forms_lite(self, agent_id: str) -> Dict[str, Any]:
        """
        Get all tax forms (lite) for a given user.

        Args:
            agent_id: UUID of the agent

        Returns:
            All tax forms (lite) for the agent

        Raises:
            RezenError: If the API request fails
        """
        return self.get(f"agents/{agent_id}/tax-forms-lite")

    def get_tax_form_lite(self, agent_id: str, tax_form_id: str) -> Dict[str, Any]:
        """
        Get a specific tax form (lite) for a given user.

        Args:
            agent_id: UUID of the agent
            tax_form_id: ID of the tax form

        Returns:
            Specific tax form (lite) for the agent

        Raises:
            RezenError: If the API request fails
        """
        return self.get(f"agents/{agent_id}/tax-forms-lite/{tax_form_id}")

    def get_latest_personal_tax_form_lite(self, agent_id: str) -> Dict[str, Any]:
        """
        Get the latest personal tax form (including historical records) for an agent.
        Used for Shareworks awards assignment.

        Args:
            agent_id: UUID of the agent

        Returns:
            Latest personal tax form (lite) for the agent

        Raises:
            RezenError: If the API request fails
        """
        return self.get(f"agents/{agent_id}/tax-forms-lite/latest-personal")

    def search_payment_settings(
        self,
        agent_id: str,
        page_number: Optional[int] = None,
        page_size: Optional[int] = None,
        sort_direction: Optional[Union[SortDirection, str]] = None,
    ) -> Dict[str, Any]:
        """
        Search payment settings history with the given criteria.

        Args:
            agent_id: UUID of the agent
            page_number: Page number for pagination
            page_size: Page size for pagination
            sort_direction: Sort direction for results

        Returns:
            Payment settings history for the agent

        Raises:
            RezenError: If the API request fails
        """
        params: Dict[str, Any] = {}
        if page_number is not None:
            params["pageNumber"] = page_number
        if page_size is not None:
            params["pageSize"] = page_size
        if sort_direction:
            params["sortDirection"] = (
                sort_direction.value
                if isinstance(sort_direction, SortDirection)
                else sort_direction
            )

        return self.get(f"agents/{agent_id}/payment-settings/history", params=params)

    def get_payment_details(self, agent_id: str) -> Dict[str, Any]:
        """
        Get payment details for an agent.

        Args:
            agent_id: UUID of the agent

        Returns:
            Payment details for the agent

        Raises:
            RezenError: If the API request fails
        """
        return self.get(f"agents/{agent_id}/payment-details")

    def get_payment_details_payable_info(self, agent_id: str) -> Dict[str, Any]:
        """
        Get payment details payable info for an agent.

        Args:
            agent_id: UUID of the agent

        Returns:
            Payment details payable info for the agent

        Raises:
            RezenError: If the API request fails
        """
        return self.get(f"agents/{agent_id}/payment-details/payable-info")

    def get_network_size_by_tier(self, agent_id: str) -> Dict[str, Any]:
        """
        Get network size by tier for an agent.

        Args:
            agent_id: UUID of the agent

        Returns:
            Network size by tier information for the agent

        Raises:
            RezenError: If the API request fails
        """
        return self.get(f"agents/{agent_id}/network-size-by-tier")

    def get_masked_tax_forms_lite(self, agent_id: str) -> Dict[str, Any]:
        """
        Get masked tax forms (lite) for a given user.

        Args:
            agent_id: UUID of the agent

        Returns:
            Masked tax forms (lite) for the agent

        Raises:
            RezenError: If the API request fails
        """
        return self.get(f"agents/{agent_id}/masked-tax-forms-lite")

    def get_masked_payment_methods(self, agent_id: str) -> Dict[str, Any]:
        """
        Get all masked payment methods for a given user.

        Args:
            agent_id: UUID of the agent

        Returns:
            Masked payment methods for the agent

        Raises:
            RezenError: If the API request fails
        """
        return self.get(f"agents/{agent_id}/masked-payment-methods")

    def get_tipalti_url(self) -> Dict[str, Any]:
        """
        Get Tipalti sign up URL.

        Returns:
            Tipalti sign up URL information

        Raises:
            RezenError: If the API request fails
        """
        return self.get("agents/tipaltiUrl")

    def is_slug_available(self, slug: str) -> Dict[str, Any]:
        """
        Return whether or not a slug is available.

        Args:
            slug: Slug to check availability for

        Returns:
            Availability information for the slug

        Raises:
            RezenError: If the API request fails
        """
        return self.get(f"agents/slugs/{slug}/available")

    def search_active_agents(
        self,
        page_number: Optional[int] = None,
        page_size: Optional[int] = None,
        sort_direction: Optional[Union[SortDirection, str]] = None,
        sort_by: Optional[List[Union[AgentSortField, str]]] = None,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        non_reportable: Optional[List[bool]] = None,
        country: Optional[List[Union[Country, str]]] = None,
        state_or_province: Optional[List[Union[StateOrProvince, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Search for active agents.

        Args:
            page_number: Page number for pagination (default: 0)
            page_size: Page size for pagination (default: 20)
            sort_direction: Sort direction (default: ASC)
            sort_by: Fields to sort by (default: ["FIRST_NAME", "LAST_NAME"])
            name: Filter by agent name
            email: Filter by email address
            phone: Filter by phone number
            non_reportable: Filter by non-reportable status
            country: Filter by country
            state_or_province: Filter by state or province

        Returns:
            Search results for active agents

        Raises:
            RezenError: If the API request fails
        """
        params: Dict[str, Any] = {}
        if page_number is not None:
            params["pageNumber"] = page_number
        if page_size is not None:
            params["pageSize"] = page_size
        if sort_direction:
            params["sortDirection"] = (
                sort_direction.value
                if isinstance(sort_direction, SortDirection)
                else sort_direction
            )
        if sort_by:
            params["sortBy"] = [
                s.value if isinstance(s, AgentSortField) else s for s in sort_by
            ]
        if name:
            params["name"] = name
        if email:
            params["email"] = email
        if phone:
            params["phone"] = phone
        if non_reportable:
            params["nonReportable"] = non_reportable
        if country:
            params["country"] = [
                c.value if isinstance(c, Country) else c for c in country
            ]
        if state_or_province:
            params["stateOrProvince"] = [
                s.value if isinstance(s, StateOrProvince) else s
                for s in state_or_province
            ]

        return self.get("agents/search/active", params=params)

    def get_agents_referral_central_details(
        self,
        agent_ids: Optional[List[str]] = None,
        page_number: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get Agents' ReferralCentral Details.

        Args:
            agent_ids: List of agent UUIDs to filter by
            page_number: Page number for pagination (default: 0)
            page_size: Page size for pagination (default: 20)

        Returns:
            Agents' ReferralCentral details

        Raises:
            RezenError: If the API request fails
        """
        params: Dict[str, Any] = {}
        if agent_ids:
            params["agentIds"] = agent_ids
        if page_number is not None:
            params["pageNumber"] = page_number
        if page_size is not None:
            params["pageSize"] = page_size

        return self.get("agents/referral-central", params=params)

    def get_revenue_share_plan(self, plan_id: str) -> Dict[str, Any]:
        """
        Get revenue sharing plan by id.

        Args:
            plan_id: UUID of the revenue share plan

        Returns:
            Revenue sharing plan information

        Raises:
            RezenError: If the API request fails
        """
        return self.get(f"agents/plans/revenue_share/{plan_id}")

    def get_equity_purchase_plan(self, plan_id: str) -> Dict[str, Any]:
        """
        Get equity purchase plan by id.

        Args:
            plan_id: UUID of the equity purchase plan

        Returns:
            Equity purchase plan information

        Raises:
            RezenError: If the API request fails
        """
        return self.get(f"agents/plans/equity_purchase/{plan_id}")

    def get_equity_award_plan(self, plan_id: str) -> Dict[str, Any]:
        """
        Get equity award plan by id.

        Args:
            plan_id: UUID of the equity award plan

        Returns:
            Equity award plan information

        Raises:
            RezenError: If the API request fails
        """
        return self.get(f"agents/plans/equity_award/{plan_id}")

    def get_elite_equity_award_plan(self, plan_id: str) -> Dict[str, Any]:
        """
        Get elite equity award plan by id.

        Args:
            plan_id: UUID of the elite equity award plan

        Returns:
            Elite equity award plan information

        Raises:
            RezenError: If the API request fails
        """
        return self.get(f"agents/plans/elite_equity_award/{plan_id}")

    def get_commission_plan(self, plan_id: str) -> Dict[str, Any]:
        """
        Get commission plan by id.

        Args:
            plan_id: UUID of the commission plan

        Returns:
            Commission plan information

        Raises:
            RezenError: If the API request fails
        """
        return self.get(f"agents/plans/commission/{plan_id}")

    def get_official_commission_plan(self) -> Dict[str, Any]:
        """
        Get official commission plan.

        Returns:
            Official commission plan information

        Raises:
            RezenError: If the API request fails
        """
        return self.get("agents/plans/commission/official")

    def get_commission_plan_basic_info(self) -> Dict[str, Any]:
        """
        Get commission plan basic info.

        Returns:
            Commission plan basic information

        Raises:
            RezenError: If the API request fails
        """
        return self.get("agents/plans/commission/basic-info")

    def get_opcity_info(self) -> Dict[str, Any]:
        """
        Get OpCity information.

        Returns:
            OpCity information

        Raises:
            RezenError: If the API request fails
        """
        return self.get("agents/opcity")

    def get_me(self) -> Dict[str, Any]:
        """
        Get current user's agent information.

        Returns:
            Current user's agent information

        Raises:
            RezenError: If the API request fails
        """
        return self.get("agents/me")

    def get_loi_agent(self) -> Dict[str, Any]:
        """
        Get the agent we use as a stand-in for LOI agents in revShare trees.

        Returns:
            LOI agent information

        Raises:
            RezenError: If the API request fails
        """
        return self.get("agents/loiAgent")

    def get_license_images(self, license_id: str) -> Dict[str, Any]:
        """
        Get license images.

        Args:
            license_id: ID of the license

        Returns:
            License images information

        Raises:
            RezenError: If the API request fails
        """
        return self.get(f"agents/license/{license_id}/images")

    def get_agents_by_ids(self, agent_ids: List[str]) -> Dict[str, Any]:
        """
        Get agents by ids (limit 20).

        Args:
            agent_ids: List of agent UUIDs (maximum 20)

        Returns:
            Agents information for the specified IDs

        Raises:
            RezenError: If the API request fails
            ValidationError: If more than 20 agent IDs are provided
        """
        if len(agent_ids) > 20:
            from .exceptions import ValidationError

            raise ValidationError(
                "Maximum of 20 agent IDs allowed",
                status_code=400,
                response_data={"agent_ids_count": len(agent_ids)},
            )

        params = {"agentIds": agent_ids}
        return self.get("agents/ids", params=params)

    def get_comment_details(self, keymaker_ids: str) -> Dict[str, Any]:
        """
        Get comment details for keymaker IDs.

        Args:
            keymaker_ids: Comma-separated keymaker IDs

        Returns:
            Comment details for the specified keymaker IDs

        Raises:
            RezenError: If the API request fails
        """
        return self.get(f"agents/comment-details/{keymaker_ids}")

    def get_agents_by_anniversary(
        self, page_number: Optional[int] = None, page_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get agents by anniversary.

        Args:
            page_number: Page number for pagination
            page_size: Page size for pagination

        Returns:
            Agents information filtered by anniversary

        Raises:
            RezenError: If the API request fails
        """
        params: Dict[str, Any] = {}
        if page_number is not None:
            params["pageNumber"] = page_number
        if page_size is not None:
            params["pageSize"] = page_size

        return self.get("agents/by-anniversary", params=params)

    def get_active_agents(
        self, page_number: Optional[int] = None, page_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get active agents.

        Args:
            page_number: Page number for pagination
            page_size: Page size for pagination

        Returns:
            Active agents information

        Raises:
            RezenError: If the API request fails
        """
        params: Dict[str, Any] = {}
        if page_number is not None:
            params["pageNumber"] = page_number
        if page_size is not None:
            params["pageSize"] = page_size

        return self.get("agents/active", params=params)

    def get_active_agent_ids(self) -> Dict[str, Any]:
        """
        Get active agent IDs.

        Returns:
            List of active agent IDs

        Raises:
            RezenError: If the API request fails
        """
        return self.get("agents/active-agent-ids")

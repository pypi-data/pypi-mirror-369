"""ReZEN API data models and dataclasses.

This module contains all the dataclass definitions for request/response objects
used throughout the ReZEN API. These provide type safety and better developer
experience compared to using raw dictionaries.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID


# Enums for various status and type fields
class AgentStatus(Enum):
    """Agent status enumeration."""

    CANDIDATE = "CANDIDATE"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    REJECTED = "REJECTED"
    RESURRECTING = "RESURRECTING"


class TeamStatus(Enum):
    """Team status enumeration."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class TeamType(Enum):
    """Team type enumeration."""

    NORMAL = "NORMAL"
    PLATINUM = "PLATINUM"
    GROUP = "GROUP"
    DOMESTIC = "DOMESTIC"
    PRO = "PRO"


class Country(Enum):
    """Country enumeration."""

    UNITED_STATES = "UNITED_STATES"
    CANADA = "CANADA"


class StateOrProvince(Enum):
    """State or province enumeration."""

    ALABAMA = "ALABAMA"
    ALASKA = "ALASKA"
    ARIZONA = "ARIZONA"
    ARKANSAS = "ARKANSAS"
    CALIFORNIA = "CALIFORNIA"
    COLORADO = "COLORADO"
    CONNECTICUT = "CONNECTICUT"
    DELAWARE = "DELAWARE"
    FLORIDA = "FLORIDA"
    GEORGIA = "GEORGIA"
    HAWAII = "HAWAII"
    IDAHO = "IDAHO"
    ILLINOIS = "ILLINOIS"
    INDIANA = "INDIANA"
    IOWA = "IOWA"
    KANSAS = "KANSAS"
    KENTUCKY = "KENTUCKY"
    LOUISIANA = "LOUISIANA"
    MAINE = "MAINE"
    MARYLAND = "MARYLAND"
    MASSACHUSETTS = "MASSACHUSETTS"
    MICHIGAN = "MICHIGAN"
    MINNESOTA = "MINNESOTA"
    MISSISSIPPI = "MISSISSIPPI"
    MISSOURI = "MISSOURI"
    MONTANA = "MONTANA"
    NEBRASKA = "NEBRASKA"
    NEVADA = "NEVADA"
    NEW_HAMPSHIRE = "NEW_HAMPSHIRE"
    NEW_JERSEY = "NEW_JERSEY"
    NEW_MEXICO = "NEW_MEXICO"
    NEW_YORK = "NEW_YORK"
    NORTH_CAROLINA = "NORTH_CAROLINA"
    NORTH_DAKOTA = "NORTH_DAKOTA"
    OHIO = "OHIO"
    OKLAHOMA = "OKLAHOMA"
    OREGON = "OREGON"
    PENNSYLVANIA = "PENNSYLVANIA"
    RHODE_ISLAND = "RHODE_ISLAND"
    SOUTH_CAROLINA = "SOUTH_CAROLINA"
    SOUTH_DAKOTA = "SOUTH_DAKOTA"
    TENNESSEE = "TENNESSEE"
    TEXAS = "TEXAS"
    UTAH = "UTAH"
    VERMONT = "VERMONT"
    VIRGINIA = "VIRGINIA"
    WASHINGTON = "WASHINGTON"
    WEST_VIRGINIA = "WEST_VIRGINIA"
    WISCONSIN = "WISCONSIN"
    WYOMING = "WYOMING"
    # Canadian provinces
    ALBERTA = "ALBERTA"
    BRITISH_COLUMBIA = "BRITISH_COLUMBIA"
    MANITOBA = "MANITOBA"
    NEW_BRUNSWICK = "NEW_BRUNSWICK"
    NEWFOUNDLAND_AND_LABRADOR = "NEWFOUNDLAND_AND_LABRADOR"
    NORTHWEST_TERRITORIES = "NORTHWEST_TERRITORIES"
    NOVA_SCOTIA = "NOVA_SCOTIA"
    NUNAVUT = "NUNAVUT"
    ONTARIO = "ONTARIO"
    PRINCE_EDWARD_ISLAND = "PRINCE_EDWARD_ISLAND"
    QUEBEC = "QUEBEC"
    SASKATCHEWAN = "SASKATCHEWAN"
    YUKON = "YUKON"


class DealType(Enum):
    """Deal type enumeration."""

    SALE = "SALE"
    COMPENSATING = "COMPENSATING"
    NON_COMPENSATING = "NON_COMPENSATING"


class PropertyType(Enum):
    """Property type enumeration."""

    RESIDENTIAL = "RESIDENTIAL"
    COMMERCIAL = "COMMERCIAL"
    LAND = "LAND"
    RENTAL = "RENTAL"


class ParticipantRole(Enum):
    """Participant role enumeration."""

    REAL = "REAL"
    OTHER = "OTHER"


class RepresentationType(Enum):
    """Representation type enumeration."""

    BUYER = "BUYER"
    SELLER = "SELLER"
    DUAL = "DUAL"


class InvitationStatus(Enum):
    """Invitation status enumeration."""

    EMAILED = "EMAILED"
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"


class ChecklistItemStatus(Enum):
    """Checklist item status enumeration."""

    BEFORE_UPDATE = "BEFORE_UPDATE"
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"


class FeeType(Enum):
    """Fee type enumeration."""

    ADDITIONAL_COMMISSION = "ADDITIONAL_COMMISSION"
    BROKERAGE_FEE = "BROKERAGE_FEE"
    TRANSACTION_FEE = "TRANSACTION_FEE"
    REFERRAL_FEE = "REFERRAL_FEE"


class DayOfWeek(Enum):
    """Day of week enumeration."""

    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


# Base classes and common data structures
@dataclass
class Address:
    """Address data model.

    Args:
        street: Street address
        city: City name
        state: State or province
        zip: ZIP or postal code
        country: Country code
        street2: Secondary street address
        unit: Unit number
        valid: Whether address is valid
        one_line: Single line address representation
    """

    street: str
    city: str
    state: Union[StateOrProvince, str]
    zip: str
    country: Union[Country, str] = Country.UNITED_STATES
    street2: Optional[str] = None
    unit: Optional[str] = None
    valid: Optional[bool] = None
    one_line: Optional[str] = None


@dataclass
class Money:
    """Money amount data model.

    Args:
        amount: Monetary amount
        currency: Currency code (default: USD)
    """

    amount: Decimal
    currency: str = "USD"


@dataclass
class Commission:
    """Commission data model."""

    commission_amount: Money
    commission_percent: Optional[float] = None
    percent_enabled: bool = True
    negative_or_empty: bool = False


@dataclass
class TimeRange:
    """Time range data model."""

    start_time: str
    end_time: str


@dataclass
class DateRange:
    """Date range data model."""

    start_date: date
    end_date: date


@dataclass
class HourRange:
    """Hour range data model."""

    start_time: str
    end_time: str


@dataclass
class OfficeSchedule:
    """Office schedule data model."""

    day_of_week: DayOfWeek
    hour_range: HourRange


@dataclass
class Division:
    """Division data model."""

    id: UUID
    name: str
    logo_url: Optional[str] = None


@dataclass
class Availability:
    """Availability data model."""

    office_schedule: List[OfficeSchedule] = field(default_factory=list)
    out_of_office: List[DateRange] = field(default_factory=list)
    do_not_disturb: bool = False
    time_zone: str = "US/Eastern"
    available: bool = True


@dataclass
class MsdxVendor:
    """MSDX vendor data model."""

    subsidiary: str
    no: str
    error: Optional[str] = None
    synced_at: Optional[int] = None


# Agent-related data models
@dataclass
class Agent:
    """Agent data model."""

    id: UUID
    first_name: str
    last_name: str
    email_address: str
    agent_status: AgentStatus
    agent_account_country: Country
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    type: str = "AGENT"
    middle_name: Optional[str] = None
    company: Optional[str] = None
    full_name: Optional[str] = None
    avatar: Optional[str] = None
    sky_slope_id: Optional[UUID] = None
    sky_slope_public_id: Optional[str] = None
    key_maker_id: Optional[UUID] = None
    title: Optional[str] = None
    phone_number: Optional[str] = None
    about: Optional[str] = None
    birth_date: Optional[date] = None
    personal_website_url: Optional[str] = None
    facebook_url: Optional[str] = None
    youtube_url: Optional[str] = None
    twitter_url: Optional[str] = None
    instagram_url: Optional[str] = None
    clubhouse_url: Optional[str] = None
    linked_in_url: Optional[str] = None
    zillow_url: Optional[str] = None
    yelp_url: Optional[str] = None
    google_business_profile_url: Optional[str] = None
    join_date: Optional[date] = None
    anniversary_date: Optional[date] = None
    last_anniversary_date: Optional[date] = None
    next_anniversary_date: Optional[date] = None
    payment_instructions: Optional[str] = None
    qualia_connect_user_id: Optional[str] = None
    divisions: List[Division] = field(default_factory=list)
    administrative_area_ids: List[str] = field(default_factory=list)
    availability: Optional[Availability] = None
    opted_into_sms: bool = False
    voice_vector_disclaimer_accepted_at: Optional[int] = None
    leo_phone: Optional[str] = None
    msdx_vendors: List[MsdxVendor] = field(default_factory=list)


@dataclass
class AgentParticipantInfo:
    """Agent participant info data model."""

    agent_id: str
    role: ParticipantRole
    receives_invoice: bool
    id: str
    created_at: int
    one_real_impact_fund_config: Optional[Dict[str, Any]] = None
    op_city_referral: bool = False
    opted_in_for_ecp: bool = False
    yenta_id: Optional[UUID] = None


@dataclass
class OneRealImpactFundConfig:
    """One Real Impact Fund configuration data model."""

    amount: float
    percent: float
    percent_enabled: bool


@dataclass
class ProfileScore:
    """Profile score data model."""

    score: int
    max_score: int
    completion_percentage: float


# Team-related data models
@dataclass
class LeaderSplitConfig:
    """Leader split configuration data model."""

    enforce_splits: bool
    min_split_percent: float


@dataclass
class RealCapConfig:
    """Real cap configuration data model."""

    leader_cap: float
    excluded_member_caps: List[float] = field(default_factory=list)


@dataclass
class TeamConfig:
    """Team configuration data model."""

    id: UUID
    commission_plan_id: UUID
    country: Country
    team_type: TeamType
    name: str
    min_teammates: int
    max_teammates: int
    min_leaders: int
    max_leaders: int
    payment_details_visibility: str
    paid_at_closing: bool
    leader_split_config: LeaderSplitConfig
    real_cap_config: RealCapConfig
    cda_approver: str
    leader_overridable_properties: List[str]
    allowed_member_caps_for_permanent_plan: List[float]
    allowed_member_caps_for_temporary_plan: List[float]
    status: TeamStatus
    permitted_transaction_editors: str
    allowed_member_caps_for_new_member: List[float]
    minimum_allowed_member_for_new_member: float
    temporary_commission_plan_id: Optional[UUID] = None
    new_members_get_temp_plan_until: Optional[date] = None
    temp_plan_expires_on: Optional[date] = None


@dataclass
class FeeSplit:
    """Fee split data model."""

    fee_type: FeeType
    percent: float


@dataclass
class TeammateLeaderSplit:
    """Teammate leader split data model."""

    leader_id: UUID
    leader_split: float


@dataclass
class TeammateFeeSplit:
    """Teammate fee split data model."""

    leader_id: UUID
    fee_splits: List[FeeSplit]


@dataclass
class TeamAgent:
    """Team agent data model."""

    id: UUID
    agent: Agent
    flex_roles: List[str]
    roles: List[str]
    member_commission_split: float
    real_cap: float
    leader_split: float
    leader_fee_splits: List[FeeSplit]
    teammate_leader_splits: List[TeammateLeaderSplit]
    teammate_fee_splits: List[TeammateFeeSplit]
    invitation_status: InvitationStatus


@dataclass
class TeamInvitation:
    """Team invitation data model."""

    invitation_id: UUID
    team_id: UUID
    first_name: str
    last_name: str
    email_address: str
    cap_level: float
    invitation_created_by_agent_id: UUID
    status: InvitationStatus
    waive_fees: bool = False
    invitation_sent_at: Optional[int] = None
    coupon_code: Optional[str] = None
    email_sent_at: Optional[int] = None
    application_id: Optional[UUID] = None
    application_status: Optional[str] = None
    email_status: Optional[str] = None
    first_and_last_name: Optional[str] = None
    pending: bool = True


@dataclass
class GenericTeamApplication:
    """Generic team application data model."""

    id: UUID
    first_name: str
    last_name: str
    email_address: str
    cap_level: float
    status: InvitationStatus
    agent_id: UUID
    waive_fees: bool = False


@dataclass
class Team:
    """Team data model."""

    id: UUID
    config: TeamConfig
    name: str
    type: TeamType
    status: TeamStatus
    country: Country
    agents: List[TeamAgent]
    team_invitations: List[TeamInvitation]
    pending_generic_team_applications: List[GenericTeamApplication]
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    flex: bool = False
    instant_payment_eligible: bool = False
    paid_at_closing: bool = False
    member_commission_split: float = 0.0
    max_member_commission_split: float = 0.0
    commission_document_approver: str = "TEAM_LEADER"
    permitted_transaction_editors: str = "TEAM_LEADER"


# Transaction-related data models
@dataclass
class Participant:
    """Participant data model."""

    id: str
    created_at: int
    role: ParticipantRole
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    vendor_directory_id: Optional[UUID] = None


@dataclass
class Buyer(Participant):
    """Buyer data model."""

    pass


@dataclass
class Seller(Participant):
    """Seller data model."""

    pass


@dataclass
class ExternalParticipantInfo(Participant):
    """External participant info data model."""

    assistant_email_address: Optional[str] = None
    w9_path: Optional[str] = None
    receives_invoice: bool = False
    ein: Optional[str] = None


@dataclass
class AgentsInfo:
    """Agents info data model."""

    owner_agent: List[AgentParticipantInfo]
    representation_type: RepresentationType
    co_agents: List[AgentParticipantInfo] = field(default_factory=list)
    office_ids: List[str] = field(default_factory=list)
    office_id: Optional[str] = None
    team_id: Optional[UUID] = None


@dataclass
class ReferralInfo:
    """Referral info data model."""

    have_to_pay_referral_fee: bool
    agent_participant_infos: List[AgentParticipantInfo] = field(default_factory=list)
    external_participant_infos: List[ExternalParticipantInfo] = field(
        default_factory=list
    )
    all_referral_participant_info: List[Participant] = field(default_factory=list)


@dataclass
class CommissionSplitInfo:
    """Commission split info data model."""

    participant_id: str
    commission: Commission


@dataclass
class AdditionalFeeInfo:
    """Additional fee info data model."""

    amount: Money
    description: str
    fee_type: FeeType
    participant_id: str
    recipient_type: str
    added_by_system: bool = False


@dataclass
class AdditionalFeesInfo:
    """Additional fees info data model."""

    additional_fees_participant_infos: List[AdditionalFeeInfo] = field(
        default_factory=list
    )


@dataclass
class CommissionPayerInfo(Participant):
    """Commission payer info data model."""

    w9_path: Optional[str] = None
    receives_invoice: bool = False
    participant_id: Optional[str] = None
    ein: Optional[str] = None


@dataclass
class TitleContactInfo:
    """Title contact info data model."""

    first_name: str
    last_name: str
    email_address: str
    phone_number: str
    address: Address


@dataclass
class ContractInfo:
    """Contract info data model."""

    contract_file_name: str
    contract_s3_path: str


@dataclass
class TitleInfo:
    """Title info data model."""

    use_real_title: bool
    manual_order_placed: bool = False
    contract: Optional[ContractInfo] = None


@dataclass
class DoubleEnderInfo:
    """Double ender info data model."""

    double_ender_agent_id: UUID
    double_ender_tx_id: UUID


@dataclass
class MortgageInfo:
    """Mortgage info data model."""

    loan_id: UUID
    using_real_mortgage: bool


@dataclass
class Transaction:
    """Transaction data model."""

    id: str
    address: Address
    buyers: List[Buyer]
    sellers: List[Seller]
    agents_info: AgentsInfo
    referral_info: ReferralInfo
    deal_type: DealType
    property_type: PropertyType
    sale_price: Money
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    commission_splits_info: List[CommissionSplitInfo] = field(default_factory=list)
    additional_fees_info: Optional[AdditionalFeesInfo] = None
    listing_commission: Optional[Commission] = None
    sale_commission: Optional[Commission] = None
    gross_commission: Optional[Commission] = None
    year_built: Optional[int] = None
    mls_number: Optional[str] = None
    escrow_number: Optional[str] = None
    checklist_id: Optional[str] = None
    journey_id: Optional[str] = None
    personal_deal: bool = False
    represented_by_agent: bool = True
    add_opcity: bool = False
    acceptance_date: Optional[date] = None
    estimated_closing_date: Optional[date] = None
    firm_date: Optional[date] = None
    financing_conditions_expiration_date: Optional[date] = None
    property_inspection_expiration_date: Optional[date] = None
    sale_of_buyers_property_expiration_date: Optional[date] = None
    condo_documents_expiration_date: Optional[date] = None
    other_conditions_expiration_date: Optional[date] = None
    all_participants: List[Participant] = field(default_factory=list)
    all_commission_recipient: List[Participant] = field(default_factory=list)
    commission_payer_info: Optional[CommissionPayerInfo] = None
    other_participants: List[ExternalParticipantInfo] = field(default_factory=list)
    listing_date: Optional[date] = None
    listing_expiration_date: Optional[date] = None
    requires_installments: bool = False
    builder_type: str = "TRANSACTION"
    built_from_transaction_id: Optional[str] = None
    title_info: Optional[TitleInfo] = None
    zero_commission_deal: bool = False
    double_ender_info: Optional[DoubleEnderInfo] = None
    transaction_owner_id: Optional[UUID] = None
    mortgage_info: Optional[MortgageInfo] = None
    transaction_coordinators: List[UUID] = field(default_factory=list)
    possible_payable_participants: List[Participant] = field(default_factory=list)


# Checklist-related data models
@dataclass
class ChecklistLabel:
    """Checklist label data model."""

    id: UUID
    created_at: int
    text: str


@dataclass
class DocumentVersion:
    """Document version data model."""

    id: UUID
    created_at: int
    name: str
    description: str
    number: int
    uploader_id: UUID
    path: str
    document_version_definition_id: UUID


@dataclass
class ChecklistDocument:
    """Checklist document data model."""

    id: UUID
    created_at: int
    name: str
    description: str
    versions: List[DocumentVersion]
    current_version: DocumentVersion
    document_definition_id: UUID


@dataclass
class EventSubscription:
    """Event subscription data model."""

    event: str
    domain_event_name: str
    checklist_definition_id: UUID
    item_definition_id: UUID


@dataclass
class DefinedConditionPair:
    """Defined condition pair data model."""

    event_type: str
    event_subscription: EventSubscription
    condition_name: str


@dataclass
class ScriptConditionPair:
    """Script condition pair data model."""

    event_type: str
    event_subscription: EventSubscription
    script_condition: str


@dataclass
class ConditionSets:
    """Condition sets data model."""

    defined_condition_pairs: List[DefinedConditionPair] = field(default_factory=list)
    script_condition_pairs: List[ScriptConditionPair] = field(default_factory=list)


@dataclass
class ChecklistTrigger:
    """Checklist trigger data model."""

    id: UUID
    created_at: int
    trigger_definition_id: UUID
    condition_sets: ConditionSets
    action_name: str
    fired: bool


@dataclass
class FileReference:
    """File reference data model."""

    file_id: UUID


@dataclass
class TemplateReference:
    """Template reference data model."""

    dropbox_id: UUID
    file_id: UUID


@dataclass
class FileReferences:
    """File references data model."""

    references: List[FileReference] = field(default_factory=list)


@dataclass
class TemplateReferences:
    """Template references data model."""

    references: List[TemplateReference] = field(default_factory=list)


@dataclass
class ChecklistItem:
    """Checklist item data model."""

    id: UUID
    created_at: int
    name: str
    checklist_id: UUID
    updated_at: int
    description: str
    item_definition_id: UUID
    position: int
    due_date: date
    required: bool
    urgent: bool
    labels: List[ChecklistLabel]
    documents: List[ChecklistDocument]
    triggers: List[ChecklistTrigger]
    assignee: UUID
    assigned_at: int
    assignor: UUID
    marked_completed_by: UUID
    completed_at: int
    system_generated: bool
    file_references: FileReferences
    template_references: TemplateReferences
    status: ChecklistItemStatus
    required_for: str
    required_for_v2: List[str]
    hidden: bool
    skipped: bool
    data: Dict[str, Any]
    read_only: bool
    complete: bool


# Authentication and MFA data models
@dataclass
class LoginRequest:
    """Login request data model."""

    email: str
    password: str


@dataclass
class JwtAuthenticationResponse:
    """JWT authentication response data model."""

    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None


@dataclass
class MfaVerificationRequest:
    """MFA verification request data model."""

    email: str
    mfa_code: str
    temporary_token: str


@dataclass
class EnableMfaRequest:
    """Enable MFA request data model."""

    mfa_code: str


@dataclass
class UpdateEmailRequest:
    """Update email request data model."""

    email: str


@dataclass
class ResetPasswordRequest:
    """Reset password request data model."""

    email: str


@dataclass
class ResetPasswordResponse:
    """Reset password response data model."""

    message: str
    success: bool


@dataclass
class UpdateExistingPasswordRequest:
    """Update existing password request data model."""

    current_password: str
    new_password: str


@dataclass
class PasswordUpdateRequest:
    """Password update request data model."""

    new_password: str
    token: str


# API Key data models
@dataclass
class ApiKeyResponse:
    """API key response data model."""

    id: UUID
    name: str
    key_prefix: str
    created_at: datetime
    last_used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


@dataclass
class GenerateApiKeyRequest:
    """Generate API key request data model."""

    name: str
    expires_at: Optional[datetime] = None


@dataclass
class RevokeApiKeyRequest:
    """Revoke API key request data model."""

    key_id: UUID


# Directory data models
@dataclass
class DirectoryEntry:
    """Directory entry data model."""

    id: UUID
    name: str
    email: str
    phone: str
    company: str
    role: str
    type: str
    created_at: datetime
    updated_at: datetime


@dataclass
class Person(DirectoryEntry):
    """Person directory entry data model."""

    first_name: str
    last_name: str


@dataclass
class Vendor(DirectoryEntry):
    """Vendor directory entry data model."""

    business_name: str
    services: List[str] = field(default_factory=list)


# Response wrapper data models
@dataclass
class PagedResponse:
    """Paged response data model."""

    page_number: int
    page_size: int
    has_next: bool
    total_count: int
    results: List[Any] = field(default_factory=list)


@dataclass
class ApiResponse:
    """Generic API response data model."""

    status: bool
    message: str
    data: Optional[Any] = None


@dataclass
class ErrorResponse:
    """Error response data model."""

    error: str
    message: str
    status_code: int
    timestamp: datetime

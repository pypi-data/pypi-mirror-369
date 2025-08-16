"""
EasySwitch - FedaPay Specific Types and Data Structures.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from easyswitch.types import (
    Currency, CustomerInfo, PaginationMeta, 
    Provider, TransactionDetail, TransactionStatus
)
from easyswitch.utils import parse_phone


####
##      FEDAPAY TRANSACTION UPDATE DETAIL
#####
@dataclass
class FedapayTransactionUpdate:
    """ Standardized FedaPay's transaction update structure. """
    amount: Optional[float] = None
    status: Optional[TransactionStatus] = None
    description: Optional[str] = None
    callback_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


####
##      FEDAPAY CUSTOMER UPDATE DETAIL
#####
@dataclass
class FedapayCustomerUpdate:
    """Standardized FedaPay's customer update structure."""
    firstname: str
    lastname: str
    email: Optional[str] = None
    phone_number: Optional[str] = None

    def to_payload(self) -> Dict[str, Any]:
        """Prépare le payload pour l'API FedaPay en ne gardant que les champs renseignés."""
        payload = {}
        
        payload["firstname"] = self.firstname
        payload["lastname"] = self.lastname
        
        if self.email is not None:
            payload["email"] = self.email
        
        # Parse the phone number using the utility function
        parsed_phone = parse_phone(
            self.phone_number,
            raise_exception=True
        )
        
        payload["phone_number"] = {
            "number": parsed_phone.get("national_number"),
            "country": parsed_phone.get("country_alpha2")
        } if parsed_phone else {}
        
        return payload


####
##      CURRENCY RESPONSE
#####
@dataclass
class CurrencyResponse:
    """Standardized Currency response structure."""

    currency_id: str
    name: str
    provider: Provider
    iso: Currency
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    modes: List[str] = field(default_factory=list)
    raw_response: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Ensure modes are unique and always a list."""
        if not isinstance(self.modes, list):
            self.modes = list(self.modes) if self.modes is not None else []
        self.modes = list(set(self.modes))
    

####
##      CUSTOMER SEARCH RESPONSE
#####
@dataclass
class CustomerSearchResponse:
    customers: List[CustomerInfo]
    meta: PaginationMeta


####
##      TRANSACTION SEARCH RESPONSE
#####
@dataclass
class TransactionSearchResponse:
    transactions: List[TransactionDetail]
    meta: PaginationMeta


#####
##      PAYMENT LINK RESPONSE
#####
@dataclass
class PaymentLinkResponse:
    """ Standardized Payment Link response structure."""
    token: str
    url: str
    raw_response: Optional[Dict[str, Any]] = None


#####
##      BALANCE DETAIL
#####
@dataclass
class BalanceDetail:
    id: int
    amount: float
    mode: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    provider: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_response: Optional[Dict[str, Any]] = None


#####
##      LOG DETAIL
#####
@dataclass
class LogDetail:
    """Standardized log detail structure."""

    id: int
    method: str
    url: str
    status: str
    ip_address: str
    version: str
    provider: Provider
    source: str
    query: Optional[Dict[str, Any]] = None
    body: Optional[str] = None
    response: Optional[str] = None
    account_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_response: Dict[str, Any] = field(default_factory=dict)


####
##      ALL LOGS RESPONSE
#####
@dataclass
class LogsResponse:
    """Standardized response structure for logs."""
    logs: List[LogDetail]
    meta: PaginationMeta


#####
##      WEBHOOK DETAIL
#####
@dataclass
class WebhookDetail:
    """Standardized webhook detail structure."""

    id: int
    url: str
    provider: Provider
    enabled: bool
    ssl_verify: bool
    disable_on_error: bool
    account_id: int
    http_headers: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_response: Dict[str, Any] = field(default_factory=dict)


####
##      ALL WEBHOOK RESPONSE
#####
@dataclass
class WebhooksResponse:
    """Standardized response structure for webhooks."""
    webhooks: List[WebhookDetail]
    meta: PaginationMeta

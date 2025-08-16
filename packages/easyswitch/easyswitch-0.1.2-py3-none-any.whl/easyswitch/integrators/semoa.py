
"""
EasySwitch - SEMOA Integrator
"""

from typing import Any, ClassVar, Dict, List, Optional, Union

from easyswitch.adapters.base import BaseAdapter
from easyswitch.conf.config import Config
from easyswitch.exceptions import (AuthenticationError, PaymentError,
                                   TransactionNotFoundError,
                                   UnsupportedOperationError)
from easyswitch.types import (Currency, CustomerInfo, PaymentResponse,
                              Provider, TransactionDetail, TransactionStatus,
                              TransactionType)
from easyswitch.utils.http import HTTPClient


####
##      SEMOA INTEGRATOR
#####
class SemoaAdapter(BaseAdapter):
    """Semoa Integrator for EasySwitch SDK."""

    SANDBOX_URL: str = "https://sandbox.semoa-payments.com/api/"

    PRODUCTION_URL: str = "https://sandbox.semoa-payments.com/api/"

    SUPPORTED_CURRENCIES: ClassVar[List[Currency]] = [
        Currency.XOF,
        Currency.XAF,
        Currency.EUR,
        Currency.USD
    ]

    MIN_AMOUNT: ClassVar[Dict[Currency, float]] = {
        Currency.XOF: 100.0,
        Currency.XAF: 100.0,
        Currency.EUR: 1.0,
        Currency.USD: 1.0
    }

    MAX_AMOUNT: ClassVar[Dict[Currency, float]] = {     # Currently unknown
        Currency.XOF: 1000000.0,
        Currency.XAF: 1000000.0,
        Currency.EUR: 10000.0,
        Currency.USD: 10000.0
    }

    def _validate_credentials(self) -> bool:
        """ Validate the credentials for CinetPay. """
        
        return all(
            self.config.api_key,                        # USED AS API KEY
            self.config.extra.get('client_id'),                      # USED AS CLIENT ID
            self.config.extra.get('client_secret'),     # USED AS API SECRET
            self.config.extra.get('username'),          # USED AS USERNAME
            self.config.extra.get('password'),          # USED AS PASSWORD
            self.config.callback_url                    # USED AS CALLBACK URL
        )
    
    def get_credentials(self):
        """Get the credentials for Semoa."""
        return {
            "username": self.config.extra.get('username'),
            "password": self.config.extra.get('password'),
            "client_id": self.config.extra.get('client_id'),
            "client_secret": self.config.extra.get('client_secret'),
        }
    
    def get_headers(self, authorization=False):
        """Get the headers for Semoa."""

        headers = {
            'Content-Type':'application/json'
        }
        if authorization:
            headers['Authorization'] = f'Bearer {self.config.token}'
        return headers
    
    async def authenticate(self):
        """Authenticate Our App and get Semoa AUTH_TOKEN."""

        # Send Authentication POST request to Semoa API
        async with self.get_client() as client:
            response = await client.post(
                endpoint = "auth",
                json_data = self.get_credentials(),
                headers = {
                    "Content-Type": "application/json"
                }
            )
            # Check if the response is successful
            if response.status == 200:
                # Extract the token from the response
                self.config.token = response.data.get("access_token")
                return True
            else:
                raise AuthenticationError(
                    message="Authentication failed",
                    status_code = response.status,
                    raw_response = response.data
                )
            
    def format_transaction(self, data):
        """
        Format the standard transaction data to Semoa specific Order format.
        Args:
            data (Dict): The transaction data to format.
        Returns:
            Dict: The formatted transaction data.
        """

        # Validate the transaction data
        self.validate_transaction(data)

        return {
            "amount": data.amount,
            "currency": data.currency,
            "description": data.reason,
            "client": {
                "last_name": data.customer.last_name or "Doe",
                "first_name": data.customer.first_name or "John",
                "phone": data.customer.phone_number.replace(" ", "")
            },
            "metadata": data.metadata,
            "callback_url": data.callback_url or self.config.callback_url
        }

    async def send_payment(self, transaction) -> PaymentResponse:
        """
        Send a payment request to Semoa.
        """

        # First we need to format the trasaction
        order = self.format_transaction(transaction)

        # Then send the payment request
        response = await self.client.post(
            endpoint = "orders",
            json_data = order,
            headers = self.get_headers(authorization=True)
        )
        # Check if the response is successful
        if response.status_code in range(200, 300):
            # Extract the payment link from the response
            payment_link = response.data.get("bill_url")
            transaction_id = response.data.get("orderNum")

            # Create a PaymentResponse object
            payment_response = PaymentResponse(
                transaction_id = transaction_id,
                provider = self.provider_name(),
                status = TransactionStatus.PENDING,
                amount = transaction.amount,
                currency = transaction.currency,
                created_at = response.data.get("created_at"),
                expires_at = response.data.get("expires_at"),
                reference = response.data.get("reference"),
                payment_link = payment_link,
                customer = transaction.customer,
                raw_response = response.data,
                metadata = transaction.metadata
            )
            return payment_response
        
        # If the response is not successful, raise an API error
        raise PaymentError(
            message="Payment request failed",
            status_code = response.status_code,
            raw_response = response.data
        )
    
    async def check_status(self, transaction_id: str) -> TransactionStatus:
        """
        Check the status of a transaction.
        Args:
            transaction_id (str): The transaction ID to check.
        Returns:
            TransactionStatus: The status of the transaction.
        """
        # Send a GET request to check the status of the transaction
        response = self.client.get(
            endpoint = f"orders/{transaction_id}",
            headers = self.get_headers(authorization=True)
        )
        # Check if the response is successful
        if response.status_code in range(200, 300):
            # Extract the status from the response
            status = response.data.get("status")
            return TransactionStatus(status)
        # If the response is not successful, raise a TransactionNotFoundError
        raise TransactionNotFoundError(
            message="Transaction not found",
            status_code = response.status_code,
            raw_response = response.data
        )
    
    async def cancel_transaction(self, transaction_id: str) -> bool:
        """
        Cancel a transaction.
        Args:
            transaction_id (str): The transaction ID to cancel.
        Returns:
            bool: True if the transaction was cancelled, False otherwise.
        """
        # Send a DELETE request to cancel the transaction
        response = self.client.delete(
            endpoint = f"orders/{transaction_id}",
            headers = self.get_headers(authorization=True)
        )
        # Check if the response is successful
        return super().send_payment(transaction)
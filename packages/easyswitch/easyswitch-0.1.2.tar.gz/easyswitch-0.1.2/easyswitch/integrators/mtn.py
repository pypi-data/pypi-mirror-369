"""
EasySwitch - Intégrateur pour MTN Mobile Money
"""
import base64
import hashlib
import hmac
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from easyswitch.adapters.base import BaseAdapter
from easyswitch.conf.config import Config
from easyswitch.exceptions import (APIError, AuthenticationError,
                                   TransactionNotFoundError,
                                   UnsupportedOperationError)
from easyswitch.types import (Currency, CustomerInfo, PaymentResponse,
                              Provider, TransactionStatus, TransactionType)
from easyswitch.utils.http import HTTPClient


class MTNIntegrator(BaseAdapter):
    """Intégrateur pour MTN Mobile Money API."""
    
    def __init__(self, config: Config):
        """
        Initialise l'intégrateur MTN.
        
        Args:
            config: Configuration du SDK
        """
        super().__init__(config)
        self.api_key = config.mtn_api_key
        self.api_secret = config.mtn_api_secret
        self.app_id = config.mtn_app_id
        self.callback_url = config.mtn_callback_url
        
        # Token d'authentification et sa date d'expiration
        self._auth_token = None
        self._token_expires_at = None
        
        # Initialiser le client HTTP
        self.http_client = HTTPClient(
            base_url=config.get_api_url("mtn"),
            default_headers={
                "Ocp-Apim-Subscription-Key": self.api_key,
                "X-Reference-Id": self.app_id or str(uuid.uuid4())
            },
            timeout=config.timeout,
            debug=config.debug
        )
    
    async def _ensure_auth_token(self) -> str:
        """
        S'assure que nous avons un token d'authentification valide.
        
        Returns:
            str: Token d'authentification valide
        """
        now = datetime.now()
        
        # Si le token n'existe pas ou est expiré, en demander un nouveau
        if not self._auth_token or not self._token_expires_at or self._token_expires_at <= now:
            try:
                # Générer une paire de clés éphémères pour l'authentification
                subscription_key = self.api_key
                
                # Obtenir le token d'authentification
                response = await self.http_client.post(
                    "collection/token/",
                    json_data={
                        "grant_type": "client_credentials"
                    },
                    headers={
                        "Authorization": f"Basic {base64.b64encode(f'{self.app_id}:{self.api_secret}'.encode()).decode()}"
                    }
                )
                
                if "access_token" not in response:
                    raise AuthenticationError("Token d'authentification MTN non reçu")
                
                self._auth_token = response["access_token"]
                # Token valide pendant 1h (3600 sec)
                expires_in = int(response.get("expires_in", 3600))
                self._token_expires_at = now + timedelta(seconds=expires_in - 60)  # 60 sec de marge
                
            except Exception as e:
                raise AuthenticationError(f"Erreur d'authentification MTN: {str(e)}")
        
        return self._auth_token
    
    async def send_payment(
        self,
        amount: float,
        phone_number: str,
        currency: Currency,
        reference: str,
        customer_info: Optional[CustomerInfo] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentResponse:
        """
        Envoie une demande de paiement MTN Mobile Money.
        
        Args:
            amount: Montant à payer
            phone_number: Numéro de téléphone du client (format international)
            currency: Devise du paiement
            reference: Référence unique pour le paiement
            customer_info: Informations supplémentaires sur le client
            metadata: Métadonnées personnalisées
            
        Returns:
            PaymentResponse: Réponse de la demande de paiement
        """
        # S'assurer d'avoir un token valide
        auth_token = await self._ensure_auth_token()
        
        # Formater le numéro de téléphone (retirer +, espaces, etc.)
        clean_phone = phone_number.replace("+", "").replace(" ", "")
        
        # Générer un UUID pour la transaction
        transaction_id = str(uuid.uuid4())
        external_id = reference or str(uuid.uuid4())
        
        # Préparer la requête
        payload = {
            "amount": str(amount),
            "currency": currency.value,
            "externalId": external_id,
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": clean_phone
            },
            "payerMessage": "Paiement via EasySwitch",
            "payeeNote": "Paiement via EasySwitch"
        }
        
        # Ajouter les métadonnées si fournies
        if metadata:
            payload["metadata"] = metadata
        
        try:
            # Effectuer la requête de paiement
            response = await self.http_client.post(
                f"collection/v1_0/requesttopay",
                json_data=payload,
                headers={
                    "Authorization": f"Bearer {auth_token}",
                    "X-Reference-Id": transaction_id,
                    "X-Callback-Url": self.callback_url
                }
            )
            
            # MTN renvoie généralement un 202 Accepted sans corps de réponse
            # Il faut vérifier le statut séparément
            payment_response = PaymentResponse(
                transaction_id=transaction_id,
                provider=Provider.MTN,
                status=TransactionStatus.PENDING,
                amount=amount,
                currency=currency,
                reference=external_id,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(minutes=10),
                customer=customer_info,
                metadata=metadata or {},
                raw_response=response if isinstance(response, dict) else {}
            )
            
            return payment_response
            
        except APIError as e:
            # Gérer les erreurs spécifiques à MTN
            raise APIError(
                message=f"Erreur MTN lors de la demande de paiement: {str(e)}",
                status_code=e.status_code,
                provider="mtn",
                raw_response=e.raw_response
            )
    
    async def check_status(self, transaction_id: str) -> TransactionStatus:
        """
        Vérifie le statut d'une transaction MTN.
        
        Args:
            transaction_id: Identifiant de la transaction
            
        Returns:
            TransactionStatus: Statut actuel de la transaction
        """
        # S'assurer d'avoir un token valide
        auth_token = await self._ensure_auth_token()
        
        try:
            # Effectuer la requête de vérification
            response = await self.http_client.get(
                f"collection/v1_0/requesttopay/{transaction_id}",
                headers={
                    "Authorization": f"Bearer {auth_token}"
                }
            )
            
            # Mapper le statut MTN à notre enum TransactionStatus
            mtn_status = response.get("status", "").lower()
            status_mapping = {
                "pending": TransactionStatus.PENDING,
                "successful": TransactionStatus.SUCCESSFUL,
                "failed": TransactionStatus.FAILED,
                "cancelled": TransactionStatus.CANCELLED,
                "ongoing": TransactionStatus.PROCESSING,
                "rejected": TransactionStatus.FAILED,
                "timeout": TransactionStatus.EXPIRED
            }
            
            return status_mapping.get(mtn_status, TransactionStatus.PENDING)
            
        except APIError as e:
            if e.status_code == 404:
                raise TransactionNotFoundError(f"Transaction MTN non trouvée: {transaction_id}")
            
            raise APIError(
                message=f"Erreur MTN lors de la vérification du statut: {str(e)}",
                status_code=e.status_code,
                provider="mtn",
                raw_response=e.raw_response
            )
    
    async def cancel_transaction(self, transaction_id: str) -> bool:
        """
        Annule une transaction MTN si possible.
        
        Args:
            transaction_id: Identifiant de la transaction
            
        Returns:
            bool: True si l'annulation a réussi, False sinon
        """
        # MTN ne supporte pas l'annulation via API
        raise UnsupportedOperationError("L'annulation de transaction n'est pas prise en charge par MTN Mobile Money")
    
    async def refund(
        self,
        transaction_id: str,
        amount: Optional[float] = None,
        reason: Optional[str] = None
    ) -> PaymentResponse:
        """
        Effectue un remboursement pour une transaction MTN.
        
        Args:
            transaction_id: Identifiant de la transaction
            amount: Montant à rembourser (si None, rembourse le montant total)
            reason: Raison du remboursement
            
        Returns:
            PaymentResponse: Réponse de la demande de remboursement
        """
        # S'assurer d'avoir un token valide
        auth_token = await self._ensure_auth_token()
        
        # Vérifier d'abord le statut de la transaction initiale
        status = await self.check_status(transaction_id)
        if status != TransactionStatus.SUCCESSFUL:
            raise APIError(
                message=f"Impossible de rembourser une transaction non réussie (statut: {status})",
                provider="mtn"
            )
        
        # Récupérer les détails de la transaction pour connaître le montant initial
        try:
            response = await self.http_client.get(
                f"collection/v1_0/requesttopay/{transaction_id}",
                headers={
                    "Authorization": f"Bearer {auth_token}"
                }
            )
            
            original_amount = float(response.get("amount", "0"))
            currency = Currency(response.get("currency", "XOF"))
            payer_id = response.get("payer", {}).get("partyId")
            
            if not amount:
                amount = original_amount
            
            if amount > original_amount:
                raise ValueError(f"Le montant du remboursement ({amount}) ne peut pas dépasser le montant initial ({original_amount})")
            
            # Créer un ID pour le remboursement
            refund_id = str(uuid.uuid4())
            
            # Préparer la requête de remboursement
            payload = {
                "amount": str(amount),
                "currency": currency.value,
                "externalId": f"refund-{transaction_id}",
                "payee": {
                    "partyIdType": "MSISDN",
                    "partyId": payer_id
                },
                "payerMessage": reason or "Remboursement via EasySwitch",
                "payeeNote": reason or "Remboursement via EasySwitch"
            }
            
            # Effectuer la requête de remboursement
            await self.http_client.post(
                "disbursement/v1_0/transfer",
                json_data=payload,
                headers={
                    "Authorization": f"Bearer {auth_token}",
                    "X-Reference-Id": refund_id,
                    "X-Callback-Url": self.callback_url
                }
            )
            
            return PaymentResponse(
                transaction_id=refund_id,
                provider=Provider.MTN,
                status=TransactionStatus.PENDING,
                amount=amount,
                currency=currency,
                reference=f"refund-{transaction_id}",
                created_at=datetime.now(),
                raw_response=response
            )
            
        except APIError as e:
            if e.status_code == 404:
                raise TransactionNotFoundError(f"Transaction MTN non trouvée: {transaction_id}")
            
            raise APIError(
                message=f"Erreur MTN lors du remboursement: {str(e)}",
                status_code=e.status_code,
                provider="mtn",
                raw_response=e.raw_response
            )
    
    async def validate_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> bool:
        """
        Valide un webhook entrant de MTN.
        
        Args:
            payload: Contenu du webhook
            headers: En-têtes de la requête
            
        Returns:
            bool: True si le webhook est valide, False sinon
        """
        # MTN utilise généralement une validation basée sur le token
        notification_token = headers.get("X-Notification-Token")
        if not notification_token:
            return False
        
        # Vérifier la signature (exemple simplifié)
        expected_signature = hmac.new(
            self.api_secret.encode(),
            json.dumps(payload).encode(),
            hashlib.sha256
        ).hexdigest()
        
        return notification_token == expected_signature
    
    async def parse_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Analyse un webhook MTN et le convertit en format standardisé.
        
        Args:
            payload: Contenu du webhook
            headers: En-têtes de la requête
            
        Returns:
            Dict[str, Any]: Données du webhook standardisées
        """
        # Vérifier que le webhook est valide
        if not await self.validate_webhook(payload, headers):
            raise ValueError("Webhook MTN invalide")
        
        # Extraire les données importantes
        transaction_id = payload.get("referenceId")
        status = payload.get("status", "").lower()
        
        # Mapper le statut MTN à notre enum TransactionStatus
        status_mapping = {
            "successful": TransactionStatus.SUCCESSFUL,
            "failed": TransactionStatus.FAILED,
            "rejected": TransactionStatus.FAILED,
            "timeout": TransactionStatus.EXPIRED,
            "pending": TransactionStatus.PENDING,
            "ongoing": TransactionStatus.PROCESSING
        }
        
        transaction_status = status_mapping.get(status, TransactionStatus.PENDING)
        
        return {
            "transaction_id": transaction_id,
            "provider": Provider.MTN,
            "status": transaction_status,
            "raw_data": payload
        }
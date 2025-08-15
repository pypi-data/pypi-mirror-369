import base64

from django.http import HttpResponse, HttpResponseBadRequest

from payments import PaymentStatus, RedirectNeeded
from payments.core import BasicProvider

from django.conf import settings

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature

from blockbee import BlockBeeCheckoutHelper, BlockBeeRequests


class BlockBeeProvider(BasicProvider):
    def __init__(self, apikey, *args, **kwargs):
        self.apikey = apikey
        super().__init__(*args, **kwargs)

    def get_form(self, payment, data=None):
        protocol = "https" if settings.PAYMENT_USES_SSL else "http"
        payment_host = settings.PAYMENT_HOST
        base_url = f"{protocol}://{payment_host}"

        notify_url = f"{base_url}/payments/process/blockbee/"
        redirect_url = f"{base_url}{payment.get_success_url()}"
        
        bb_parameters = {
            "notify_url": notify_url,
            "currency": payment.currency,
            "item_description": payment.description,
            "post": 1
        }

        bb = BlockBeeCheckoutHelper(self.apikey, None, bb_parameters)

        payment_request = bb.payment_request(redirect_url, payment.total)

        if payment_request.get("status") != "success":
            raise Exception(f"BlockBee API error: {payment_request.get('error')}")

        payment.token = payment_request.get("payment_id")
        payment.attrs.success_token = payment_request.get("success_token")
        payment.save()
        
        raise RedirectNeeded(payment_request.get("payment_url"))


    def process_data(self, payment, request):
        # Verify webhook signature before processing any data
        if not self._verify_webhook_signature(request):
            return HttpResponse(status=401)

        data = request.POST
        payload = {key: data.get(key) for key in data.keys()}

        if all(k in payload for k in ("payment_id", "is_paid", "status")):
            payment_id = payload.get("payment_id")
            is_paid = str(payload.get("is_paid"))
            status = str(payload.get("status"))

            last_id = getattr(payment.attrs, "last_processed_payment_id", None)
            if last_id and last_id == payment_id:
                return HttpResponse("*ok*")

            expected_payment_id = getattr(payment.attrs, "payment_id", None)
            if expected_payment_id and expected_payment_id != payment_id:
                return HttpResponseBadRequest("payment_id mismatch")

            # Persist interesting fields for audit/debug
            for key in (
                "payment_url",
                "redirect_url",
                "value",
                "currency",
                "paid_amount",
                "paid_amount_fiat",
                "received_amount",
                "received_amount_fiat",
                "paid_coin",
                "exchange_rate",
                "txid",
                "address",
                "type",
                "status",
            ):
                val = payload.get(key)
                if val is not None:
                    setattr(payment.attrs, key, val)

            payment.attrs.last_processed_payment_id = payment_id
            payment.transaction_id = payload.get("txid")
            payment.save()

            if is_paid == "1" and status == "done":
                if payment.status != PaymentStatus.CONFIRMED:
                    payment.change_status(PaymentStatus.CONFIRMED, message="BlockBee webhook confirmed")
                return HttpResponse("*ok*")
            return HttpResponse("pending", status=202)

        return HttpResponseBadRequest("invalid webhook payload")

    def get_token_from_request(self, payment, request):
        if request.method != 'POST':
            return None

        token = request.POST.get("payment_id")
        if token:
            return token
        return None
        
    def _verify_webhook_signature(self, request):
        if request.method != 'POST':
            return False

        try:
            data = request.body.decode('utf-8')

            sig_b64 = request.headers["x-ca-signature"]
            if not sig_b64:
                return False

            pubkey = BlockBeeRequests.process_request_get(endpoint="pubkey").get("pubkey")

            signature = base64.b64decode(sig_b64)

            try:
                public_key = serialization.load_pem_public_key(
                    pubkey.encode("utf-8"),
                    backend=default_backend()
                )
                public_key.verify(
                    signature,
                    data.encode("utf-8"),
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )
                return True
            except InvalidSignature:
                return False
        except Exception:
            return False

    def capture(self, payment, amount=None):
      # Implement payment capture logic
      raise NotImplementedError("Capture method not implemented.")


    def refund(self, payment, amount=None):
      # Implement payment refund logic
      raise NotImplementedError("Refund method not implemented.")
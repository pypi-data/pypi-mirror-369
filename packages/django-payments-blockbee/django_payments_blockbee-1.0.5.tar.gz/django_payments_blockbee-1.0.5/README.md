# django-payments-blockbee

[![PyPI - Version](https://img.shields.io/pypi/v/django-payments-blockbee.svg)](https://pypi.org/project/django-payments-blockbee)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-payments-blockbee.svg)](https://pypi.org/project/django-payments-blockbee)

-----

`django-payments-blockbee` adds support for the [BlockBee](https://blockbee.io) hosted checkout to [Django Payments](https://django-payments.readthedocs.io/).

**Table of Contents**

- [Installation](#installation)
- [Configuration](#configuration)
- [Webhook](#webhook)
- [Usage](#usage)
- [Security Features](#security-features)
- [Testing](#testing)
- [License](#license)

## Installation

```console
pip install django-payments-blockbee
```

## Configuration

Follow the Django Payments setup (define a concrete `Payment` model and set `PAYMENT_MODEL`). Then add this variant:

```python
PAYMENT_VARIANTS = {
    "blockbee": (
        "payments_blockbee.BlockBeeProvider",
        {
            "apikey": "your-blockbee-api-key",
        },
    )
}

# Required django-payments settings
PAYMENT_HOST = "your-domain.com"  # or ngrok URL for development
PAYMENT_USES_SSL = True  # Set to False for local development
PAYMENT_MODEL = "your_app.Payment"
```

### Available configuration options

- `apikey`: Your BlockBee API key

### Django-payments settings

- `PAYMENT_HOST`: Your domain or ngrok URL for development
- `PAYMENT_USES_SSL`: Set to `True` for production, `False` for local development
- `PAYMENT_MODEL`: Your concrete Payment model

Notes:
- Currency is taken from the `Payment` instance (`payment.currency`, e.g. `"EUR"`).
- The provider automatically constructs webhook and redirect URLs using django-payments standard endpoints.
- We recommend using a public tunnel (ngrok/cloudflared) for local development.

## Webhook

**No custom webhook view needed!** The provider automatically handles webhooks through django-payments standard endpoints:

- **Webhook URL**: `/payments/process/blockbee/` (automatically created by django-payments)
- **Success URL**: Uses your payment model's `get_success_url()` method
- **Method**: POST with signature verification

The provider processes POST webhooks and confirms the payment when `is_paid == "1"` and `status == "done"`.

## Usage

Create a `Payment` and call `get_form()` or handle `RedirectNeeded` per Django Payments docs:

```python
from django.shortcuts import redirect, render
from payments import RedirectNeeded, get_payment_model

def checkout(request):
    Payment = get_payment_model()
    payment = Payment.objects.create(
        variant="blockbee",
        description="Order #123",
        total="10.00",
        currency="EUR",
    )
    try:
        # This will raise RedirectNeeded with BlockBee payment URL
        payment.get_form(data=request.POST or None)
    except RedirectNeeded as redirect_to:
        # Django-payments automatically redirects user to BlockBee
        return redirect(str(redirect_to))
```

On successful webhook processing, the provider will set the `Payment` status to `confirmed`. Useful webhook payload fields (like `paid_amount_fiat`, `paid_coin`, `txid`) are saved into `payment.attrs`.

## Security Features

### Webhook Signature Verification

The provider automatically verifies BlockBee webhook signatures using RSA-SHA256:

- **Algorithm**: RSA-SHA256 with PKCS1v15 padding
- **Public Key**: Fetched dynamically from BlockBee's API
- **Signature Header**: `x-ca-signature`
- **Data Verified**: Request body for POST requests

### Payment ID Mapping

- BlockBee's `payment_id` is automatically mapped to your payment's `token` and `transaction_id`
- This ensures consistent identification across both systems
- No manual ID mapping required

## Testing

BlockBee does not provide a sandbox environment. Testing is done against live endpoints. Recommended practices:

- Use small order amounts when developing (e.g., 1–2 USD) and low-fee networks/coins
- Enable a public tunnel (ngrok/cloudflared) so your webhook endpoint is reachable
- Treat webhook handling as idempotent (this provider already does)
- Never expose secrets in client code; keep the API key in server-side settings

## License

`django-payments-blockbee` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
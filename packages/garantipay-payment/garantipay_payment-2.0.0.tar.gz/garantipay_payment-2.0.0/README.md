# Garantipay 2.0 Redirect View

This app provides order related data to the Garantipay 2.0 payment extension when plugged-in to project zero.

## Installation

Add the package to requirements.txt file and install it via pip:

    garantipay-payment

## Adding App

Add the following lines in `omnife_base.settings`:

    INSTALLED_APPS.append('garantipay_payment')
    PZ_SERVICE_CLASS = "omnife.core.service.Service"
    HASH_SECRET_KEY = "your-hash-secret-key"
    PRODUCT_KIND_ATTRIBUTE_NAME = "product_kind"
    GARANTIPAY_EXTENSION_URL = "" put extension form page url 

Add url pattern to `omnife_base.urls` like below:

    urlpatterns = [
        ...
        path('payment-gateway/garantipay/', include('garantipay_payment.urls')),
    ]

## Running Tests

    python -m unittest discover

## Python Version Compatibility

This package is compatible with the following Python versions:
  - Python 3.8
  - Python 3.9
  - Python 3.13

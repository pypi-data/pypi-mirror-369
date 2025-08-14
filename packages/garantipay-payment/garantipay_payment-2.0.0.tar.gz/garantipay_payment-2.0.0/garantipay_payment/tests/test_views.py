from django.conf import settings
from django.template.response import TemplateResponse
from django.test import SimpleTestCase
from django.test import override_settings
from django.test.client import RequestFactory
from mock.mock import patch
from rest_framework import status

from garantipay_payment.tests.mixins import MockResponseMixin

try:
    settings.configure()
except RuntimeError:
    pass


@override_settings(
    GARANTIPAY_EXTENSION_URL="http://test.com",
    PRODUCT_KIND_ATTRIBUTE_NAME="product_kind",
    PZ_SERVICE_CLASS="garantipay_payment.commerce.dummy.Service",
    HASH_SECRET_KEY="hash_secret_key",
)
class TestGarantiPayPaymentRedirectView(SimpleTestCase, MockResponseMixin):

    def setUp(self):
        self.request_factory = RequestFactory()

    @patch("garantipay_payment.commerce.dummy.Service.get")
    @patch("garantipay_payment.commerce.checkout.CheckoutService.generate_hash")
    @patch("secrets.token_hex")
    def test_get(self, mock_token_hex, mock_generate_hash, mock_get):
        import django
        django.setup()
        from garantipay_payment.views import GarantiPayView

        response = self._mock_response(
            status_code=200,
            content=self._get_response("orders_checkout_response"),
            headers={"Content-Type": "application/json"},
        )
        mock_get.return_value = response
        mock_generate_hash.return_value = "test-hash"
        mock_token_hex.return_value = "test-salt"

        request = self.request_factory.get("/payment-gateway/garantipay/")
        request.GET = {"sessionId": "test-session-id"}
        response = GarantiPayView.as_view()(request)
        mock_generate_hash.assert_called_once_with("test-session-id", "test-salt")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response, TemplateResponse)
        self.assertEqual(response.template_name, "garantipay.html")

        context = response.context_data
        self.assertIn("basket_items", context)
        self.assertIn("hash_form", context)

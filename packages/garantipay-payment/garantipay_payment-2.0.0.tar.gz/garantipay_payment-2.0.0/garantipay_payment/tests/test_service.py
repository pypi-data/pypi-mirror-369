from django.conf import settings
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
    HASH_SECRET_KEY="test-hash-secret-key",
    PRODUCT_KIND_ATTRIBUTE_NAME="product_kind",
    PZ_SERVICE_CLASS="garantipay_payment.commerce.dummy.Service",
)
class TestCheckoutService(SimpleTestCase, MockResponseMixin):
    def setUp(self):
        from garantipay_payment.commerce.checkout import CheckoutService

        self.service = CheckoutService()
        self.request_factory = RequestFactory()

    @patch("garantipay_payment.commerce.dummy.Service.get")
    @patch("garantipay_payment.commerce.checkout.CheckoutService.generate_hash")
    def test_get_basket_data(self, mock_generate_hash, mock_get):
        mock_generate_hash.return_value = "test-hash"
        mocked_response = self._mock_response(
            status_code=200,
            content=self._get_response("orders_checkout_response"),
            headers={"Content-Type": "application/json"},
        )
        mock_get.return_value = mocked_response

        request = self.request_factory.get("/payment-gateway/garantipay/")
        basket_data = self.service.get_basket_data(request, "test-salt")

        self.assertEqual(basket_data["platform"], "default")
        self.assertEqual(basket_data["hash"], "test-hash")
        self.assertEqual(
            basket_data["basket_items"],
            [
                {"amount": "30.00", "product_kind": "test-phone"},
            ],
        )

    @patch("garantipay_payment.commerce.dummy.Service.get")
    def test_retrieve_pre_oder(self, mock_get):
        mocked_response = self._mock_response(
            status_code=200,
            content=self._get_response("orders_checkout_response"),
            headers={"Content-Type": "application/json"},
        )
        mock_get.return_value = mocked_response

        request = self.request_factory.get("/payment-gateway/garantipay/")
        response = self.service._retrieve_pre_order(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("pre_order", response.data)

    @patch("garantipay_payment.commerce.dummy.Service.get")
    def test_get_basket_items(self, mock_get):
        mocked_response = self._mock_response(
            status_code=200,
            content=self._get_response("orders_checkout_response"),
            headers={"Content-Type": "application/json"},
        )
        mock_get.return_value = mocked_response

        request = self.request_factory.get("/payment-gateway/garantipay/")
        basket_items = self.service._get_basket_items(request)

        self.assertEqual(
            basket_items,
            [
                {"amount": "30.00", "product_kind": "test-phone"},
            ],
        )

    def test_get_client_type(self):
        request = self.request_factory.get("/payment-gateway/garantipay/")
        default_client_type = self.service._get_client_type(request)
        self.assertEqual(default_client_type, "default")

        request.META["HTTP_X_APP_DEVICE"] = "android"
        android_client_type = self.service._get_client_type(request)
        self.assertEqual(android_client_type, "android")

    @patch("hashlib.sha512")
    def test_get_hash(self, mock_sha512):
        session_id = "test-session-id"
        self.service.generate_hash(session_id, "test-salt")
        mock_sha512.assert_called_once_with(
            "test-salt|test-session-id|test-hash-secret-key".encode("utf-8")
        )

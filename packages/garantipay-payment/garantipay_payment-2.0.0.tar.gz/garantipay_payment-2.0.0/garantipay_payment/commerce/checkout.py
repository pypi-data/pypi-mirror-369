import hashlib
from importlib import import_module
from enum import Enum

from django.conf import settings


module, _class = settings.PZ_SERVICE_CLASS.rsplit(".", 1)
Service = getattr(import_module(module), _class)


class ClientType(Enum):
    default = "default"
    android = "android"
    ios = "ios"
    instore = "instore"
    b2b = "b2b"


class CheckoutService(Service):
    def get_basket_data(self, request, salt):
        platform = self._get_client_type(request)
        session_id = request.GET.get("sessionId")
        hash_ = self.generate_hash(session_id, salt)
        basket_items = self._get_basket_items(request)

        return {
            "basket_items": basket_items,
            "platform": platform,
            "hash": hash_,
        }

    @staticmethod
    def _get_client_type(request):
        device = request.META.get("HTTP_X_APP_DEVICE")
        try:
            return ClientType(device).value
        except ValueError:
            return ClientType.default.value

    def generate_hash(self, session_id, salt):
        hash_key = settings.HASH_SECRET_KEY
        return hashlib.sha512(
            f"{salt}|{session_id}|{hash_key}".encode("utf-8")
        ).hexdigest()

    def _get_basket_items(self, request):
        product_kind = settings.PRODUCT_KIND_ATTRIBUTE_NAME
        response = self._retrieve_pre_order(request)
        basket_items = response.data["pre_order"]["basket"]["basketitem_set"]
        return [
            {
                "amount": item["total_amount"],
                "product_kind": item["product"]["attributes"].get(product_kind),
            }
            for item in basket_items
        ]

    def _retrieve_pre_order(self, request):
        path = "/orders/checkout/?page=OrderNotePage"
        response = self.get(
            path, request=request, headers={"X-Requested-With": "XMLHttpRequest"}
        )
        return self.normalize_response(response)

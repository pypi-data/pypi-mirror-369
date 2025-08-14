import secrets

from django.conf import settings
from django.views.generic import View
from django.template.response import TemplateResponse

from garantipay_payment.forms import BasketItemFormSet, HashForm
from garantipay_payment.commerce.checkout import CheckoutService


class GarantiPayView(View):
    checkout_service = CheckoutService()

    def get(self, request):
        salt = secrets.token_hex(16)
        basket = self.checkout_service.get_basket_data(request, salt)
        session_id = request.GET.get("sessionId")
        basket_items = basket["basket_items"]
        hash_form = HashForm(
            initial={
                "salt": salt,
                "hash": basket["hash"],
                "platform": basket["platform"],
            }
        )

        return TemplateResponse(
            request=request,
            template="garantipay.html",
            context={
                "action_url": f"{settings.GARANTIPAY_EXTENSION_URL}/?sessionId={session_id}",
                "action_method": "POST",
                "hash_form": hash_form,
                "basket_items": BasketItemFormSet(initial=basket_items),
            },
        )

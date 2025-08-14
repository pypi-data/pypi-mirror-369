from django.urls import path

from garantipay_payment.views import GarantiPayView

urlpatterns = [
    path("", GarantiPayView.as_view(), name="garantipay-payment"),
]

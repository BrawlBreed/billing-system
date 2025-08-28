# billing_system/silver/urls.py

from __future__ import absolute_import

from django.conf.urls import include, re_path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from silver.views import (
    pay_transaction_view, complete_payment_view,
    InvoiceAutocomplete, ProformaAutocomplete,
    PaymentMethodAutocomplete, PlanAutocomplete,
    CustomerAutocomplete, ProviderAutocomplete
)

admin.autodiscover()

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^api-auth/', include('rest_framework.urls',
                                   namespace='rest_framework')),
    re_path(r'', include('silver.api.urls')),

    re_path(r'pay/(?P<token>[0-9a-zA-Z-_\.]+)/$',
            pay_transaction_view, name='payment'),
    re_path(r'pay/(?P<token>[0-9a-zA-Z-_\.]+)/complete$',
            complete_payment_view, name='payment-complete'),

    re_path(r'^autocomplete/invoices/$',
            InvoiceAutocomplete.as_view(), name='autocomplete-invoice'),
    re_path(r'^autocomplete/proformas/$',
            ProformaAutocomplete.as_view(), name='autocomplete-proforma'),
    re_path(r'^autocomplete/payment-method/$',
            PaymentMethodAutocomplete.as_view(), name='autocomplete-payment-method'),
    re_path(r'^autocomplete/plan/$',
            PlanAutocomplete.as_view(), name='autocomplete-plan'),
    re_path(r'^autocomplete/customer/$',
            CustomerAutocomplete.as_view(), name='autocomplete-customer'),
    re_path(r'^autocomplete/provider/$',
            ProviderAutocomplete.as_view(), name='autocomplete-provider'),
]

# Optional: serve media in dev
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

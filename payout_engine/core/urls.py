from django.urls import path
from core.views import PayoutCreateView, PayoutStatusView,MerchantBalanceView,PayoutListView

urlpatterns = [
    path('payouts', PayoutCreateView.as_view()),
    path('payouts/<int:payout_id>', PayoutStatusView.as_view()),
    path('merchant/<int:merchant_id>/balance', MerchantBalanceView.as_view()),
    path('merchant/<int:merchant_id>/payouts', PayoutListView.as_view()),
]
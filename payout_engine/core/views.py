from rest_framework.views import APIView
from rest_framework.response import Response
from core.models import Merchant
from core.models import Payout
from rest_framework import status
import uuid

from core.serializers import PayoutRequestSerializer
from core.services.payout_service import create_payout
from core.services.payout_service import get_balance

from core.models import Payout

class PayoutCreateView(APIView):

    def post(self, request):
        serializer = PayoutRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        idempotency_key = request.headers.get("Idempotency-Key")

        if not idempotency_key:
            return Response(
                {"error": "Idempotency-Key header required"},
                status=400
            )

        try:
            idempotency_key = uuid.UUID(idempotency_key)
        except:
            return Response({"error": "Invalid UUID"}, status=400)

        try:
            payout = create_payout(
                merchant_id=serializer.validated_data["merchant_id"],  # ✅ FIXED
                amount_paise=serializer.validated_data["amount_paise"],
                idempotency_key=idempotency_key
            )

            return Response({
                "id": payout.id,
                "amount": payout.amount_paise,
                "status": payout.status
            })

        except Exception as e:
            return Response({"error": str(e)}, status=400)


class PayoutStatusView(APIView):

    def get(self, request, payout_id):
        try:
            payout = Payout.objects.get(id=payout_id)

            return Response({
                "id": payout.id,
                "amount": payout.amount_paise,
                "status": payout.status,
                "retry_count": payout.retry_count
            })

        except Payout.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

class MerchantBalanceView(APIView):

    def get(self, request, merchant_id):
        try:
            merchant = Merchant.objects.get(id=merchant_id)
            balance = get_balance(merchant)

            return Response({
                "merchant_id": merchant.id,
                "balance": balance
            })

        except Merchant.DoesNotExist:
            return Response({"error": "Merchant not found"}, status=404)

from rest_framework.views import APIView
from rest_framework.response import Response
from core.models import Payout

class PayoutListView(APIView):

    def get(self, request, merchant_id):
        payouts = Payout.objects.filter(merchant_id=merchant_id).order_by('-created_at')

        data = []
        for p in payouts:
            data.append({
                "id": p.id,
                "amount": p.amount_paise,
                "status": p.status,
                "created_at": p.created_at
            })

        return Response(data)
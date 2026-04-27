from rest_framework import serializers

class PayoutRequestSerializer(serializers.Serializer):
    merchant_id = serializers.IntegerField()
    amount_paise = serializers.IntegerField()
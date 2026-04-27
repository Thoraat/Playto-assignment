from rest_framework import serializers

class PayoutRequestSerializer(serializers.Serializer):
    merchant_id = serializers.IntegerField() 
    amount_paise = serializers.IntegerField(min_value=1)
    bank_account_id = serializers.IntegerField()  # just dummy for now
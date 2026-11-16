from decimal import Decimal

from rest_framework import serializers

from .models import Account, Transaction


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Account
        # VULN-04: mass assignment, every model field is writable on signup,
        # including balance_eur and is_verified
        fields = "__all__"
        read_only_fields = ["user", "iban"]


class AccountSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Account
        fields = ["username", "iban", "balance_eur", "balance_usd", "is_verified", "avatar_url"]
        read_only_fields = ["iban", "balance_eur", "balance_usd", "is_verified"]


class TransactionSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source="sender.iban", read_only=True)
    receiver = serializers.CharField(source="receiver.iban", read_only=True)

    class Meta:
        model = Transaction
        fields = ["id", "sender", "receiver", "amount", "note", "created"]


class TransferSerializer(serializers.Serializer):
    to = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))
    note = serializers.CharField(required=False, allow_blank=True, max_length=200)


class ExchangeSerializer(serializers.Serializer):
    source = serializers.ChoiceField(choices=["EUR", "USD"])
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))

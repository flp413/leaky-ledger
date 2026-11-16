import random
from decimal import ROUND_UP, Decimal

import requests
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import connection
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .auth import make_token
from .models import Account, Transaction
from .assistant import chat
from .services import TransferError, send_money
from .serializers import (
    AccountSerializer,
    ExchangeSerializer,
    RegisterSerializer,
    TransactionSerializer,
    TransferSerializer,
)

EUR_TO_USD = Decimal("1.0837")

CENT = Decimal("0.01")


def index(request):
    return HttpResponse("<h1>leaky-ledger</h1><p>Deliberately vulnerable. Localhost only.</p>")


class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = RegisterSerializer

    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        username = ser.validated_data.pop("username")
        password = ser.validated_data.pop("password")
        if User.objects.filter(username=username).exists():
            return Response({"error": "username taken"}, status=400)
        user = User.objects.create_user(username=username, password=password)
        iban = f"SI56{random.randint(10**14, 10**15 - 1)}"
        account = Account.objects.create(user=user, iban=iban, **ser.validated_data)
        return Response(AccountSerializer(account).data, status=201)


class LoginView(APIView):
    # VULN-05b: no throttle_classes, so passwords can be brute forced
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        request=inline_serializer(
            "Login", {"username": serializers.CharField(), "password": serializers.CharField()}
        ),
        responses=inline_serializer("Token", {"token": serializers.CharField()}),
    )
    def post(self, request):
        user = authenticate(
            username=request.data.get("username"), password=request.data.get("password")
        )
        if user is None:
            return Response({"error": "bad credentials"}, status=401)
        return Response({"token": make_token(user)})


class MeView(APIView):
    serializer_class = AccountSerializer

    def get(self, request):
        return Response(AccountSerializer(request.user.account).data)

    def patch(self, request):
        account = request.user.account
        ser = AccountSerializer(account, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        url = ser.validated_data.get("avatar_url")
        if url:
            # VULN-06: SSRF, the server fetches any URL, including internal
            # ones like http://169.254.169.254/ or http://localhost:8000/
            resp = requests.get(url, timeout=5)
            if not resp.headers.get("Content-Type", "").startswith("image/"):
                return Response(
                    {"error": "not an image", "preview": resp.text[:300]}, status=400
                )
        ser.save()
        return Response(ser.data)


class AccountDetailView(APIView):
    serializer_class = AccountSerializer

    def get(self, request, iban):
        # VULN-10: BOLA, any user can look up anyone's balance by IBAN
        account = Account.objects.filter(iban=iban).first()
        if account is None:
            return Response(status=404)
        return Response(AccountSerializer(account).data)


class TransferView(APIView):
    serializer_class = TransferSerializer

    def post(self, request):
        ser = TransferSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            tx = send_money(
                request.user,
                ser.validated_data["to"],
                ser.validated_data["amount"],
                ser.validated_data.get("note", ""),
            )
        except TransferError as e:
            return Response({"error": str(e)}, status=e.status)
        return Response(TransactionSerializer(tx).data, status=201)


class ExchangeView(APIView):
    serializer_class = ExchangeSerializer

    def post(self, request):
        ser = ExchangeSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        source = ser.validated_data["source"]
        amount = ser.validated_data["amount"]
        acc = Account.objects.get(user=request.user)

        if source == "EUR":
            if acc.balance_eur < amount:
                return Response({"error": "insufficient funds"}, status=400)
            # VULN-11: the credited side is rounded UP, so tiny round trips
            # EUR -> USD -> EUR create money out of nothing
            credited = (amount * EUR_TO_USD).quantize(CENT, rounding=ROUND_UP)
            acc.balance_eur -= amount
            acc.balance_usd += credited
        else:
            if acc.balance_usd < amount:
                return Response({"error": "insufficient funds"}, status=400)
            credited = (amount / EUR_TO_USD).quantize(CENT, rounding=ROUND_UP)
            acc.balance_usd -= amount
            acc.balance_eur += credited
        acc.save()
        return Response({"credited": str(credited), **AccountSerializer(acc).data})


class TransactionListView(APIView):
    serializer_class = TransactionSerializer

    @extend_schema(operation_id="transactions_list", responses=TransactionSerializer(many=True))
    def get(self, request):
        acc = request.user.account
        txs = (Transaction.objects.filter(sender=acc) | Transaction.objects.filter(receiver=acc))
        return Response(TransactionSerializer(txs.order_by("-created"), many=True).data)


class TransactionDetailView(APIView):
    serializer_class = TransactionSerializer

    def get(self, request, tx_id):
        # VULN-01: IDOR, any logged-in user can read any transaction by id
        tx = Transaction.objects.filter(pk=tx_id).first()
        if tx is None:
            return Response(status=404)
        return Response(TransactionSerializer(tx).data)


class TransactionSearchView(APIView):
    @extend_schema(
        operation_id="transactions_search",
        parameters=[OpenApiParameter("q", str, description="text to look for in notes")],
        responses=TransactionSerializer(many=True),
    )
    def get(self, request):
        q = request.query_params.get("q", "")
        # VULN-02: SQL injection through the note search
        sql = (
            "SELECT id, amount, note FROM wallet_transaction "
            f"WHERE sender_id = {request.user.account.id} AND note LIKE '%{q}%'"
        )
        with connection.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()
        return Response([{"id": r[0], "amount": str(r[1]), "note": r[2]} for r in rows])


class AssistantView(APIView):
    @extend_schema(
        request=inline_serializer("AssistantRequest", {"message": serializers.CharField()}),
        responses=inline_serializer(
            "AssistantReply",
            {"reply": serializers.CharField(), "actions": serializers.ListField()},
        ),
    )
    def post(self, request):
        return Response(chat(request.user, str(request.data.get("message", ""))))


def receipt(request, tx_id):
    # VULN-08: no auth at all, and ?name= is reflected unescaped (XSS)
    tx = Transaction.objects.filter(pk=tx_id).first()
    if tx is None:
        return HttpResponse("not found", status=404)
    name = request.GET.get("name", "customer")
    html = (
        f"<h2>Receipt #{tx.id}</h2><p>Hi {name},</p>"
        f"<p>{tx.amount} EUR to {tx.receiver.iban}</p>"
    )
    return HttpResponse(mark_safe(html))

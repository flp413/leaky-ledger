from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from wallet.auth import make_token
from wallet.models import Account, Transaction


@pytest.fixture
def alice(db):
    user = User.objects.create_user("alice", password="alice-pass-1")
    Account.objects.create(user=user, iban="SI56100000000000001", balance_eur=Decimal("500"))
    return user


@pytest.fixture
def bob(db):
    user = User.objects.create_user("bob", password="bob-pass-1")
    Account.objects.create(user=user, iban="SI56100000000000002", balance_eur=Decimal("100"))
    return user


@pytest.fixture
def alice_tx(alice, bob):
    return Transaction.objects.create(
        sender=alice.account, receiver=bob.account, amount=Decimal("42.00"), note="rent split"
    )


def client_for(user):
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {make_token(user)}")
    return c

from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from wallet.models import Account, Transaction


class Command(BaseCommand):
    help = "Create demo users alice, bob and carol with some money and one transaction"

    def handle(self, *args, **opts):
        if User.objects.filter(username="alice").exists():
            self.stdout.write("already seeded")
            return
        alice = User.objects.create_user("alice", password="alice-pass-1")
        bob = User.objects.create_user("bob", password="bob-pass-1")
        a = Account.objects.create(user=alice, iban="SI56100000000000001", balance_eur=Decimal("500"))
        b = Account.objects.create(user=bob, iban="SI56100000000000002", balance_eur=Decimal("100"))
        carol = User.objects.create_user("carol", password="carol-pass-1")
        c = Account.objects.create(user=carol, iban="SI56100000000000003", balance_eur=Decimal("50"))
        Transaction.objects.create(sender=a, receiver=b, amount=Decimal("42.00"), note="rent split")
        Transaction.objects.create(sender=a, receiver=c, amount=Decimal("15.00"), note="birthday gift")
        self.stdout.write("seeded alice, bob and carol")

import time

from .models import Account, Transaction


class TransferError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def fraud_check(sender, receiver, amount):
    """Stand-in for a call to an external risk engine (~50 ms)."""
    time.sleep(0.05)
    return True


def send_money(user, to_iban, amount, note=""):
    receiver = Account.objects.filter(iban=to_iban).first()
    if receiver is None:
        raise TransferError("unknown IBAN", status=404)

    # VULN-05: check-then-act with no transaction or row lock, so two
    # parallel transfers can both pass the balance check (double spend)
    sender = Account.objects.get(user=user)
    if sender.balance_eur < amount:
        raise TransferError("insufficient funds")
    if not fraud_check(sender, receiver, amount):
        raise TransferError("blocked by risk engine", status=403)
    sender.balance_eur -= amount
    receiver.balance_eur += amount
    sender.save()
    receiver.save()
    return Transaction.objects.create(sender=sender, receiver=receiver, amount=amount, note=note)

from django.db import transaction


def bad(sender, amount):
    # ruleid: balance-check-then-act
    if sender.balance_eur < amount:
        return "no"
    sender.balance_eur -= amount
    sender.save()


def good(user, amount):
    with transaction.atomic():
        sender = Account.objects.select_for_update().get(user=user)
        # ok: balance-check-then-act
        if sender.balance_eur < amount:
            return "no"
        sender.balance_eur -= amount
        sender.save()

from rest_framework.views import APIView


class Bad(APIView):
    def get(self, request, tx_id):
        # ruleid: drf-object-lookup-without-owner
        tx = Transaction.objects.filter(pk=tx_id).first()
        return tx


class BadByIban(APIView):
    def get(self, request, iban):
        # ruleid: drf-object-lookup-without-owner
        return Account.objects.get(iban=iban)


class Good(APIView):
    def get(self, request, tx_id):
        # ok: drf-object-lookup-without-owner
        return Transaction.objects.filter(pk=tx_id, sender__user=request.user).first()


def helper(request):
    # not a view method with a URL key, so the user lookup from a token is fine
    # ok: drf-object-lookup-without-owner
    return User.objects.filter(pk=payload["sub"]).first()

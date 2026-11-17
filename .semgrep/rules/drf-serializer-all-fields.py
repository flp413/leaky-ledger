from rest_framework import serializers


class Bad(serializers.ModelSerializer):
    class Meta:
        model = Account
        # ruleid: drf-serializer-all-fields
        fields = "__all__"


class Good(serializers.ModelSerializer):
    class Meta:
        model = Account
        # ok: drf-serializer-all-fields
        fields = ["username", "avatar_url"]

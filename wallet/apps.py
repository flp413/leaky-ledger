from django.apps import AppConfig


class WalletConfig(AppConfig):
    name = "wallet"

    def ready(self):
        from . import schema  # noqa: F401  registers the OpenAPI auth scheme

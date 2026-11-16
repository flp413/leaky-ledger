from django.urls import path
from drf_spectacular.views import SpectacularAPIView

from wallet import views

urlpatterns = [
    path("", views.index),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/auth/register", views.RegisterView.as_view()),
    path("api/auth/login", views.LoginView.as_view()),
    path("api/me", views.MeView.as_view()),
    path("api/accounts/<str:iban>", views.AccountDetailView.as_view()),
    path("api/transfers", views.TransferView.as_view()),
    path("api/exchange", views.ExchangeView.as_view()),
    path("api/transactions", views.TransactionListView.as_view()),
    path("api/transactions/search", views.TransactionSearchView.as_view()),
    path("api/transactions/<int:tx_id>", views.TransactionDetailView.as_view()),
    path("api/assistant", views.AssistantView.as_view()),
    path("receipt/<int:tx_id>", views.receipt),
]

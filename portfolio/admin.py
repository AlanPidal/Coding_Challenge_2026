from django.contrib import admin
from .models import Wallet, Transaction

# Registro simple para poder gestionar wallets desde el admin
@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("exchange_name", "user", "address", "created_at")
    search_fields = ("exchange_name", "address", "user__username")

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("wallet", "tx_type", "amount", "currency", "timestamp")
    search_fields = ("wallet__exchange_name", "tx_hash")

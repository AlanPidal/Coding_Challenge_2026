from django.db import models
from django.contrib.auth.models import User

# Modelo que representa una wallet o cuenta en un exchange o dirección on-chain
class Wallet(models.Model):
    # Relación con el usuario propietario (User de Django)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wallets")
    # Nombre del exchange o etiqueta de la wallet (ej. "Binance", "Metamask")
    exchange_name = models.CharField(max_length=100)
    # Campos para claves API (opcionales, no usados en el prototipo inicial)
    api_key = models.CharField(max_length=255, blank=True, null=True)
    api_secret = models.CharField(max_length=255, blank=True, null=True)
    # Dirección on-chain o identificador de la wallet
    address = models.CharField(max_length=255, blank=True, null=True)
    # Fecha de creación automática
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Representación legible en admin y shell
        return f"{self.exchange_name} — {self.address or 'sin dirección'}"


# Modelo opcional para transacciones asociadas a una wallet
class Transaction(models.Model):
    # Cada transacción pertenece a una Wallet
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    # Tipo de transacción: depósito o retiro
    tx_type = models.CharField(max_length=20, choices=(("deposit","Deposit"),("withdraw","Withdraw")), default="deposit")
    # Monto de la transacción (decimal para precisión)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    # Moneda de la transacción (ej. BTC, ETH, USDT)
    currency = models.CharField(max_length=10, default="BTC")
    # Hash de la transacción (opcional)
    tx_hash = models.CharField(max_length=255, blank=True, null=True)
    # Fecha y hora de la transacción
    timestamp = models.DateTimeField()

    def __str__(self):
        # Representación legible
        return f"{self.tx_type} {self.amount} {self.currency} ({self.wallet})"

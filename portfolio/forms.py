from django import forms
from .models import Wallet

class WalletForm(forms.ModelForm):
    """
    Formulario para crear una Wallet.
    Solo incluye exchange_name y address para el prototipo inicial.
    """
    class Meta:
        model = Wallet
        fields = ["exchange_name", "address", "cryptocurrency", "amount"]
        widgets = {
            "exchange_name": forms.TextInput(attrs={
                "class": "border rounded px-2 py-1 w-full",
                "placeholder": "Nombre del exchange (ej. Binance)"
            }),
            "address": forms.TextInput(attrs={
                "class": "border rounded px-2 py-1 w-full",
                "placeholder": "Dirección o etiqueta de la wallet (opcional)"
            }),
            "cryptocurrency": forms.Select(attrs={
                "class": "border rounded px-2 py-1 w-full"
            }),
            "amount": forms.NumberInput(attrs={
                "step": "0.00000001",
                "class": "border rounded px-2 py-1 w-full",
                "placeholder": "Cantidad (ej. 0.001)"
            }),
        }
        labels = {
            "exchange_name": "Exchange",
            "address": "Address",
            "cryptocurrency": "Cryptocurrency",
            "amount": "Amount",
        }
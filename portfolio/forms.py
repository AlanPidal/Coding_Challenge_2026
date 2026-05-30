from django import forms
from .models import Wallet

class WalletForm(forms.ModelForm):
    """
    Formulario para crear una Wallet.
    Solo incluye exchange_name y address para el prototipo inicial.
    """
    class Meta:
        model = Wallet
        fields = ["exchange_name", "address"]
        widgets = {
            # Widgets con clases CSS para que se vean bien con Tailwind CDN
            "exchange_name": forms.TextInput(attrs={
                "class": "border rounded px-2 py-1 w-full",
                "placeholder": "Nombre del exchange (ej. Binance)"
            }),
            "address": forms.TextInput(attrs={
                "class": "border rounded px-2 py-1 w-full",
                "placeholder": "Dirección o etiqueta de la wallet (opcional)"
            }),
        }
        labels = {
            "exchange_name": "Exchange",
            "address": "Address",
        }

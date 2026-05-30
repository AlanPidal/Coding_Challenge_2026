import requests
import logging
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Wallet
from .forms import WalletForm
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm

# Mapeo de códigos a IDs de CoinGecko (incluye BNB y DOGE)
COINGECKO_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "USDT": "tether",
    "SOL": "solana",
    "BNB": "binancecoin",
    "DOGE": "dogecoin",
}

@login_required
def dashboard(request):
    """
    Vista del dashboard:
    - Procesa formulario de agregar wallet (POST).
    - Consulta precios de BTC y ETH desde CoinGecko.
    - Calcula saldo de prueba por wallet.
    """

    # --- Manejo del formulario de agregar wallet ---
    if request.method == "POST":
        form = WalletForm(request.POST)
        if form.is_valid():
            wallet = form.save(commit=False)
            wallet.user = request.user  # asigna el usuario dueño
            wallet.save()
            messages.success(request, "Wallet agregada correctamente.")
            return redirect("portfolio:dashboard")
    else:
        form = WalletForm()

    # Preparar lista de ids para CoinGecko
    ids = ",".join(set(COINGECKO_IDS.values()))

    # --- Consulta de precios desde CoinGecko ---
    prices = {}
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": ids, "vs_currencies": "usd"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        for code, cg_id in COINGECKO_IDS.items():
            usd_val = data.get(cg_id, {}).get("usd")
            try:
                prices[code] = Decimal(str(usd_val)) if usd_val is not None else None
            except (InvalidOperation, TypeError):
                prices[code] = None
    except Exception as e:
        logging.error(f"Error al consultar CoinGecko: {e}")
        for code in COINGECKO_IDS.keys():
            prices[code] = None
    
    # Calcular balances usando cryptocurrency y amount
    wallets_qs = Wallet.objects.filter(user=request.user).order_by("-id")
    wallets_with_balance = []
    total_balance = Decimal("0")
    # acumulador por crypto en USD
    per_crypto_usd = {}

    for w in wallets_qs:
        price = prices.get(w.cryptocurrency)
        try:
            amount = Decimal(w.amount)
        except (InvalidOperation, TypeError):
            amount = Decimal("0")

        if price is not None:
            balance_usd = (amount * price).quantize(Decimal("0.01"))
            total_balance += balance_usd
            balance_display = f"{balance_usd}"
            # acumular por crypto
            per_crypto_usd[w.cryptocurrency] = per_crypto_usd.get(w.cryptocurrency, Decimal("0")) + balance_usd
        else:
            balance_display = "No disponible"
            # no acumulamos si no hay precio

        wallets_with_balance.append({
            "wallet": w,
            "balance": balance_display,
            "currency": "USD",
            "amount": str(amount),
            "crypto": w.cryptocurrency,
            "price_per_unit": str(price) if price is not None else None,
        })

    # --- Preparar datos para el gráfico de pastel (porcentajes) ---
    chart_labels = []
    chart_values = []
    chart_colors = []

    # Paleta simple por crypto (puedes ajustar colores)
    COLOR_MAP = {
        "BTC": "#f2a900",   # naranja Bitcoin
        "ETH": "#3c3c3d",   # gris Ethereum
        "USDT": "#26a17b",  # verde Tether
        "SOL": "#00ffa3",   # verde-azulado Solana
        "BNB": "#f3ba2f",   # amarillo BNB
        "DOGE": "#c2a633",  # dorado Doge
    }

    # Si total_balance es 0 o no hay datos, evitamos división por cero
    if total_balance > 0:
        for code, usd_sum in per_crypto_usd.items():
            # saltar si usd_sum es 0
            if usd_sum <= 0:
                continue
            chart_labels.append(code)
            # convertir Decimal a float para JS
            chart_values.append(float(usd_sum))
            chart_colors.append(COLOR_MAP.get(code, "#888888"))
    else:
        # Si no hay saldo (o API falló), podemos mostrar datos vacíos o un placeholder
        chart_labels = []
        chart_values = []
        chart_colors = []

    # Preparar objeto que pasaremos al template (se serializará con json_script)
    chart_data = {
        "labels": chart_labels,
        "values": chart_values,
        "colors": chart_colors,
    }

    context = {
        "wallets": wallets_with_balance,
        "total_balance": float(total_balance.quantize(Decimal("0.01"))),
        "form": form,
        "chart_data": chart_data,  # datos para el pie chart
    }
    return render(request, "portfolio/dashboard.html", context)

def register_view(request):
    """
    Registro simple con UserCreationForm.
    """
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("portfolio:dashboard")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})

@login_required
def delete_wallet(request, pk):
    """
    Borra una Wallet identificada por pk.
    - Solo acepta POST (evita borrados por GET).
    - Verifica que la wallet pertenezca al usuario autenticado.
    - Redirige al dashboard con un mensaje.
    """
    # Recupera la wallet o devuelve 404 si no existe
    wallet = get_object_or_404(Wallet, pk=pk)

    # Verifica propiedad
    if wallet.user != request.user:
        # No autorizado: opcionalmente podrías devolver 403, aquí redirigimos con mensaje
        messages.error(request, "No tienes permiso para eliminar esta wallet.")
        return redirect("portfolio:dashboard")

    if request.method == "POST":
        wallet.delete()
        messages.success(request, "Wallet eliminada correctamente.")
        return redirect("portfolio:dashboard")

    # Si por alguna razón se accede por GET, redirigimos al dashboard
    return redirect("portfolio:dashboard")
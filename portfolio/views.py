from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Wallet
from .forms import WalletForm
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

@login_required
def dashboard(request):
    """
    Vista del dashboard:
    - Requiere que el usuario esté autenticado (login_required).
    - Recupera las wallets del usuario.
    - Calcula un 'pseudo-saldo' por wallet usando una fórmula determinista
      (esto es solo para pruebas; más adelante se integraría con APIs).
    - Suma los saldos para mostrar un saldo total.
    - Permite crear una nueva wallet mediante POST (mismo formulario en la página).
    """
    # Queryset con las wallets del usuario actual
    wallets_qs = Wallet.objects.filter(user=request.user).order_by("-created_at")

    wallets_with_balance = []
    total_balance = 0.0

    # Generamos un balance de ejemplo por wallet (determinista, sin APIs)
    # Fórmula simple: (len(address) % 7 + 1) * 12.34 -> produce valores reproducibles
    for w in wallets_qs:
        addr = w.address or ""
        pseudo_balance = (len(addr) % 7 + 1) * 12.34
        pseudo_balance = round(pseudo_balance, 2)
        wallets_with_balance.append({
            "wallet": w,
            "balance": pseudo_balance,
            "currency": "USD"  # mostramos en USD por simplicidad
        })
        total_balance += pseudo_balance

    total_balance = round(total_balance, 2)

    # Manejo del formulario para agregar wallet
    if request.method == "POST":
        form = WalletForm(request.POST)
        if form.is_valid():
            new_wallet = form.save(commit=False)
            new_wallet.user = request.user  # asignamos el usuario actual
            new_wallet.save()
            messages.success(request, "Wallet agregada correctamente.")
            # Redirigimos para evitar reenvío del formulario al refrescar
            return redirect("portfolio:dashboard")
    else:
        form = WalletForm()

    context = {
        "wallets": wallets_with_balance,
        "total_balance": total_balance,
        "form": form,
    }
    # Renderizamos el template del dashboard
    return render(request, "portfolio/dashboard.html", context)


def register_view(request):
    """
    Vista de registro:
    - Usa UserCreationForm para crear un usuario nuevo.
    - Si el formulario es válido, hace login automático y redirige al dashboard.
    """
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # loguea al usuario recién creado
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
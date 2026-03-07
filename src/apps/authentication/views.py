from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _


def login_view(request):
    if request.user.is_authenticated:
        return redirect("general:index")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(request.GET.get("next", "general:index"))

        return render(request, "auth/login.html", {"form_errors": True})

    return render(request, "auth/login.html")


def logout_view(request):
    logout(request)
    return redirect("auth:login")

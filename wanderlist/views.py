from django.shortcuts import render
from .utils import get_daily_quote

def dashboard(request):
    quote = get_daily_quote()
    return render(request, "dashboard.html", {"quote": quote})

from django.shortcuts import render
from .models import Plato

def home_view(request):
    platos_destacados = Plato.objects.filter(es_destacado=True, disponible=True)
    return render(request, 'home.html', {'platos': platos_destacados})
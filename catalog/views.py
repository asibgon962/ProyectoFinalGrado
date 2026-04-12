from django.shortcuts import render
from .models import Plato, Categoria

def home_view(request):
    platos_destacados = Plato.objects.filter(es_destacado=True, disponible=True)
    return render(request, 'home.html', {'platos': platos_destacados})

def menu_view(request):
    # 1. Traemos todas las categorías ordenadas según el campo 'orden' que definiste
    categorias = Categoria.objects.all().order_by('orden')
    
    # 2. Traemos solo los platos que están marcados como disponibles
    # Usamos prefetch_related para optimizar la carga de imágenes y categorías en una sola consulta
    platos = Plato.objects.filter(disponible=True).select_related('categoria')
    
    # 3. Enviamos los datos al template
    context = {
        'categorias': categorias,
        'platos': platos,
    }
    
    return render(request, 'menu.html', context)
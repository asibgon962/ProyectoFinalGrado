from django.contrib import admin
from .models import Categoria, Ingrediente, Plato, PlatoIngrediente

# Esto permite añadir ingredientes dentro de la ficha del plato
class RecetaInline(admin.TabularInline):
    model = PlatoIngrediente
    extra = 1  # Muestra una fila vacía por defecto para añadir rápido

@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_coste_unidad', 'unidad_medida')
    search_fields = ('nombre',)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'orden')

@admin.register(Plato)
class PlatoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio_venta', 'get_coste', 'get_beneficio', 'es_destacado')
    list_filter = ('categoria', 'es_destacado', 'disponible')
    inlines = [RecetaInline]  # <--- AQUÍ está la magia de la receta

    # Métodos para mostrar las @property en la lista
    def get_coste(self, obj):
        return f"{obj.coste_total} €"
    get_coste.short_description = 'Coste Prep.'

    def get_beneficio(self, obj):
        from django.utils.html import format_html
        color = "green" if obj.beneficio > 0 else "red"
        return format_html('<b style="color: {};">{} €</b>', color, obj.beneficio)
    get_beneficio.short_description = 'Margen Bruto'
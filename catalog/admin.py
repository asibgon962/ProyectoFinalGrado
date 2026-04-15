from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, Ingrediente, Plato, PlatoIngrediente, Producto, ProductoIngrediente, CategoriaProducto

# Esto permite añadir ingredientes dentro de la ficha del plato
class RecetaInline(admin.TabularInline):
    model = PlatoIngrediente
    extra = 1  # Muestra una fila vacía por defecto para añadir rápido
    autocomplete_fields = ['ingrediente']

@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_coste_unidad', 'unidad_medida')
    search_fields = ('nombre',)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'orden')
    list_editable = ('orden',)

@admin.register(Plato)
class PlatoAdmin(admin.ModelAdmin):
    # Usamos los nombres de campos que definimos en el models.py del catálogo
    list_display = ('nombre', 'categoria', 'precio_venta', 'get_coste', 'get_beneficio', 'disponible', 'es_destacado')
    list_filter = ('categoria', 'es_destacado', 'disponible')
    search_fields = ('nombre', 'descripcion')
    inlines = [RecetaInline]

    # Métodos para mostrar las @property del modelo en la lista del admin
    def get_coste(self, obj):
        return f"{obj.coste_total} €"
    get_coste.short_description = 'Coste Prep.'

    def get_beneficio(self, obj):
        beneficio = obj.beneficio
        color = "green" if beneficio > 0 else "red"
        return format_html('<b style="color: {};">{} €</b>', color, beneficio)
    get_beneficio.short_description = 'Margen Bruto'

class ProductoIngredienteInline(admin.TabularInline):
    model = ProductoIngrediente
    extra = 1
    autocomplete_fields = ['ingrediente']

@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'orden')
    list_editable = ('orden',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio_venta', 'stock', 'get_coste', 'get_beneficio', 'disponible')
    list_editable = ('stock', 'disponible')
    list_filter = ('categoria', 'disponible')
    search_fields = ('nombre', 'descripcion')
    inlines = [ProductoIngredienteInline]

    def get_coste(self, obj):
        return f"{obj.coste_total} €"
    get_coste.short_description = 'Coste Prep.'

    def get_beneficio(self, obj):
        beneficio = obj.beneficio
        color = "green" if beneficio > 0 else "red"
        return format_html('<b style="color: {};">{} €</b>', color, beneficio)
    get_beneficio.short_description = 'Margen Bruto'
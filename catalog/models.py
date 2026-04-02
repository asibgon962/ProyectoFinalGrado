from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Categorías"
        ordering = ['orden']

    def __str__(self):
        return self.nombre

class Ingrediente(models.Model):
    UNIDADES = [
        ('KG', 'Kilogramos'),
        ('L', 'Litros'),
        ('UNID', 'Unidades'),
    ]
    nombre = models.CharField(max_length=100)
    unidad_medida = models.CharField(max_length=20, choices=UNIDADES)
    precio_coste_unidad = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Coste por KG, Litro o Unidad"
    )

    def __str__(self):
        return f"{self.nombre} ({self.precio_coste_unidad}€/{self.unidad_medida})"

class Plato(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='platos')
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio de Venta")
    imagen = models.ImageField(upload_to='platos/', blank=True, null=True) # Permitimos que esté vacío al principio
    es_destacado = models.BooleanField(default=False)
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    @property
    def coste_total(self):
        """Suma el coste de todos los ingredientes asociados a este plato"""
        total = sum(item.importe_coste() for item in self.receta.all())
        return round(total, 2)

    @property
    def beneficio(self):
        """Diferencia entre PVP y Coste de producción"""
        return self.precio_venta - self.coste_total

class PlatoIngrediente(models.Model):
    """Relación muchos a muchos para la receta"""
    plato = models.ForeignKey(Plato, on_delete=models.CASCADE, related_name='receta')
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE)
    cantidad = models.DecimalField(
        max_digits=10, 
        decimal_places=3, 
        help_text="Ej: 0.150 para 150g o 1.000 para una unidad"
    )

    def importe_coste(self):
        # Convertimos a Decimal para asegurar precisión en el cálculo
        return self.cantidad * self.ingrediente.precio_coste_unidad

    def __str__(self):
        return f"{self.cantidad} de {self.ingrediente.nombre} para {self.plato.nombre}"
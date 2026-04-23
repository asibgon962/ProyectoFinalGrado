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
    precio_venta = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Precio de Venta")
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

class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=100)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Categorías de Productos (Mercado)"
        ordering = ['orden']

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    precio_venta = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Precio de Venta (Mercado Negro)")
    stock = models.IntegerField(default=0, verbose_name="Stock Disponible")
    imagen = models.ImageField(upload_to='productos_mercado/', blank=True, null=True)
    disponible = models.BooleanField(default=True)
 
    class Meta:
        verbose_name = "Producto (Mercado)"
        verbose_name_plural = "Productos (Mercado)"

    def __str__(self):
        return self.nombre

    @property
    def coste_total(self):
        total = sum(item.importe_coste() for item in self.receta.all())
        return round(total, 2)

    @property
    def beneficio(self):
        return self.precio_venta - self.coste_total

class ProductoIngrediente(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='receta')
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=3)

    def importe_coste(self):
        return self.cantidad * self.ingrediente.precio_coste_unidad

    def __str__(self):
        return f"{self.cantidad} de {self.ingrediente.nombre} para {self.producto.nombre}"


class BannerNormal(models.Model):
    """Banner visible en Home y en el Menú, filtrable por categoría de plato."""
    titulo = models.CharField(max_length=200, blank=True)
    subtitulo = models.CharField(max_length=300, blank=True)
    imagen = models.ImageField(upload_to='banners/', blank=True, null=True)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Si se deja vacío, aparece en 'Ver Todo' y en Home.",
        related_name='banners'
    )
    solo_en_home = models.BooleanField(
        default=False, 
        verbose_name="Solo en Home", 
        help_text="Si se marca, el banner solo aparecerá en la página principal y no en el menú general."
    )
    enlace = models.URLField(blank=True, help_text="URL opcional al hacer clic en el banner")
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Banner Normal"
        verbose_name_plural = "Banners Normales"
        ordering = ['orden']

    oferta = models.ForeignKey(
        'OfertaServicio', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='banners',
        help_text="Si se selecciona una oferta, al clicar el banner se pre-seleccionarán los platos de la oferta."
    )

    def __str__(self):
        cat = self.categoria.nombre if self.categoria else "General (Home & Todo)"
        return f"[{cat}] {self.titulo or 'Sin título'}"

class OfertaMercado(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    precio_total = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Precio Total Pack")
    activo = models.BooleanField(default=True)
    auto_aplicar = models.BooleanField(
        default=False, 
        verbose_name="Auto-aplicar",
        help_text="Si el usuario añade estos productos manualmente al carrito (en las cantidades indicadas), se aplicará el descuento automáticamente."
    )

    class Meta:
        verbose_name = "Oferta Mercado Negro"
        verbose_name_plural = "Ofertas Mercado Negro"

    def __str__(self):
        return f"{self.titulo} ({self.precio_total}€)"

class ItemOfertaMercado(models.Model):
    oferta = models.ForeignKey(OfertaMercado, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"

class OfertaServicio(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    precio_total = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Precio Total Pack")
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Oferta de Servicio/Platos"
        verbose_name_plural = "Ofertas de Servicio/Platos"

    def __str__(self):
        return f"{self.titulo} ({self.precio_total}€)"

class ItemOfertaServicio(models.Model):
    oferta = models.ForeignKey(OfertaServicio, related_name='items', on_delete=models.CASCADE)
    plato = models.ForeignKey(Plato, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.cantidad}x {self.plato.nombre}"

class Cupon(models.Model):
    TIPO_CHOICES = [
        ('PORCENTAJE', 'Porcentaje (%)'),
        ('FIJO', 'Importe Fijo (€)'),
    ]
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código del Cupón")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='PORCENTAJE')
    valor = models.DecimalField(max_digits=10, decimal_places=2, help_text="Ej: 10 para 10% o 10€")
    activo = models.BooleanField(default=True)
    usos_maximos = models.PositiveIntegerField(default=1, help_text="Cuántas veces se puede usar en total")
    usos_actuales = models.PositiveIntegerField(default=0)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Cupón"
        verbose_name_plural = "Cupones"

    def __str__(self):
        return f"{self.codigo} (-{self.valor}{'%' if self.tipo == 'PORCENTAJE' else '€'})"

    def es_valido(self):
        from django.utils import timezone
        if not self.activo:
            return False
        if self.usos_actuales >= self.usos_maximos:
            return False
        if self.fecha_expiracion and self.fecha_expiracion < timezone.now():
            return False
        return True


class BannerMercadoNegro(models.Model):
    """Banner visible en la página del Mercado Negro, filtrable por categoría de producto."""
    titulo = models.CharField(max_length=200, blank=True)
    subtitulo = models.CharField(max_length=300, blank=True)
    imagen = models.ImageField(upload_to='banners_mercado/', blank=True, null=True)
    categoria = models.ForeignKey(
        CategoriaProducto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Si se deja vacío, aparece al inicio de la página (sobre todas las categorías).",
        related_name='banners'
    )
    enlace = models.URLField(blank=True, help_text="URL opcional al hacer clic en el banner")
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Banner Mercado Negro"
        verbose_name_plural = "Banners Mercado Negro"
        ordering = ['orden']

    oferta = models.ForeignKey(
        'OfertaMercado', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='banners',
        help_text="Si se selecciona una oferta, al clicar el banner se añadirán los productos al carrito con precio especial."
    )

    def __str__(self):
        cat = self.categoria.nombre if self.categoria else "General (Portada)"
        return f"[{cat}] {self.titulo or 'Sin título'}"
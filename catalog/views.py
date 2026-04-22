from django.shortcuts import render
from .models import Plato, Categoria, BannerNormal, BannerMercadoNegro

def home_view(request):
    platos_destacados = Plato.objects.filter(es_destacado=True, disponible=True)
    # Banners generales (sin categoría) + todos los activos para el home
    banners_home = BannerNormal.objects.filter(activo=True)
    return render(request, 'home.html', {
        'platos': platos_destacados,
        'banners_home': banners_home,
    })

def restaurante_view(request):
    return render(request, 'restaurante.html')

def menu_view(request):
    # 1. Traemos todas las categorías ordenadas según el campo 'orden' que definiste
    categorias = Categoria.objects.all().order_by('orden')
    
    # 2. Traemos solo los platos que están marcados como disponibles y los ordenamos por el orden de la categoría
    platos = Plato.objects.filter(disponible=True).select_related('categoria').order_by('categoria__orden', 'id')

    # 3. Banners activos del menú, excluyendo los marcados solo para home
    banners_menu = BannerNormal.objects.filter(activo=True, solo_en_home=False).select_related('categoria')
    
    # 4. Enviamos los datos al template
    context = {
        'categorias': categorias,
        'platos': platos,
        'banners_menu': banners_menu,
    }
    
    return render(request, 'menu.html', context)

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Producto, CategoriaProducto
from orders.models import PedidoMercado, ItemPedidoMercado
from decimal import Decimal

@login_required
def mercado_negro_view(request):
    if getattr(request.user, 'organization', None) and request.user.organization.es_ilegal:
        categorias = CategoriaProducto.objects.all().order_by('orden')
        productos = Producto.objects.filter(disponible=True).select_related('categoria')
        banners_mercado = BannerMercadoNegro.objects.filter(activo=True).select_related('categoria')
        return render(request, 'mercado_negro.html', {
            'categorias': categorias,
            'productos': productos,
            'banners_mercado': banners_mercado,
        })
    messages.error(request, "Acceso Denegado. Solo organizaciones autorizadas pueden acceder al Mercado Negro.")
    return redirect('/')

@login_required
def agregar_carrito(request, producto_id):
    if not (getattr(request.user, 'organization', None) and request.user.organization.es_ilegal):
        return redirect('/')
    
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id)
        
        try:
            cantidad = int(request.POST.get('cantidad', 1))
        except ValueError:
            cantidad = 1
            
        if cantidad <= 0 or cantidad > 99:
            messages.error(request, "Cantidad inválida. Operación cancelada por seguridad.")
            return redirect('mercado_negro')
        
        cart = request.session.get('cart', {})
        if str(producto_id) in cart:
            nueva_cantidad = cart[str(producto_id)]['cantidad'] + cantidad
            if nueva_cantidad > 99:
                 messages.error(request, "No puedes exceder el límite de 99 unidades por producto.")
                 return redirect('mercado_negro')
            cart[str(producto_id)]['cantidad'] = nueva_cantidad
        else:
            cart[str(producto_id)] = {
                'nombre': producto.nombre,
                'precio_venta': str(producto.precio_venta),
                'cantidad': cantidad
            }
        
        request.session['cart'] = cart
        messages.success(request, f"Añadido {cantidad}x {producto.nombre} al carrito.")
    return redirect('mercado_negro')

@login_required
def ver_carrito(request):
    if not (getattr(request.user, 'organization', None) and request.user.organization.es_ilegal):
        return redirect('/')
    
    cart = request.session.get('cart', {})
    items_carrito = []
    total = Decimal('0.00')
    
    for p_id, item_data in cart.items():
        precio = Decimal(item_data['precio_venta'])
        subtotal = precio * item_data['cantidad']
        total += subtotal
        items_carrito.append({
            'producto_id': p_id,
            'nombre': item_data['nombre'],
            'precio': precio,
            'cantidad': item_data['cantidad'],
            'subtotal': subtotal
        })
        
    return render(request, 'carrito.html', {'items_carrito': items_carrito, 'total': total})

@login_required
def vaciar_carrito(request):
    request.session['cart'] = {}
    messages.success(request, "Has vaciado tu carrito.")
    return redirect('ver_carrito')

@login_required
def eliminar_item_carrito(request, producto_id):
    if not (getattr(request.user, 'organization', None) and request.user.organization.es_ilegal):
        return redirect('/')
    
    cart = request.session.get('cart', {})
    str_id = str(producto_id)
    if str_id in cart:
        nombre = cart[str_id]['nombre']
        del cart[str_id]
        request.session['cart'] = cart
        messages.success(request, f"Se ha retirado {nombre} del carrito.")
    
    return redirect('ver_carrito')

@login_required
def procesar_compra(request):
    if not (getattr(request.user, 'organization', None) and request.user.organization.es_ilegal):
        return redirect('/')
    
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if not cart:
            messages.error(request, "El carrito está vacio.")
            return redirect('ver_carrito')
            
        pedido = PedidoMercado.objects.create(
            usuario=request.user,
            organizacion=request.user.organization,
            total=0
        )
        total_pedido = Decimal('0.00')
        
        for p_id, item_data in cart.items():
            producto = Producto.objects.get(id=p_id)
            cantidad = item_data['cantidad']
            precio = producto.precio_venta
            
            ItemPedidoMercado.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio
            )
            total_pedido += precio * cantidad
            
        pedido.total = total_pedido
        pedido.save()

        # --- Notificación Discord (aquí tenemos total e items correctos) ---
        try:
            from orders.utils import send_discord_notification
            items_reales = pedido.items.select_related('producto').all()
            lineas_items = "\n".join(
                f"• {item.cantidad}x {item.producto.nombre if item.producto else '?'} — {item.precio_unitario} €"
                for item in items_reales
            )
            title = f"📦 Nuevo Pedido Mercado Negro #{pedido.id}"
            description = (
                f"Se ha registrado una nueva venta para **{pedido.organizacion.nombre}**.\n\n"
                f"**Productos solicitados:**\n{lineas_items or 'Sin detalle'}"
            )
            fields = [
                {"name": "Solicitante", "value": pedido.usuario.username, "inline": True},
                {"name": "Total Transacción", "value": f"{pedido.total} €", "inline": True},
                {"name": "Estado", "value": pedido.get_estado_display(), "inline": True},
            ]
            admin_url = f"https://koienterprise.onrender.com/admin/orders/pedidomercado/{pedido.id}/change/"
            send_discord_notification('mn', title, description, fields, url=admin_url)
        except Exception:
            pass  # Nunca bloquear la compra por un fallo de Discord
        # ------------------------------------------------------------------

        request.session['cart'] = {}
        messages.success(request, "Pago procesado y pedido enviado a la red con éxito.")
        return redirect('mi_organizacion')

    return redirect('ver_carrito')
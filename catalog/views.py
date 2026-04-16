from django.shortcuts import render
from .models import Plato, Categoria

def home_view(request):
    platos_destacados = Plato.objects.filter(es_destacado=True, disponible=True)
    return render(request, 'home.html', {'platos': platos_destacados})

def restaurante_view(request):
    return render(request, 'restaurante.html')

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
        return render(request, 'mercado_negro.html', {'categorias': categorias, 'productos': productos})
    messages.error(request, "Acceso Denegado. Solo organizaciones autorizadas pueden acceder al Mercado Negro.")
    return redirect('/')

@login_required
def agregar_carrito(request, producto_id):
    if not (getattr(request.user, 'organization', None) and request.user.organization.es_ilegal):
        return redirect('/')
    
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id)
        cantidad = int(request.POST.get('cantidad', 1))
        
        cart = request.session.get('cart', {})
        if str(producto_id) in cart:
            cart[str(producto_id)]['cantidad'] += cantidad
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
        
        request.session['cart'] = {}
        messages.success(request, "Pago procesado y pedido enviado a la red con éxito.")
        return redirect('mi_organizacion')
        
    return redirect('ver_carrito')
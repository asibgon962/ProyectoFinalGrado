from django.shortcuts import render
from django.views.decorators.cache import never_cache
from .models import Plato, Categoria, BannerNormal, BannerMercadoNegro, OfertaMercado, OfertaServicio, Cupon
from django.http import JsonResponse

def validar_cupon_ajax(request):
    codigo = request.GET.get('codigo', '').strip().upper()
    cupon = Cupon.objects.filter(codigo=codigo, activo=True).first()
    if cupon and cupon.es_valido():
        return JsonResponse({
            'valido': True,
            'id': cupon.id,
            'tipo': cupon.tipo,
            'valor': float(cupon.valor),
            'mensaje': f"Cupón '{codigo}' aplicado con éxito."
        })
    return JsonResponse({'valido': False, 'mensaje': 'Cupón inválido, expirado o agotado.'})

@never_cache
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
    total_individual = Decimal('0.00')
    
    for p_id, item_data in cart.items():
        precio = Decimal(item_data['precio_venta'])
        subtotal = precio * item_data['cantidad']
        total_individual += subtotal
        items_carrito.append({
            'producto_id': p_id,
            'nombre': item_data['nombre'],
            'precio': precio,
            'cantidad': item_data['cantidad'],
            'subtotal': subtotal
        })

    # --- Lógica de Ofertas Automáticas ---
    oferta_aplicada = None
    descuento_oferta = Decimal('0.00')
    
    # Prioridad 1: Oferta seleccionada por banner
    oferta_id = request.session.get('oferta_id_mn')
    if oferta_id:
        oferta_aplicada = OfertaMercado.objects.filter(id=oferta_id, activo=True).first()
    
    # Prioridad 2: Detección automática si no hay una seleccionada
    if not oferta_aplicada:
        ofertas_auto = OfertaMercado.objects.filter(activo=True, auto_aplicar=True).prefetch_related('items__producto')
        for off in ofertas_auto:
            es_valida = True
            for item in off.items.all():
                p_id = str(item.producto.id)
                # Debe estar el producto y tener al menos la cantidad requerida
                if p_id not in cart or cart[p_id]['cantidad'] < item.cantidad:
                    es_valida = False
                    break
            if es_valida:
                oferta_aplicada = off
                break

    if oferta_aplicada:
        # Calculamos cuánto costarían esos productos por separado (con las cantidades de la oferta)
        coste_base_pack = sum(item.producto.precio_venta * item.cantidad for item in oferta_aplicada.items.all())
        # El ahorro es la diferencia
        descuento_oferta = coste_base_pack - oferta_aplicada.precio_total
        if descuento_oferta < 0: descuento_oferta = Decimal('0.00')

    # --- Lógica de Cupones ---
    cupon_aplicado = None
    descuento_cupon = Decimal('0.00')
    cupon_id = request.session.get('cupon_id')
    if cupon_id:
        cupon_obj = Cupon.objects.filter(id=cupon_id).first()
        if cupon_obj and cupon_obj.es_valido():
            cupon_aplicado = cupon_obj
            if cupon_obj.tipo == 'PORCENTAJE':
                descuento_cupon = (total_individual - descuento_oferta) * (cupon_obj.valor / 100)
            else:
                descuento_cupon = cupon_obj.valor

    total_final = total_individual - descuento_oferta - descuento_cupon
    if total_final < 0: total_final = Decimal('0.00')

    context = {
        'items_carrito': items_carrito,
        'total_individual': total_individual,
        'descuento_oferta': descuento_oferta,
        'oferta_aplicada': oferta_aplicada,
        'cupon_aplicado': cupon_aplicado,
        'descuento_cupon': descuento_cupon,
        'total_final': total_final,
    }
        
    return render(request, 'carrito.html', context)

@login_required
def aplicar_oferta_mercado(request, oferta_id):
    if not (getattr(request.user, 'organization', None) and request.user.organization.es_ilegal):
        return redirect('/')
    
    oferta = get_object_or_404(OfertaMercado, id=oferta_id, activo=True)
    cart = request.session.get('cart', {})
    
    # Añadimos los productos de la oferta con sus cantidades correspondientes
    for item in oferta.items.all():
        p_id = str(item.producto.id)
        if p_id in cart:
            # Si ya está, nos aseguramos de que tenga al menos la cantidad de la oferta
            if cart[p_id]['cantidad'] < item.cantidad:
                cart[p_id]['cantidad'] = item.cantidad
        else:
            cart[p_id] = {
                'nombre': item.producto.nombre,
                'precio_venta': str(item.producto.precio_venta),
                'cantidad': item.cantidad
            }
    
    request.session['cart'] = cart
    request.session['oferta_id_mn'] = oferta.id
    messages.success(request, f"¡Oferta '{oferta.titulo}' aplicada al carrito!")
    return redirect('ver_carrito')

@login_required
def aplicar_cupon(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip().upper()
        cupon = Cupon.objects.filter(codigo=codigo, activo=True).first()
        if cupon and cupon.es_valido():
            request.session['cupon_id'] = cupon.id
            messages.success(request, f"Cupón '{codigo}' aplicado con éxito.")
        else:
            messages.error(request, "Cupón inválido, expirado o agotado.")
    return redirect('ver_carrito')

@login_required
def aplicar_oferta_servicio(request, oferta_id):
    oferta = get_object_or_404(OfertaServicio, id=oferta_id, activo=True)
    # Redirigimos al formulario con la oferta en la URL
    return redirect(f"/solicitar/?oferta_id={oferta.id}")

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
            
        # --- Gestión de Descuentos ---
        descuento_total = Decimal('0.00')
        oferta_id = request.session.get('oferta_id_mn')
        oferta_obj = None
        if oferta_id:
            oferta_obj = OfertaMercado.objects.filter(id=oferta_id, activo=True).first()
            if oferta_obj:
                coste_base = sum(item.producto.precio_venta * item.cantidad for item in oferta_obj.items.all())
                descuento_total += (coste_base - oferta_obj.precio_total)

        cupon_id = request.session.get('cupon_id')
        cupon_obj = None
        if cupon_id:
            cupon_obj = Cupon.objects.filter(id=cupon_id).first()
            if cupon_obj and cupon_obj.es_valido():
                if cupon_obj.tipo == 'PORCENTAJE':
                    descuento_total += (total_pedido - descuento_total) * (cupon_obj.valor / 100)
                else:
                    descuento_total += cupon_obj.valor
                
                # Consumir uso del cupón
                cupon_obj.usos_actuales += 1
                cupon_obj.save()

        pedido.total = max(Decimal('0.00'), total_pedido - descuento_total)
        pedido.descuento_total = descuento_total
        pedido.oferta_aplicada = oferta_obj
        pedido.cupon_aplicado = cupon_obj
        pedido.save()

        # Limpiar sesión
        request.session['oferta_id_mn'] = None
        request.session['cupon_id'] = None

        # --- Notificación Discord (aquí tenemos total e items correctos) ---
        try:
            from orders.utils import send_discord_notification, formato_europeo, generar_links_accion
            items_reales = pedido.items.select_related('producto').all()
            lineas_items = "\n".join(
                f"• {item.cantidad}x {item.producto.nombre if item.producto else '?'} — {formato_europeo(item.precio_unitario)} €"
                for item in items_reales
            )
            title = f"📦 Nuevo Pedido Mercado Negro #{pedido.id}"
            description = (
                f"Se ha registrado una nueva venta para **{pedido.organizacion.nombre}**.\n\n"
                f"**Productos solicitados:**\n{lineas_items or 'Sin detalle'}"
            )
            fields = [
                {"name": "Solicitante", "value": pedido.usuario.username, "inline": True},
                {"name": "Total Transacción", "value": f"{formato_europeo(pedido.total)} €", "inline": True},
                {"name": "Estado", "value": pedido.get_estado_display(), "inline": True},
            ]

            # ── Links de acción firmados ─────────────────────────────────────────
            links = generar_links_accion('mercado', pedido.id)
            links_texto = "  ·  ".join(f"[{l['label']}]({l['url']})" for l in links)
            fields.append({"name": "⚡ Cambiar estado", "value": links_texto, "inline": False})
            # ───────────────────────────────────────────────────────────────

            admin_url = f"https://koienterprise.onrender.com/admin/orders/pedidomercado/{pedido.id}/change/"
            send_discord_notification('mn', title, description, fields, url=admin_url)
        except Exception:
            pass  # Nunca bloquear la compra por un fallo de Discord
        # ------------------------------------------------------------------

        request.session['cart'] = {}
        messages.success(request, "Pago procesado y pedido enviado a la red con éxito.")
        return redirect('mi_organizacion')

    return redirect('ver_carrito')
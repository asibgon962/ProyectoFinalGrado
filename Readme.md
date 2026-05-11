# KOIENTERPRISE - Proyecto Final de Grado (KOI278963)

> **Aviso de Responsabilidad / Disclaimer:**
> Este proyecto ha sido desarrollado exclusivamente con fines académicos como **Trabajo de Final de Grado (TFG)**. La temática del sitio se enmarca estrictamente dentro del ecosistema de un **Juego de Rol**. Todo el contenido comercializado, entidades mencionadas y servicios ofrecidos son completamente ficticios y no tienen representatividad alguna en la realidad.

---

## 1. Introducción y Contexto

**KOIENTERPRISE** es una plataforma web desarrollada para simular y agilizar un ecosistema comercial interactivo dentro de un Juego de Rol. El proyecto proporciona una interfaz en la que los distintos participantes pueden interactuar con productos de diversas categorías, gestionar un inventario de artículos y participar en una experiencia inmersiva.

### 1.1 Objetivos del Proyecto

* **Centralizar** la gestión del mercado de manera automatizada.
* **Proveer** un sistema seguro y robusto de autenticación y organización por grupos.
* **Garantizar** una navegación fluida e inmersiva gracias a un diseño visual atractivo y el uso de animaciones avanzadas.
* **Aplicar** conocimientos avanzados sobre backend, ciberseguridad, y buenas prácticas de SEO y rendimiento web para entornos productivos.

---

## 2. Stack Tecnológico y Herramientas

### 2.1 Backend

* **Python 3.12** — Lenguaje principal de programación.
* **Django 6.0** — Framework MTV para la estructura de la aplicación.
* **Django Channels ≥ 4.0** — Soporte para conexiones asíncronas y WebSockets.
* **Daphne ≥ 4.0** — Servidor ASGI que sustituye a Gunicorn para soportar el protocolo HTTP/2 y WebSockets en producción.
* **Gunicorn** — Mantenido en requirements como fallback WSGI.

### 2.2 Base de Datos y Almacenamiento

* **PostgreSQL** — En producción mediante **Neon** (serverless PostgreSQL).
* **SQLite3** — Para el entorno de desarrollo y pruebas en local.
* **Cloudinary** — Integración mediante `django-cloudinary-storage` para almacenamiento, entrega y procesamiento de ficheros multimedia (imágenes estáticas y subidas de usuario).

### 2.3 Frontend & Diseño

* **HTML5 y CSS3 Vanilla** — Estructuración y diseño con animaciones fluidas, paleta de colores oscura y dorada con efectos de paralaje.
* **Bootstrap 5** — Grid, utilidades y componentes base.
* **JavaScript** — Control de interactividad y peticiones asíncronas (validación de cupones vía AJAX).
* **Jazzmin** — Panel de administración de Django personalizado con tema oscuro.
* **Diseño Responsivo (Mobile First)** — Adaptación correcta desde móviles a monitores Ultrawide.

### 2.4 Integraciones Externas

* **Discord Webhooks** — Notificaciones automáticas al canal de administración cuando se registra un nuevo pedido o solicitud de servicio.
* **Links de acción HMAC firmados** — Los mensajes de Discord incluyen botones que permiten al administrador cambiar el estado del pedido directamente desde Discord, validados criptográficamente para prevenir manipulaciones.

---

## 3. Arquitectura y Estructura del Software

El sistema divide las responsabilidades de negocio en las siguientes aplicaciones Django:

| App | Responsabilidad |
|-----|----------------|
| 📁 `core/` | Configuración central, URLs globales, procesadores de contexto y páginas estáticas. |
| 📁 `catalog/` | Catálogo de platos y productos del Mercado Negro. Gestión de categorías, ofertas, cupones y banners promocionales. |
| 📁 `orders/` | Ciclo de vida del carrito (añadir/eliminar/checkout), gestión de solicitudes de servicio, chats integrados y lógica de descuentos. |
| 📁 `users/` | Autenticación, registro, perfil de usuario, organizaciones (grupos de rol) y mensajes de contacto. |

---

## 4. Funcionalidades Principales

### 4.1 Autenticación e Identidad de Usuario
* Login, registro y restablecimiento seguro de contraseña (SMTP).
* Perfil de personaje personalizable con avatar (sistema o imagen propia).
* Vinculación a **Organizaciones** mediante código de grupo secreto. Si el usuario elimina el código de su perfil, se desvincula automáticamente.

### 4.2 Sistema de Catálogo y Mercado Negro
* Catálogo de platos (restaurante) y productos (Mercado Negro) organizados por categorías con orden configurable.
* Vista del Mercado Negro restringida a usuarios pertenecientes a organizaciones de tipo "ilegal".
* Carrito de sesión con control de cantidad máxima por producto.

### 4.3 Sistema de Ofertas y Cupones
* **Ofertas de Mercado Negro:** Packs de productos con precio especial, aplicables manualmente desde banners o de forma automática al detectar los productos requeridos en el carrito.
* **Ofertas de Servicio:** Packs de platos para eventos, aplicables desde banners.
* **Cupones de descuento:** Por porcentaje o importe fijo. Control de usos máximos totales y por usuario. Validación en tiempo real vía AJAX.

### 4.4 Sistema de Banners Promocionales
* Banners configurables desde el admin (título, subtítulo, imagen, enlace u oferta asociada).
* Carrusel automático para la home y el Mercado Negro.
* Tipos separados: `BannerNormal` (home/menú) y `BannerMercadoNegro`.

### 4.5 Gestión de Pedidos y Solicitudes de Servicio
* Creación de pedidos del Mercado Negro con desglose de descuentos aplicados.
* Solicitudes de servicio (eventos, transporte) con cálculo de precio basado en ítems seleccionados.
* Panel de organización para seguimiento del estado de pedidos.
* Chat en tiempo real integrado entre usuario y administración.

### 4.6 Notificaciones Discord con Acciones Firmadas
* Notificación automática al procesar una compra o solicitud de servicio.
* Los mensajes incluyen el detalle del pedido, total y links de acción.
* Los links permiten cambiar el estado directamente desde Discord, firmados con HMAC-SHA256 para evitar manipulaciones externas.

### 4.7 Panel de Administración
* Tema visual personalizado con **Jazzmin**.
* `RecetaInline` para gestionar ingredientes de platos directamente desde su ficha.
* Visualización de margen bruto por plato y producto con código de colores (verde/rojo).
* Vista previa de banners en la lista del admin.

---

## 5. Seguridad y SEO

* **Evaluación STRIDE** en partes críticas (carrito, subida de multimedia, cambio de estado vía tokens).
* **Certificados SSL** y configuraciones `CSRF_COOKIE_SECURE` y `SESSION_COOKIE_SECURE` activas en producción.
* **Links de acción HMAC** con caducidad temporal para prevenir replay attacks.
* **SEO:** `robots.txt`, metaetiquetas Open Graph, jerarquía semántica `<h1>`/`<h2>` y optimización de contraste (A11y).

---

## 6. Producción y Despliegue (Render)

La aplicación está desplegada en **Render** (PaaS) con la siguiente configuración:

| Parámetro | Valor |
|-----------|-------|
| **Servidor** | `daphne -b 0.0.0.0 -p $PORT core.asgi:application` |
| **Build** | `build.sh` (pip install + collectstatic + migrate con reintentos) |
| **Base de datos** | Neon PostgreSQL (serverless) |
| **Almacenamiento de medios** | Cloudinary |
| **Auto-Deploy** | On Commit (rama `main`) |

> El script `build.sh` reintenta `migrate` hasta 5 veces con espera de 10 segundos entre intentos para tolerar el arranque lento de la base de datos serverless de Neon.

---

*Desarrollado para KOIENTERPRISE - 2026.*

# KOIENTERPRISE - Proyecto Final de Grado (KOI278963)

> **Aviso de Responsabilidad / Disclaimer:** 
> Este proyecto ha sido desarrollado exclusivamente con fines académicos como **Trabajo de Final de Grado (TFG)**. La temática del sitio se enmarca estrictamente dentro del ecosistema de un **Juego de Rol**. Todo el contenido comercializado, entidades mecionadas y servicios ofrecidos son completamente ficticios y no tienen representatividad alguna en la realidad.

---

## 1. Introducción y Contexto

**KOIENTERPRISE** es una plataforma web desarrollada para simular y agilizar un ecosistema comercial interactivo dentro de un Juego de Rol. El proyecto proporciona una interfaz en la que los distintos participantes pueden interactuar con productos de diversas categorías, gestionar e interaccionar con un inventario de artículos e integrarse en una experiencia inmersiva.

### 1.1 Objetivos del Proyecto
* **Centralizar** la gestión del mercado de manera automatizada.
* **Proveer** un sistema seguro y robusto de autenticación.
* **Garantizar** una navegación fluida e inmersiva gracias a un diseño visual atractivo y el uso de animaciones avanzadas.
* **Aplicar** conocimientos avanzados sobre backend, ciberseguridad, y buenas prácticas de SEO y rendimiento web para entornos productivos.

---

## 2. Stack Tecnológico y Herramientas

Para el desarrollo de KOIENTERPRISE, se ha hecho uso de tecnologías de vanguardia siguiendo los estándares convencionales del desarrollo full-stack:

### 2.1 Backend 
* **Python 3:** Lenguaje principal de programación.
* **Django:** Framework MTV utilizado para generar la robusta estructura de la aplicación.
* **Gunicorn:** Servidor HTTP WSGI para la puesta en producción.

### 2.2 Base de Datos y Almacenamiento
* **PostgreSQL:** (En producción mediante el entorno de despliegue).
* **SQLite3:** Para el entorno de desarrollo y pruebas en local.
* **Cloudinary:** Integración implementada mediante la librería `django-cloudinary-storage` para garantizar el almacenamiento, entrega y procesamiento de ficheros multimedia (imágenes estáticas y subidas de usuario).

### 2.3 Frontend & Diseño
* **HTML5 y CSS3 Vanilla:** Estructuración y diseño aplicando animaciones fluidas, paleta de colores inmersiva (tonalidades oscuras y doradas) con efectos paralaje.
* **JavaScript:** Control avanzado de interactividad y manejo asíncrono en ciertos componentes.
* **Diseño Responsivo (Mobile First):** Garantizando el correcto redimensionado desde teléfonos móviles a monitores Ultrawide.

---

## 3. Arquitectura y Estructura del Software

El sistema divide fuertemente las responsabilidades de negocio implementando las siguientes aplicaciones nativas en Django:

* 📁 **`core/`**: Aplicación encargada de la vista principal (Home/Menú principal) y de la lógica central (Ej. páginas estáticas sobre nosotros, enlaces corporativos).
* 📁 **`catalog/`**: Eje principal del catálogo. Controla los modelos de productos, marcas en venta y clasificación por categorías, brindando funciones de filtrado.
* 📁 **`orders/`**: Controla el ciclo de vida del carrito (Añadir/Eliminar/Checkout), gestionando el modelo transaccional.
* 📁 **`users/`**: Encargada del proceso de autenticación, el registro de usuarios, reseteos de contraseñas y paneles de perfil (perfil del personaje en el ROL).

---

## 4. Funcionalidades Principales Desarrolladas

1. **Autenticación e Identidad de Usuario:**
   * Login, Interfaz de validación de correos electrónicos.
   * Sistema de reinicio seguro de contraseñas (uso de SMTP).
2. **Exploración de Catálogo (Mercado Negro / General):**
   * El sistema está provisto de categorías principales (Equipamiento, Vehículos, etc.), presentadas de manera elegante.
3. **Gestión de Carrito y Checkout:**
   * Operatoria atómica para garantizar y registrar el encargo.
4. **Chat Integrado:**
   * Solución de comunicación integrado en la plataforma.
5. **Estética y Visuales - Sistema de Banners Promocionales y Paralaje:**
   * Animaciones en CSS persistentes (Trazas de linternas, divisores con estética visual propia).

---

## 5. Prevención de Vulnerabilidades, Seguridad y SEO

El proyecto implementa un estricto control sobre optimización y seguridad:

* **Evaluación STRIDE:** Revisión implementada en partes críticas como el carrito y la subida de elementos multimedia para evitar Inyección de SQL, Spoofing de identidad, Manipulación de datos y exposición inintencionada.
* **Certificados SSL y Entorno Seguro.** Controlado en Cloud y mediante configuraciones `CSRF_COOKIE_SECURE` y `SESSION_COOKIE_SECURE`.
* **Mejoras SEO / Web Semántica:**  
   * Incorporación de archivos de indexado `robots.txt` y `sitemap.xml` para regularidad de visibilidad en índices de búsquedas e interacciones con bots.
   * Modificación de estructuras HTML usando Metaetiquetas e información estandarizada de jerarquía (`<h1>`, `<h2>`).
   * Optimización y resolución de errores severos de Contraste para la accesibilidad web (A11y).

---

## 6. Producción y Servidores (Despliegue)

La aplicación **ha sido empaquetada y desplegada íntegramente en Render**. Se han eliminado las tareas inherentes a despliegues locales al automatizar el proceso:
   * **Servidor de la Aplicación:** Se ha configurado usando `Gunicorn`. Render es el proveedor PAAS principal.
   * El archivo de requisitos `requirements.txt` y el script `.sh` garantizan la recolección de archivos estáticos y configuraciones de migración cada vez que se envía una nueva versión.
   * El sistema usa un Script de "Ping Keep-Alive" contra un Endpoint especial para evitar que la capa gratuita se duerma en ningún momento, garantizando acceso directo.

---
*Desarrollado para KOIENTERPRISE - 2026.*

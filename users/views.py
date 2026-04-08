from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
# Importamos ambos formularios desde tu archivo .form
from .form import RegistroUsuarioForm, EditarPerfilForm 
from .models import Organization, Profile

# --- VISTA DE REGISTRO ---
def register_view(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            # 1. Creamos el usuario pero no lo guardamos en DB todavía
            user = form.save(commit=False)
            
            # 2. Sacamos los datos limpios del formulario
            id_form = form.cleaned_data.get('id_code')
            tel_form = form.cleaned_data.get('telefono')
            cod_org = form.cleaned_data.get('codigo_empresa')

            # 3. Asignamos el ID Code al User
            user.id_code = id_form
            
            # 4. Intentamos vincular la Organización por su código
            if cod_org:
                try:
                    org = Organization.objects.get(codigo_grupo=cod_org)
                    user.organization = org
                except Organization.DoesNotExist:
                    pass # Si no existe, se queda sin organización
            
            # 5. Guardamos el User (esto dispara el signal del Profile)
            user.save()

            # 6. Actualizamos el teléfono en el Profile recién creado
            profile = user.profile
            profile.telefono = tel_form
            profile.save()

            return redirect('login') 
    else:
        form = RegistroUsuarioForm()
    
    return render(request, 'registration/register.html', {'form': form})


# --- VISTA DE PERFIL (VER) ---
@login_required
def profile_view(request):
    # Obtenemos el perfil del usuario actual
    profile = request.user.profile
    return render(request, 'profile.html', {'profile': profile})


# --- VISTA DE EDITAR PERFIL ---
@login_required
def editar_perfil_view(request):
    profile = request.user.profile
    user = request.user
    
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Lógica del Código de Empresa
            nuevo_codigo = form.cleaned_data.get('codigo_grupo')
            if nuevo_codigo:
                try:
                    org = Organization.objects.get(codigo_grupo=nuevo_codigo)
                    user.organization = org
                    user.save()
                except Organization.DoesNotExist:
                    # Opcional: añadir un mensaje de error si el código no existe
                    pass

            # Lógica de Avatares Predefinidos
            option = request.POST.get('avatar_option')
            if not request.FILES.get('avatar'):
                if option == 'masculino':
                    profile.avatar = 'avatars/masculino.jpg'
                elif option == 'femenino':
                    profile.avatar = 'avatars/femenino.jpg'
            
            form.save()
            return redirect('profile') # Asegúrate que coincida con tu urls.py
    else:
        # Pre-cargamos el código actual si el usuario ya tiene organización
        inicial = {}
        if user.organization:
            inicial['codigo_grupo'] = user.organization.codigo_grupo
        form = EditarPerfilForm(instance=profile, initial=inicial)
    
    return render(request, 'editar_perfil.html', {'form': form})

def privacidad(request):
    return render(request, 'privacidad.html')

def terminos(request):
    return render(request, 'terminos.html')

def contacto(request):
    return render(request, 'contacto.html')
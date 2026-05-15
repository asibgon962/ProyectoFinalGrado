from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from catalog.models import Plato

from .form import RegistroUsuarioForm, EditarPerfilForm, ContactoForm
from django.contrib import messages

from .models import Organization, Profile


def register_view(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            id_form = form.cleaned_data.get('id_code')
            tel_form = form.cleaned_data.get('telefono')
            cod_org = form.cleaned_data.get('codigo_empresa', '').strip() if form.cleaned_data.get('codigo_empresa') else None

            user.id_code = id_form
            

            if cod_org:
                try:
                    org = Organization.objects.get(codigo_grupo=cod_org)
                    user.organization = org
                except Organization.DoesNotExist:
                    pass
            
            user.save()
            profile = user.profile
            profile.telefono = tel_form
            profile.save()

            return redirect('login') 
    else:
        form = RegistroUsuarioForm()
    
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile_view(request):
    profile = request.user.profile
    return render(request, 'profile.html', {'profile': profile})



@login_required
def editar_perfil_view(request):
    profile = request.user.profile
    user = request.user
    
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():

            nuevo_codigo = form.cleaned_data.get('codigo_grupo', '').strip() if form.cleaned_data.get('codigo_grupo') else None
            if nuevo_codigo:
                try:
                    org = Organization.objects.get(codigo_grupo=nuevo_codigo)
                    user.organization = org
                    user.save()
                except Organization.DoesNotExist:
                    pass
            else:

                if user.organization:
                    user.organization = None
                    user.save()


            option = request.POST.get('avatar_option')
            if not request.FILES.get('avatar'):
                if option == 'masculino':
                    profile.avatar = 'avatars/masculino.jpg'
                elif option == 'femenino':
                    profile.avatar = 'avatars/femenino.jpg'
            
            form.save()
            return redirect('profile')
    else:

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
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Debes iniciar sesión para enviar una consulta.")
            return redirect('login')

        form = ContactoForm(request.POST)
        if form.is_valid():

            msj = form.save(commit=False)
            msj.nombre = request.user.username
            msj.save()
            messages.success(request, "Tu solicitud ha sido enviada correctamente. Te contactaremos pronto.")
            return redirect('contacto')
        else:
            messages.error(request, "Hubo un error en tu formulario.")
    return render(request, 'contacto.html')

def servicios(request):
    return render(request, 'servicios.html')


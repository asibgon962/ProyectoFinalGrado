from django.shortcuts import render, redirect
from .form import RegistroUsuarioForm
from .models import Organization, Profile

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

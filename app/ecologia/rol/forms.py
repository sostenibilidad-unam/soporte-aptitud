# -*- coding: utf-8 -*-
from django.utils.encoding import smart_str, smart_unicode
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Permission, Group
from rol.models import UserProfile
from lib.D import PERMISSION as P, ROL as R

"""
error_messages 
invalid
required
"""

class NewUserForm(UserCreationForm):
        
    error_messages = {'invalid':"El campo no es valido", 'required':"El campo es requerido"}    
    
    username = forms.CharField(label="*Nombre de usuario:", error_messages=error_messages, max_length=30, widget=forms.TextInput())    
    first_name = forms.CharField(label="*Nombre:", error_messages=error_messages, max_length=30, widget=forms.TextInput())
    last_name = forms.CharField(label="*Apellido:", required=True, error_messages=error_messages, max_length=30, widget=forms.TextInput())
    charge = forms.CharField(label="*Cargo:", required=True, error_messages=error_messages, max_length=100, widget=forms.TextInput())
    company = forms.CharField(label="*Institución/Empresa:", required=True, error_messages=error_messages, max_length=100, widget=forms.TextInput())
    password1 = forms.CharField(label="*Contraseña:", error_messages=error_messages, widget=forms.PasswordInput())
    password2 = forms.CharField(label="*Confirmar contraseña:", error_messages=error_messages, widget=forms.PasswordInput())
    email = forms.EmailField(label="*Email", error_messages=error_messages, widget=forms.TextInput())
    rol = forms.CharField(label="*Rol", widget=forms.Select(choices=[]))
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', "password1", "password2", "email", "rol")
    
    def __init__(self, *args, **kwargs):
        self.rol = kwargs.pop('rol', None)
        super(NewUserForm, self).__init__(*args, **kwargs)    
    
        cho_root = ((P.ROOT2, 'Root2'),)        
        cho_root2 = (
               (P.ADMIN, 'Responsable de estudio técnico'),
               (P.SUPERVISOR, 'Supervisor'),
        )        
        cho_admin = (
               (P.OPERADOR, 'Operador'),
               #(P.OPERADOR_PRIVILEGIOS, 'Operador(grupo mapa aptitud)'),
        )    
        if self.rol == R.ROOT:
            self.fields['rol'].widget = forms.Select(choices=cho_root)
            # escondemos los campos que no son necesarios para este rol
            self.fields['charge'] = forms.CharField(widget=forms.HiddenInput(), label='',required=False)
            self.fields['company'] = forms.CharField(widget=forms.HiddenInput(), label='',required=False)
        elif self.rol == R.ROOT2:            
            self.fields['rol'].widget = forms.Select(choices=cho_root2)
        elif self.rol == R.ADMIN:            
            self.fields['rol'].widget = forms.Select(choices=cho_admin)
            # escondemos los campos que no son necesarios para este rol
            self.fields['charge'] = forms.CharField(widget=forms.HiddenInput(), label='',required=False)
            self.fields['company'] = forms.CharField(widget=forms.HiddenInput(), label='',required=False)
            
    
     
    def clean_username(self):
        username = self.cleaned_data["username"]        
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            if len(username) < 4 and len(username)<=20:
                raise forms.ValidationError("Debes usar entre 4 y 20 caracteres.")
            else:
                return username
        raise forms.ValidationError("El nombre de usuario está ocupado")
    
        
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError("La contraseña de confirmación no coincide")
        return password2

    def save(self, grupo,commit=True):
        username = self.cleaned_data['username']
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        password = self.cleaned_data["password1"]
        email = self.cleaned_data['email']
        rol = self.cleaned_data['rol']
        charge = self.cleaned_data['charge']
        company = self.cleaned_data['company']
        
        if commit:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()    
            perm = Permission.objects.get(codename=rol)   
            user.user_permissions.add(perm)            
            if self.rol == R.ROOT2:
                userProfile = UserProfile(charge=charge,company=company,user=user);
                userProfile.save()
            # crear grupo
            if rol == P.ROOT2 or rol == P.ADMIN:  
                Group(name=user.username).save() 
                
            #add usuario al grupo correspondiente            
            if self.rol == R.ROOT2 or self.rol == R.ADMIN:
                grp = Group.objects.get(name=grupo)
                user.groups.add(grp)
                
            
        return user
    def getUsr(self):        
        return "El usuario \"" + self.cleaned_data['username'] + "\" se " + smart_unicode("creó") + " satisfactoriamente"










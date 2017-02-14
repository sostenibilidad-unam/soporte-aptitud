# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.template import Library
from lib.D import ROL
from ordenamiento.models import User_Programa_Sector
register = Library()


@register.filter
def getRol(id):    
    usr = User.objects.get(id=id)
    
    if usr.has_perm(ROL.ROOT):        
        rol = "root"
    elif usr.has_perm(ROL.ROOT2):
        rol = "root 2"

    elif usr.has_perm(ROL.ADMIN):        
        rol = "Administrador"

    elif usr.has_perm(ROL.SUPERVISOR):        
        rol = "Supervisor"

    elif usr.has_perm(ROL.OPERADOR):
        rol = "Operador"
    elif usr.has_perm(ROL.OPERADOR_PRIVILEGIOS):
        rol = "Operador(grupo mapa aptitud)"
    
        
    return rol 

@register.filter
def getUsr(id):   
    if id.isdigit():
        usr = User.objects.get(id=id)
        return usr.username
    else:
        return ""
    
@register.filter
def getFullUsrName(id):   
    if id.isdigit():
        usr = User.objects.get(id=id)
        return usr.first_name + " " + usr.last_name
    else:
        return ""
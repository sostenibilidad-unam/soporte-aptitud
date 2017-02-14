# -*- coding: utf-8 -*-
from django.utils.encoding import smart_str, smart_unicode
from django.contrib.admin.templatetags.admin_list import results
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils import simplejson
from lib import U
from lib.D import ROL
from lib.U import *
from django.db.models.query_utils import Q
from lib.D import PERMISSION as P
from ordenamiento.models import Sector, User_Programa_Sector, Programa
from programa.forms import ProgramaForm, ProgramaSelect, AsignarForm, SeleccionaProgramaForm
from rol.forms import NewUserForm
import lib.GrassShell as gsh
import programa.querys as q
from lib import journal        

@login_required
def programa(request):    
    html = "app/programa.html"
    rol = getUsrRol(request)
    grupo = getUsr(request).username
    id_usr = getUsrId(request)
    arg = {}
    TAB_ALTA_USUARIOS = 'rad_crear';
    TAB_ALTA_PROCESOS = 'rad_ver';
    
    #programa=q.getCountPrograma(id)
        
    if rol == ROL.ROOT2:      
           
        if request.method == 'POST':
            if "location" in request.POST:
                p = ProgramaForm(request.POST, grupo=grupo)        
                arg["tab_id"] = TAB_ALTA_PROCESOS        
                if p.is_valid():
                    p.save(id_usr)
                    
                    #save program creation acction in journal   
                    detalles = 'program ' + request.POST['nombre'] + ' created'
                    journal.registerActionProgramCreated(request, detalles)                    
                    
                    arg['program_saved'] = "El proceso \"" + request.POST['nombre'] + "\" se " + smart_unicode("creó") + " satisfactoriamente"            
                    arg["fprograma"] = ProgramaForm(grupo=grupo)
                    arg["frol"] = NewUserForm(rol=rol)
                else:
                    arg["fprograma"] = p
                    arg["frol"] = NewUserForm(rol=rol)                                    
                
            if "rol" in request.POST:
                f = NewUserForm(request.POST, rol=rol)
                arg["tab_id"] = TAB_ALTA_USUARIOS                
                if f.is_valid():
                    f.save(grupo)
                    
                    newUserName = f.cleaned_data['username'] 
                    newUserRol = f.cleaned_data['rol']
                    detalles = "usuario creado:" + newUserName + " rol:" + newUserRol                      
                    journal.registerActionUserCreated(request, detalles)    
                    
                    arg['user_name'] = f.getUsr()  
                    arg["fprograma"] = ProgramaForm(grupo=grupo)
                    arg["frol"] = NewUserForm(rol=rol)                    
                else:
                    arg["frol"] = f
                    arg["fprograma"] = ProgramaForm(grupo=grupo)
                    
        else:
            arg["fprograma"] = ProgramaForm(grupo=grupo)
            arg["frol"] = NewUserForm(rol=rol)
            arg["tab_id"] = TAB_ALTA_USUARIOS
                        
    #if rol == ROL.ADMIN:        
    #    if request.method == 'POST':  
    #        f = NewUserForm(request.POST, rol=rol)
    #        arg["tab_id"] = 1                
    #        if f.is_valid():
    #            f.save(grupo)    
    #            arg['user_name'] = f.getUsr() 
    #            arg["frol"] = NewUserForm(rol=rol)                    
    #        else:
    #            arg["frol"] = f                
    #    else: 
    #        arg["frol"] = NewUserForm(rol=rol)  
    #   
    #    asignar = AsignarForm(grupo=grupo)   
    #    arg["fasignar"] = asignar
         
    
    #prg = Programa.objects.all().order_by('nombre')   
    #arg['prg'] = prg
       
    #programa_select = ProgramaSelect(rol=rol, id_usr=id_usr)
    arg['rol'] = rol
    arg['ROL'] = ROL
    #arg['programa'] = programa_select
        
    return render_to_response(html, arg, context_instance=RequestContext(request))



@U.ajax
def get_programa(request):
    
    msg = {}
    sector = []
    programa = {}
    operador = 0
    
    id_programa = request.POST['id']
    id_usr = U.getUsrId(request)
    
    s = Sector.objects.select_related("sector").filter(sector__user=id_usr, sector__programa=id_programa)
    for _s in s:
        sector.append((_s.id, _s.nombre))
        
    ups = User_Programa_Sector.objects.filter(programa=id_programa, sector=sector[0][0])
    for _ups in ups:
        if _ups.user.has_perm(ROL.OPERADOR) and not _ups.user.is_superuser:            
            operador = _ups.user.id
            
    p = Programa.objects.get(id=id_programa)
    programa['nombre'] = p.nombre
    programa['fecha'] = str(p.fecha_inicio)    
    programa['responsable'] = User.objects.get(id=p.responsable_instituto).username
    programa['location'] = p.location
    
    msg['programa'] = programa
    msg['sector'] = sector
    msg['operador'] = operador
    
    return msg


"""
Asignar Operador Secotr
"""

@U.ajax
def get_operador_sector(request):
    msg = {}
    id_programa = request.POST['id_programa']
    id_sector = request.POST['id_sector']
    operador = 0
    
    ups = User_Programa_Sector.objects.filter(programa=id_programa, sector=id_sector)
    for _ups in ups:
        if _ups.user.has_perm(ROL.OPERADOR) and not _ups.user.is_superuser:            
            operador = _ups.user.id
            
    msg['operador'] = operador
    
    return msg
            

@U.ajax
def set_asignar_sector_operador(request):
    msg = {}
    
    a = AsignarForm(request.POST)                
    if a.is_valid():
        a.save(getUsrId(request))
        
        #save sector assignation action to journal           
        detalles = 'sector id: '+ request.POST['sector'] +' asignado a operador id: ' + request.POST['operador']
        journal.registerActionSectorAssignated(request, detalles)
                    
    msg['success'] = True
    return msg

# Muestra los programas a los que tiene el usuario con el rol asignado
@login_required
def get_programa_por_rol(request):
    html = "app/selecciona_programa.html"
    rol = getUsrRol(request)
    user = getUsr(request)    
    arg = {}
    arg['rol'] = rol
    arg['ROL'] = ROL
    if request.method == 'POST':
        idProgrma = request.POST['programas']
        request.session['admin_selectd_program_id'] = idProgrma
        programa = Programa.objects.get(pk=idProgrma)
        request.session['admin_selectd_program_name'] = programa.nombre
        if rol == ROL.ADMIN:            
            html = "menu/menu.html"
            arg["title"] = "Administracion de procesos de OE"
        elif rol == ROL.OPERADOR:
            return HttpResponseRedirect('/ecologia/ordenamiento/')
        elif rol == ROL.SUPERVISOR:
            return HttpResponseRedirect('/ecologia/ordenamiento/')
    else:        
        #userId =  user.id
        seleccionaProgramaForm = SeleccionaProgramaForm(rol=rol,user=user)
        if len(seleccionaProgramaForm.fields['programas'].widget.choices)==0:
            return HttpResponseRedirect('/ecologia/no_programa/')
        arg['programaForm'] = seleccionaProgramaForm
    return render_to_response(html, arg, context_instance=RequestContext(request))
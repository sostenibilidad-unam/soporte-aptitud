# -*- coding: utf-8 -*-
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Permission, PermissionManager
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from lib.D import MENU, ROL
from lib.U import getUsr
from ordenamiento.models import Rol
import lib.journal as journal


def login(request):   
    
    user = auth.get_user(request) 
    if user.is_active:        
        return HttpResponseRedirect("/ecologia/menu/")    
    else:
        loginResponse = auth.views.login(request)                
        return loginResponse


@login_required
def logout(request):
    auth.logout(request)    
    return HttpResponseRedirect("/ecologia/")
    

@login_required
def menu(request):
    
    html = "menu/menu.html"    
    arg = {"rol":"", "ROL":ROL, "title":"", "MENU":MENU}    
    usr = getUsr(request)    
    
    if usr.has_perm(ROL.ROOT):        
        arg["title"] = "Root"
        arg["rol"] = ROL.ROOT

    elif usr.has_perm(ROL.ROOT2):        
        arg["title"] = "Root 2"
        arg["rol"] = ROL.ROOT2
                
    elif usr.has_perm(ROL.ADMIN):        
        arg["title"] = "Administración de procesos de OE"
        arg["rol"] = ROL.ADMIN
        request.session['rol'] = arg['rol']
        if request.session.get('admin_selectd_program_id',None) == None:        
            return HttpResponseRedirect("/ecologia/seleccionprograma/")
        #else:
        #    programName = request.session['admin_selectd_program_name']
        #    arg["title"] = "Administracion de procesos de OE (" + programName + ")"
            
    elif usr.has_perm(ROL.OPERADOR):        
        arg["title"] = "Operador"
        arg["rol"] = ROL.OPERADOR
        request.session['rol'] = arg['rol']
        #return HttpResponseRedirect('/ecologia/ordenamiento/')
        if request.session.get('admin_selectd_program_id',None) == None:        
            return HttpResponseRedirect("/ecologia/seleccionprograma/")
    elif usr.has_perm(ROL.SUPERVISOR):
        arg["title"] = "Supervisor"
        arg["rol"] = ROL.SUPERVISOR
        request.session['rol'] = arg['rol']
        if request.session.get('admin_selectd_program_id',None) == None:        
            return HttpResponseRedirect("/ecologia/seleccionprograma/")
        
    request.session['rol'] = arg['rol']
    if arg['rol'] == ROL.ROOT or arg['rol'] == ROL.ROOT2:    
        request.session['canSeeProgramName'] = False
    else:
        request.session['canSeeProgramName'] = True
    return render_to_response(html, arg, context_instance=RequestContext(request))

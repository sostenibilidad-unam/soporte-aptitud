# -*- coding:utf-8 -*-
from django.utils.encoding import smart_str, smart_unicode
from django.contrib.admin.templatetags.admin_list import results
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils import simplejson
from lib import U
from lib.D import ROL
from lib.U import *
from django.db.models.query_utils import Q
from lib.D import PERMISSION as P
from ordenamiento.models import Sector, User_Programa_Sector, Programa
from programa.forms import ProgramaForm, ProgramaSelect, AsignarForm
from rol.forms import NewUserForm
from administracion.forms import AdminViewProgramForm
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
import lib.GrassShell as gsh
import programa.querys as q
from lib import journal       
import csv 

# Administracion: procesos y usuarios
@login_required
def administracion(request):
    html = "app/administracion.html"
    arg = {}
    if request.method == 'POST':
        return viewProgram(request);
    rol = getUsrRol(request)
    if rol == ROL.ROOT2:
        # Programas
        prg = Programa.objects.all().order_by('nombre')   
        arg['prg'] = prg
        #Usuarios
        usersAdmin = User.objects.filter(Q(user_permissions__codename=P.ADMIN) | Q(user_permissions__codename=P.SUPERVISOR))
        usersPrograms = [];
        # relacionamos un usuario y los programas a los que esta asignado
        for userAdmin in usersAdmin:
            program = Programa.objects.filter(Q(responsable_autoridad=userAdmin.id) | Q(responsable_instituto=userAdmin.id) | Q(responsable_dgpairs=userAdmin.id) | Q(responsable_ine=userAdmin.id))
            userProgram = UserPrograms(userAdmin,program)
            usersPrograms.append(userProgram) 
            
        arg['usersAdmin'] = usersAdmin
        arg['usersPrograms'] = usersPrograms
        arg["userForm"] = NewUserForm(rol=rol)
        arg["adminViewProgramForm"] = AdminViewProgramForm()
    return render_to_response(html, arg, context_instance=RequestContext(request))

@login_required
def exportExcelPrograms(request):
    html = "app/administracion.html"
    arg = {}
    rol = getUsrRol(request)
    response = HttpResponse(content_type='application/excel')
    response['Content-Disposition'] = 'attachment; filename=procesos_ordenamiento.xls'
    fileHandler = csv.writer(response, delimiter = ' ')
    # headers
    headers = ["Proceso", "Modalidad","Fecha inicio"]
    headersAuroridad = ["(Autoridad responsable del proceso)\nNombre usuario","(Autoridad responsable del proceso)\nNombre","(Autoridad responsable del proceso)\nApellido","(Autoridad responsable del proceso)\nEmail","(Autoridad responsable del proceso)\nCargo","(Autoridad responsable del proceso)\nInstitucion/Empresa"]
    headersInstituto = [smart_str("(Responsable del estudio técnico)\nNombre usuario"),smart_str("(Responsable del estudio técnico)\nNombre"),smart_str("(Responsable del estudio técnico)\nApellido"),smart_str("(Responsable del estudio técnico)\nEmail"),smart_str("(Responsable del estudio técnico)\nCargo"),smart_str("(Responsable del estudio técnico)\nInstitucion/Empresa")]
    headersDgpairs = ["(Responsable en DGPAIRS)\nNombre usuario","(Responsable en DGPAIRS)\nNombre","(Responsable en DGPAIRS)\nApellido","(Responsable en DGPAIRS)\nEmail","(Responsable en DGPAIRS)\nCargo","(Responsable en DGPAIRS)\nInstitucion/Empresa"]
    headersIne = ["(Supervisor)\nNombre usuario","(Supervisor)\nNombre","(Supervisor)\nApellido","(Supervisor)\nEmail","(Supervisor)\nCargo","(Supervisor)\nInstitucion/Empresa"]
    
    headers.extend(headersAuroridad)
    headers.extend(headersInstituto)
    headers.extend(headersDgpairs)
    headers.extend(headersIne)
    fileHandler.writerow(headers)
    if rol == ROL.ROOT2 and request.method == 'POST':        
        programs = Programa.objects.all().order_by('nombre')        
        for programa in programs:            
            
            if programa.responsable_ine:
                ids = [int(programa.responsable_autoridad),int(programa.responsable_instituto),int(programa.responsable_dgpairs),int(programa.responsable_ine)]
            else:
                ids = [int(programa.responsable_autoridad),int(programa.responsable_instituto),int(programa.responsable_dgpairs),None]
                        
            users = User.objects.filter(id__in=ids)            
            row = [smart_str(programa.nombre),smart_str(programa.modalidad),programa.fecha_inicio]
            usersMap = {}
            for user in users:
                usersMap[user.id] = user
            # autoridad responsable del proceso    
            userAutoridad = usersMap[int(programa.responsable_autoridad)]
            # Responsable del estudio técnico:
            userInstituto = usersMap[int(programa.responsable_instituto)]
            # Responsable en DGPAIRS
            userDgpairs = usersMap[int(programa.responsable_dgpairs)]
            # Supervisor
            if programa.responsable_ine:
                userIne = usersMap[int(programa.responsable_ine)]
                                        
            row = helperUserRow(row,userAutoridad)
            row = helperUserRow(row,userInstituto)
            row = helperUserRow(row,userDgpairs)
            
            if programa.responsable_ine:
                row = helperUserRow(row,userIne)
            else:
                row = helperEmptyUserRow(row)
                
            fileHandler.writerow(row)
            
           
            
            
            
            
            
    return response
    #return render_to_response(html, arg, context_instance=RequestContext(request))
def helperUserRow(row,user):
    userProfile = user.get_profile();
    row.append(smart_str(user.username))
    row.append(smart_str(user.first_name))
    row.append(smart_str(user.last_name))
    row.append(smart_str(user.email))
    row.append(smart_str(userProfile.charge))
    row.append(smart_str(userProfile.company))
    return row

def helperEmptyUserRow(row):    
    row.append('')
    row.append('')
    row.append('')
    row.append('')
    row.append('')
    row.append('')
    return row

@login_required
def viewProgram(request):
    program_id = request.POST['programa_id']
    if len(program_id)>0 and program_id.isnumeric(): 
        request.session['admin_selectd_program_id'] = program_id
        request.session['admin_selectd_program_name'] = Programa.objects.get(pk=program_id).nombre        
        return HttpResponseRedirect("/ecologia/ordenamiento/")
    else:
        return HttpResponseRedirect("/ecologia/administracion/")
@U.ajax
def getUser(request):
    #@todo: validate userId be number
    userId = request.GET['userId']
    user = User.objects.get(pk=userId)
    response = {}
    response["id"] = user.id
    response["username"] = user.username 
    response["first_name"] = user.first_name
    response["last_name"] = user.last_name
    response["email"] = user.email
    response["charge"] = user.get_profile().charge
    response["company"] = user.get_profile().company
    return response
# actualiza los datos de un usuario admin o supervisor
@U.ajax
def updateUser(request):
    response = {}
    response["status"] = "fail";
    if request.method == 'POST':
        user_id = request.POST['id']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        charge = request.POST['charge']
        company = request.POST['company']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        user = User.objects.get(pk=user_id)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        if password1!="":
            user.set_password(password1)
        user.save()
        
        detalles = "datos actualizados: " + user.username                      
        journal.registerActionUserCreated(request, detalles)
        
        if charge!="" and company!="":
            userProfile = user.get_profile();
            userProfile.charge = charge
            userProfile.company = company
            userProfile.save()
        
        
        response["status"] = "ok";
        data = {}
        data["id"] = user_id;
        data["first_name"] = first_name;
        data["last_name"] = last_name;
        data["email"] = email;
        response["data"] = data;
        
    return response
       
# clase wrapper para un usuario y un conjunto de 
# programas al cual esta relacionado el usuario
class UserPrograms:
    def __init__(self,user,programs):
        self.__programs = programs
        self.__user = user
    def user(self):
        return self.__user
    def programs(self):
        return self.__programs
  
    
    


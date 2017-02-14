# -*- coding: utf-8 -*-
from django.contrib.admin.templatetags.admin_list import results
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils import simplejson
from lib import U
from lib.D import ROL
from lib.U import *
from django import forms
from django.db.models.query_utils import Q
from lib.D import PERMISSION as P
from ordenamiento.models import Programa, Sector, User_Programa_Sector, \
    Mapset, MapsetAdmin
from preparacion_proceso.forms import SectorAltasForm, UsuariosSectorForm, PrepararSigForm, ExportarCapaForm, ImportarCapaForm
from rol.forms import NewUserForm
from lib import journal
from django.core.servers.basehttp import FileWrapper
import lib.GrassShell as gsh
import programa.querys as q
import ordenamiento.querys as q_ord
import os


@login_required
def preparacion(request):
    html = "app/preparacion_proceso/preparacion_proceso.html"
    rol = getUsrRol(request)
    grupo = getUsr(request).username
    id_usr = getUsrId(request)
    arg = {}
    return render_to_response(html, arg, context_instance=RequestContext(request)) 

@login_required
def sectores(request):
    html = "app/preparacion_proceso/sectores.html"
    arg = {}
    programId = request.session.get('admin_selectd_program_id',None);
    arg['sectorForm'] = SectorAltasForm(programId=programId)
    if request.method == 'POST':
        sectorForm = SectorAltasForm(request.POST,programId=programId)
        if sectorForm.is_valid():
            id_usr = getUsrId(request)
            programId = request.session.get('admin_selectd_program_id',None);
            programa = Programa.objects.get(pk=programId)
            sectorForm.save(id_usr=id_usr,programa=programa)            
            
            nombre = sectorForm.cleaned_data['nombre']
            detalles = 'sector creado: ' + nombre
            journal.registerActionSectorCreated(request, detalles)
            
            arg['savedSector'] = 'Sector guardado'
        else:
            arg['sectorForm'] = sectorForm
    
    
    programa = Programa.objects.get(pk=programId)
    sectores = Sector.objects.filter(programa=programa);
    arg['sectores'] = sectores
    
    return render_to_response(html, arg, context_instance=RequestContext(request))
# Muestra la relación entre operadores y sectores
@login_required
def get_operador_sector(request):
    html = "app/preparacion_proceso/operador_sector.html"
    arg = {}
    
    grupo = getUsr(request).username    
    users = User.objects.filter(Q(user_permissions__codename=P.OPERADOR) & Q(groups__name=grupo))    
    users.order_by('username')
    
    programId = request.session.get('admin_selectd_program_id',None);
    programa = Programa.objects.get(pk=programId)
    sectores = Sector.objects.filter(programa=programa);
    
    arg['usuariosSectorForm'] = UsuariosSectorForm(operadores=users,sectores=sectores)
    usuarioSectorRelacion = User_Programa_Sector.objects.filter(programa=programa).order_by('user')
    arg['usuarioSectorRelacion'] = usuarioSectorRelacion
    return render_to_response(html, arg, context_instance=RequestContext(request))

@login_required
@U.ajax
def asociar_operador_sector(request):
    response = {}
    response["status"] = "fail";
    if request.method == 'POST':
        operadorId = request.POST['operadorId']
        sectorId = request.POST['sectorId']
        programId = int(request.session.get('admin_selectd_program_id',None));
        user = operador = User.objects.get(pk=operadorId)
        programa = Programa.objects.get(pk=programId)
        sector = Sector.objects.get(pk=sectorId)
        
        #Checamos si ya existe la relación                
        if len(User_Programa_Sector.objects.filter(user=user, programa=programa, sector=sector)) != 0:
            response['status'] = 'fail'
            response['description'] = 'Relación ya existente'
        #Checamos si el sector ya ha sido asignado a otro operadpor
        elif len(User_Programa_Sector.objects.filter(programa=programa, sector=sector)) > 0:
            response['status'] = 'fail'
            response['description'] = 'Este sector ya ha sido asignado a otro operador'        
        else:
            s = User_Programa_Sector(user=user, programa=programa, sector=sector)
            s.save()
            #crea mapset
            #nombre = "sector_" + str(sector.id) + "_" + user.username + "_" + str(user.id)# + "_" + programa.location
            nombre = sector.nombre + "_" + str(sector.id) + "_" + user.username + "_" + str(user.id)# + "_" + programa.location
            m = Mapset(nombre=nombre, user_programa_sector_id=s.id)
            m.save()            
            gsh.create_mapset(m.nombre, programa.location)
                        
                            
            grupo = q_ord.getGrupoAptitudByProgramId(programId)                
            if grupo:
                if grupo.estado:
                    if grupo.estado == U.GROUPS_STARTED:
                        grupo.estado = U.GROUPS_CHANGED
                        grupo.save()
                                
            data = {}
            data['relacionId'] = s.id
            data['sectorName'] = sector.nombre
            data['userName'] = user.first_name + " " + user.last_name            
            response['status'] = 'ok'
            response['data'] = data
            
        
        
    return response;

@login_required
def preparar_sig(request):
    html = "app/preparacion_proceso/preparar_sig.html"
    arg = {}
    programId = int(request.session.get('admin_selectd_program_id',None));        
    programa = Programa.objects.get(pk=programId)
    if request.method == 'POST':
        form = PrepararSigForm(request.POST)
        if form.is_valid():
            programa.descripcion = request.POST['descripcion']        
            programa.save()
            arg['savedDesc'] = 'Descripción guardada'
            #return HttpResponseRedirect("/ecologia/preparar_sig/")        
    else:        
        form = PrepararSigForm(descripcion=programa.descripcion)
    
    arg['prepararSigForm'] = form
    return render_to_response(html, arg, context_instance=RequestContext(request))          

@login_required
@U.ajax
def existe_nombre_capa_importar(request): 
    arg = {}
    arg["error"] = False
    programId = int(request.session.get('admin_selectd_program_id',None));
    location = q_ord.getLocationProgram(programId)
    # Nombre a validar
    capaName = request.GET["capaName"]
    #Obtengo los nombres de las capas del PERMANENT
    gsh.grass_init(location)
    rast = gsh.g_list('rast')        
    rast.sort()
    if capaName in rast:
        arg["error"] = True
        arg["error_description"] = "Nombre existente, por favor eliga otro."
    elif not capaName.isalpha():
        arg["error"] = True
        arg["error_description"] = "Nombre inválido. Proporcione sin espacios y caracteres especiales."
    
    
    return arg

@login_required
def exportar_importar_capa(request):
    html = "app/preparacion_proceso/exp_imp_capa.html"
    arg = {}
    arg["section_imp"] = False
    programId = int(request.session.get('admin_selectd_program_id',None));
    arg["capa_importada_ok"] = ""
    
    if request.method == 'POST':       
        id_usr = getUsrId(request) 
        type = request.POST['type']
        if type == "export":            
            exportarCapaForm = ExportarCapaForm(programa_id=programId)
            # Se dese exportar una capa
            PERMANENT_PREFIX = "*PER*"
            capa_exportar = request.POST['capa_exportar']
            mapset_sector = None
            location = q_ord.getLocationProgram(programId)
            is_permanent = True
            if capa_exportar.startswith(PERMANENT_PREFIX):
                # es una capa de la base del permanent
                capa_exportar = capa_exportar.replace(PERMANENT_PREFIX,"")                
                gsh.grass_init(location)
                
            else:
                # ES una capa de un sector   
                SECTOR_MAPA_SPLIT = "**"
                mapset_capa = capa_exportar.split(SECTOR_MAPA_SPLIT)
                capa_exportar = mapset_capa[1]
                mapset_sector = mapset_capa[0]
                is_permanent = False 
                gsh.grass_init(location,mapset_sector)
                
            
            # Generamos el archivo temporal
            #ascii_file = "jules000_1.txt"
            # obtenemos el archivo exportado para tratar
            res = gsh.exporta_capa(capa_exportar,id_usr,is_permanent,mapset_sector)
            """
            res contiene los elementos:
            file = objeto file de python
            file_size = size de file
            """
            wrapper = FileWrapper(res["file"])
            response = HttpResponse(wrapper,content_type="text/plain")
            response["Content-Length"] = res["file_size"]
            response["Content-Disposition"] = "attachment;filename=" + capa_exportar + ".txt"
            # Eliminamos el archivo temporal
            os.remove(res["file_temp_fullpath"])
            return response
        else:
            # Se desea importar una capa
            arg["section_imp"] = True
            importarCapaForm = ImportarCapaForm(request.POST, request.FILES)
            if importarCapaForm.is_valid():
                location = q_ord.getLocationProgram(programId)
                gsh.grass_init(location)
                nombre_capa_imp = request.POST["nombre_capa"]
                res = gsh.importa_capa(nombre_capa_imp,id_usr,request.FILES["capa"])
                grass_res = res["grass_res"]
                arg["grass_res"] = grass_res
                arg["capa_importada_ok"] = "Capa '" + nombre_capa_imp + "' importada satisfacoriamente."
            exportarCapaForm = ExportarCapaForm(programa_id=programId)
            os.remove(res["file_temp_fullpath"])
    else:
        exportarCapaForm = ExportarCapaForm(programa_id=programId)        
        importarCapaForm = ImportarCapaForm()
    arg["exportarCapaForm"] = exportarCapaForm
    arg["importarCapaForm"] = importarCapaForm
    return render_to_response(html, arg, context_instance=RequestContext(request))


@login_required
@U.ajax
def borrar_sector(request):
    response = {}            
    sectorId = request.POST['sector_id']    
    ups = User_Programa_Sector.objects.filter(sector__id=sectorId)                       
    if len(ups) != 0:
        response['status'] = 'fail'
        response['description'] = 'Este sector ya está relacionado, no se puede borrar'
    else:
        sector = Sector.objects.get(id=sectorId)
        sector.delete()
        response['status'] = 'ok'
        response['description'] = 'Sector eliminado exitosamente'        
    return response;

    
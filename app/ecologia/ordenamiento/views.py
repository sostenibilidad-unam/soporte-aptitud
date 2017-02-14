# -*- coding: utf-8 -*-
#from debian.debtags import reverse
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from lib import U, journal
from lib.D import FUNCION, ROL, PERMISSION as P
from lib.U import getUsr
from ordenamiento.forms import SectorForm, ActividadForm, \
    ActividadAtributoForm, BdCartografica, MapaSector, ComandosForm, MapaValor, \
    MapaAptitud, MapaAptitudAdmin, MapaGrupoAdmin
from ordenamiento.models import Actividad, Atributo, Mapset, Mapa_Valor, \
    Sector, Programa, Mapa_Aptitud, Mapa_Aptitud_Mapa_Valor, Bitacora, \
    User_Programa_Sector
from preparacion_proceso.forms import DiscreteFunctionForm
from settings import DJANGO_MEDIA
from types import FloatType
import lib.D as D
import lib.GrassShell as gsh
import lib.U as U
import ordenamiento.querys as q
import json
import operator
from ordenamiento.querys import MissingAptitudeMapsException, NotApprovedMapsException


@login_required
def ordenamiento(request):
    
    html = "app/ordenamiento/ordenamiento.html"
    home = "/ecologia/menu/"        
    rol = U.getUsrRol(request)
    id_usr = U.getUsrId(request)
    arg = {}  
           
    home = "/ecologia/logout/"
    programa_id = request.session.get('admin_selectd_program_id')
    sector = None
    ups = None
    if rol == ROL.OPERADOR:
        sector = SectorForm(id=id_usr,programa_id=programa_id)
        ups = q.get_idUserProgramaSector_nombreSector(id_usr,programa_id)
        ups_objects = q.get_UserProgramaSector(id_usr,programa_id)
        fdiscretaForm = DiscreteFunctionForm(programa_id=programa_id,ups=ups_objects,label_capa_exportar="Capa")
        arg["fdiscretaForm"] = fdiscretaForm
    elif rol == ROL.SUPERVISOR or rol == ROL.ROOT2:
        """
        Un supervisor debe ver todos los mapas del programa, es deir, ver todos los sectores
        y sus mapas, sin importar el operador 
        """        
        sector = SectorForm(id=None,programa_id=programa_id)
        ups = q.get_idUserProgramaSector_nombreSector(None,programa_id)
    elif rol == ROL.ADMIN:
        if request.GET.has_key('admin_operid'):
            id_usr = request.GET['admin_operid']
            request.session['admin_operador_id_revision'] = id_usr
        else:
            id_usr = request.session.get('admin_operador_id_revision')
        sector = SectorForm(id=id_usr,programa_id=programa_id)
        ups = q.get_idUserProgramaSector_nombreSector(id_usr,programa_id)
    # no tiene programas
    if len(ups) == 0:            
        return HttpResponseRedirect('/ecologia/no_programa/')
    
    str_sector = ups[0][1]
    id_ups = ups[0][0]
    
    actividad_atributo = ActividadAtributoForm(id=id_ups)
    peso = actividad_atributo.getPeso()
    atributo = actividad_atributo.getAtributo()
            
    actividad = ActividadForm()
    mapset = q.getMapset(id_ups)        
    location = q.getLocation(ups[0][0])
    
    #BD cartografica        
    bd_cartografica = BdCartografica(location=location)        
    
    #Lista de mapas
                
    mapa_valor = MapaValor(id_ups=id_ups)
    mapa_aptitud = MapaAptitud(id_ups=id_ups)
    mapas_valor_aptitud = []
    for ma in mapa_aptitud.fields['mapa_aptitud'].widget.choices:
        mapas_valor_aptitud.append(ma[1])
    for mv in mapa_valor.fields['mapa_valor'].widget.choices:
        mapas_valor_aptitud.append(mv[1])        
    mapa_sector = MapaSector(mapset=mapset, location=location,names_avoid=mapas_valor_aptitud)     
    
    #comandos
    cmd = ComandosForm(mapset=mapset, location=location, sector=str_sector)
                
    #arg = {"":home, "":sector, "":, "":, "":, "":, "":, "":, "":, "":}
    arg["home"] = home
    arg["fsector"] = sector
    arg["factividad"] = actividad_atributo
    arg["actividad"] = actividad
    arg["fcmd"] = cmd
    arg["peso"] = peso
    arg["fbd_cartografica"] = bd_cartografica
    arg["mapa_sector"] = mapa_sector
    arg["mapa_valor"] = mapa_valor
    arg["mapa_aptitud"] = mapa_aptitud
    arg["rol"] = rol;
    arg["ROL"] = ROL;
    return render_to_response(html, arg, context_instance=RequestContext(request))



@login_required
def grupos(request):        
    html = "app/ordenamiento/grupos.html"
    home = "/ecologia/menu/"
    rol = U.getUsrRol(request)
    id_usr = U.getUsrId(request)
    if rol == ROL.ADMIN:        
        home = "/ecologia/logout/"        
        sector = SectorForm(id=id_usr)
        arg = {"home":home, "fsector":sector}        
    return render_to_response(html, arg, context_instance=RequestContext(request))


@U.ajax
def change_cut(request):            
    program_id = request.session.get('admin_selectd_program_id')
    localidad = q.getLocationProgram(program_id)
    mapset = q.getMapsetAdmin(program_id).name    
    node_id = request.POST['node_id']
    cut_value = int(request.POST['cut_value'])+1
    id_usr = U.getUsrId(request)
    try:
        gsh.modifica_corte(node_id, cut_value, id_usr, localidad, mapset)
    except:
        gsh.grass_close()
    finally:
        gsh.grass_close()
        grupo = q.getGrupoAptitudByProgramId(program_id)
        grupo.residuales = None
        grupo.promedios = None
        grupo.nodos = None
        #grupo.mapas = None 
        grupo.imagen = None           
        grupo.save()        
    msg = {}
    msg['message'] = 'ok'
    return msg


@U.ajax
def get_nodes(request):            
    programa_id = request.session.get('admin_selectd_program_id')    
    nodes = q.getAllAptitudeNodes(programa_id)
    msg = []    
    for node in nodes:
        node_id = node.id
        parent_node_id = None
        mapindex = q.getNodeCut(node).nombre_corte
        if node.nodo_padre:
            parent_node_id = node.nodo_padre.id
        msg.append({'id':node_id,'parent':parent_node_id,'mapkey':node_id, 'mapindex': mapindex})                
    return msg    


@U.ajax
def check_changes(request):    
    programa_id = request.session.get('admin_selectd_program_id')    
    grupo = q.getGrupoAptitudByProgramId(programa_id)    
    msg = {}
    msg["estado"] = "new"    
    if grupo:
        if grupo.estado:
            if grupo.estado == U.GROUPS_CHANGED:
                msg["estado"] = "changed"
            else:
                msg["estado"] = "started"
    return msg


@U.ajax
def show_group_image(request):            
    programa_id = request.session.get('admin_selectd_program_id')    
    msg = {}
    grupo = q.getGrupoAptitudByProgramId(programa_id)
    if grupo.imagen:
        msg['imagen_grupo'] = True
    else:
        msg['imagen_grupo'] = False                    
    return msg    


@U.ajax
def eliminate_nodes(request):    
    program_id = request.session.get('admin_selectd_program_id')
    localidad = q.getLocationProgram(program_id)
    mapset = q.getMapsetAdmin(program_id).name    
    node_id = request.POST['node_id']    
    try:
        gsh.eliminate_sons(node_id, localidad, mapset)
        grupo = q.getGrupoAptitudByProgramId(program_id)
        grupo.residuales = None
        grupo.promedios = None
        grupo.nodos = None
        #grupo.mapas = None 
        grupo.imagen = None           
        grupo.save()
    except:
        gsh.grass_close()
    finally:
        gsh.grass_close()
        
    msg = {}
    msg['message'] = 'ok'
    return msg

@U.ajax
def eliminate_all(request):    
    
    program_id = request.session.get('admin_selectd_program_id')
    localidad = q.getLocationProgram(program_id)
    mapset = q.getMapsetAdmin(program_id).name
    node_id = q.getRootNode(program_id).id
        
    try:
        gsh.eliminate_sons(node_id, localidad, mapset)
        gsh.eliminate_root(node_id, localidad, mapset)
        grupo = q.getGrupoAptitudByProgramId(program_id)
        grupo.residuales = None
        grupo.promedios = None
        grupo.nodos = None
        grupo.mapas = None 
        grupo.imagen = None
        grupo.estado = U.GROUPS_NEW           
        grupo.save()
    except:
        gsh.grass_close()
    finally:
        gsh.grass_close()
        
    msg = {}
    msg['message'] = 'ok'
    return msg


    
    
@U.ajax
def get_residuals(request):
                
    programa_id = request.session.get('admin_selectd_program_id')
    localidad = q.getLocationProgram(programa_id)
    mapset = q.getMapsetAdmin(programa_id).name        
    user = getUsr(request)
    grupo = user.username
    #users = User.objects.filter(Q(user_permissions__codename=P.OPERADOR) & Q(groups__name=grupo))
    users = q.getOperadoresPrograma(programa_id)
    msg = {}
    
    try:
        map_names = q.getMapNames(users,programa_id)
        if not map_names:
            msg['residuals'] = 'missing_maps'
            return msg
    except MissingAptitudeMapsException as ne:
        msg['residuals'] = 'missing_maps'
        return msg
    except NotApprovedMapsException as me:
        msg['residuals'] = 'missing_approved'
        return msg
    
    try:
        residuals, type = gsh.get_residuals(programa_id, map_names, localidad, mapset, user.id)
    except:
        gsh.grass_close()
                
    msg['residuals'] = residuals
    msg['type'] = type    
    maps = [ map.split('@')[0] for map in map_names]
    msg['maps'] = maps            
    return msg    


@U.ajax
def generate_first_node(request):
    
    user = getUsr(request)
    user_name = user.username
    #users = User.objects.filter(Q(user_permissions__codename=P.OPERADOR) & Q(groups__name=user_name))    
    program_id = request.session.get('admin_selectd_program_id')           
    users = q.getOperadoresPrograma(program_id)
    msg = {}
    grupo = q.getGrupoAptitudByProgramId(program_id)
    try:
        map_names = q.getMapNames(users,program_id)
    except MissingAptitudeMapsException as ne:
        msg['corte_ejecutado'] = 'missing_maps'
        return msg
    except NotApprovedMapsException as me:
        msg['corte_ejecutado'] = 'missing_approved'
        return msg
        
    
    localidad = q.getLocationProgram(program_id)
    mapset = q.getMapsetAdmin(program_id).name    
    the_user = journal.getUserFromRequest(request)               
    prfx = "1"
    gsh.import_maps_to_local_mapset(map_names, localidad, mapset)
    
    try:
        node,cut = gsh.crea_nodo_grupo_aptitud(grupo, localidad, mapset, map_names, prfx, U.NUM_CATEGORIAS, None, the_user.id, None, "left", True)
        node.save()
        cut.nodo=node
        cut.save()        
        grupo.residuales = None
        grupo.promedios = None
        grupo.nodos = None
        grupo.imagen = None
        maps_str = ''
        for m in map_names:
            maps_str += m + '#'        
        grupo.mapas = maps_str
        grupo.estado = U.GROUPS_STARTED
        grupo.save()
        print "group saved"
    
    except:
        gsh.remove_mask()
        gsh.grass_close()        
        msg['corte_ejecutado'] = 'insuficientes'    
        return msg
    
    msg['node_id'] = node.id
    return msg

@U.ajax
def generate_aptitude_groups(request):            
    
    node_id = request.POST['node_id']    
    user = getUsr(request)
    user_name = user.username
    #users = User.objects.filter(Q(user_permissions__codename=P.OPERADOR) & Q(groups__name=user_name))        
    program_id = request.session.get('admin_selectd_program_id')
    users = q.getOperadoresPrograma(program_id)
    msg = {}
    
    try:
        map_names = q.getMapNames(users,program_id)
    except MissingAptitudeMapsException as me:
        msg['corte_ejecutado'] = 'missing_maps'
        return msg
    except NotApprovedMapsException as ne:
        msg['corte_ejecutado'] = 'missing_approved'
        return msg
        
    programa_id = request.session.get('admin_selectd_program_id')
    grupo = q.getGrupoAptitudByProgramId(programa_id)
    localidad = q.getLocationProgram(program_id)
    mapset = q.getMapsetAdmin(program_id).name            
    node = q.getAptitudeNode(node_id)    
    node_cut = q.getNodeCut(node_id) 
    prefx = node_cut.nombre_corte
        
    try:
        gsh.realiza_cortes(node_cut.nombre_mascara_a, node_cut.nombre_mascara_b, node_cut, node, prefx, user.id, U.NUM_CATEGORIAS, localidad, mapset, map_names, grupo)        
        grupo.residuales = None
        grupo.promedios = None
        grupo.nodos = None
        #grupo.mapas = None       
        grupo.imagen = None     
        grupo.save()
    
    except:
        gsh.remove_mask()
        gsh.grass_close()                
        msg['corte_ejecutado'] = 'insuficientes'    
        return msg
        
    msg['corte_ejecutado'] = 'ok'    
    return msg


def export_averages(request):    
    programa_id = request.session.get('admin_selectd_program_id')                
    grupo = q.getGrupoAptitudByProgramId(programa_id)
    return get_excel_document(False, grupo)


def export_residuals(request):
    programa_id = request.session.get('admin_selectd_program_id')                
    grupo = q.getGrupoAptitudByProgramId(programa_id)
    return get_excel_document(True, grupo)


def get_excel_document(are_residuals, grupo):
    
    from django.http import HttpResponse
    import csv
    
    response = HttpResponse(content_type='application/excel')
    
    if are_residuals:
        response['Content-Disposition'] = 'attachment; filename=residuales.xls'
    else:
        response['Content-Disposition'] = 'attachment; filename=promedios.xls'
            
    fileHandler = csv.writer(response, delimiter = ' ')
    residuals = gsh.getMatrixFromString(grupo.residuales)
    averages = gsh.getMatrixFromString(grupo.promedios)
    nodos = gsh.getArrayFromString(grupo.nodos)    
    maps = gsh.getArrayFromString(grupo.mapas)
    mapas = [m.split('@')[0] for m in maps]
    
    headers = []
    footer = []
    headers.append(' ')    
    for m in mapas:
        headers.append(m)
        footer.append('')
    fileHandler.writerow(headers)
    
    if are_residuals:
        for i in range(0,len(residuals)):
            new_row = []
            new_row.append(nodos[i])
            for j in range(0, len(residuals[i])):
                new_row.append(residuals[i][j])
            fileHandler.writerow(new_row)
    else:
        for i in range(0,len(averages)):
            new_row = []
            new_row.append(nodos[i])
            for j in range(0, len(averages[i])):
                new_row.append(averages[i][j])
            fileHandler.writerow(new_row)
    
    fileHandler.writerow(footer)        
    return response

"""
    AJAX ORDENAMIENTO
"""


@U.ajax
def grass_mapa_grupos(request):
    
    programa_id = request.session.get('admin_selectd_program_id')
    grupo = q.getGrupoAptitudByProgramId(programa_id)
    
    nodes = q.getLeaveNodes(programa_id)        
    actual_nodes = gsh.getArrayFromString(grupo.nodos)
        
    if gsh.compare_nodes(nodes, actual_nodes):
        message = ''
    else:
        message = 'El mapa de grupos no está actualizado, debe ir a la seccion Residuales de Gower para que se actualice esta imagen'
            
    im_b64 = grupo.imagen
    img_view =  im_b64
    img_zoom = im_b64   
    msg = {}
    msg['img_view'] = img_view
    msg['img_zoom'] = img_zoom
    msg['mensaje'] = message            
    return msg

    
@U.ajax
def grass_mapa_grupo(request):
    node_id = request.POST['node_id']
    node_cut = q.getNodeCut(node_id)    
    im_b64 = node_cut.imagen
    img_view =  im_b64
    img_zoom = im_b64   
    msg = {}
    msg['img_view'] = img_view
    msg['img_zoom'] = img_zoom
    msg['corte_ejecutado'] = node_cut.corte_ejecutado
    node = q.getAptitudeNode(node_id)
    hyst_data = U.getHistogramData(node.histogram_data)      
    msg['hyst_data'] = hyst_data
    msg['map_title'] = q.getNodeCut(node).nombre_corte
    msg['valor_corte'] = node_cut.valor_corte
    msg['es_final'] = node.es_final        
    return msg


@U.ajax
def select_subsector(request):
    """
    select actividad atributo peso mapset
    """
    
    msg = {}        
    typ = int(request.POST['typ'])
    id_ups = int(request.POST['id_ups'])
    program_id = request.session.get('admin_selectd_program_id')
    location = q.getLocationProgram(program_id)
    
    #tabla funcion valor    
    tbl_mapa_valor = []    
    for act in Actividad.objects.select_related('user_sector_programa').filter(user_sector_programa__id=id_ups):
        for atr in Atributo.objects.select_related('actividad').filter(actividad__id=act.id):
            for m in Mapa_Valor.objects.select_related('atributo').filter(atributo__id=atr.id):               
                tbl_mapa_valor.append((m.id, m.nombre[1:], m.atributo.actividad.actividad, m.atributo.atributo, "{0:.2f}".format(m.atributo.peso)))
    

    #actividad
    if typ == 0:
        
        ja = {}             
        actividad = q.getActividad(id_ups)        
        for a in actividad:
            ja[a[0]] = a[1]
        msg['actividad'] = sorted(ja.iteritems(), key=operator.itemgetter(1))
        
        if actividad:        
            jb = {}
            atributo = q.getAtributo(actividad[0][0])        
            for a in atributo:
                jb[a[0]] = a[1]
            msg['atributo'] = sorted(jb.iteritems(), key=operator.itemgetter(1))
            
            jc = {}
            peso = q.getPeso(actividad[0][0])        
            for a in peso:            
                jc[a[0]] = str(a[1])
            msg['peso'] = sorted(jc.iteritems(), key=operator.itemgetter(1))
        else:
            msg['atributo'] = []
            msg['peso'] = []
        
        mapas_valor = q.getMapaValor(id_ups)
        mapas_aptitud = q.getMapaAptitud(id_ups)
        msg['mapa_valor'] = mapas_valor
        names_avoid = []    
        for mv in mapas_valor:
            names_avoid.append(mv[1])
        for ma in mapas_aptitud:
            names_avoid.append(ma[1])
        msg['mapa_sector'] = U.getMapsetSector(location, q.getMapset(id_ups),names_avoid)
        msg['mapa_aptitud'] = mapas_aptitud        
        msg['tbl_mapa_valor'] = tbl_mapa_valor
     
        
    #atributo
    elif typ == 1:
        jb = {}
        atributo = q.getAtributo(id_ups)        
        for a in atributo:
            jb[a[0]] = a[1]
        msg['atributo'] = sorted(jb.iteritems(), key=operator.itemgetter(1))
        
        jc = {}
        peso = q.getPeso(id_ups)        
        for a in peso:            
            jc[a[0]] = str(a[1])
        msg['peso'] = sorted(jc.iteritems(), key=operator.itemgetter(1))
            
    #peso
    elif typ == 2:
        atributo_id = int(request.POST['atributo_id'])
        peso = str(q.getPesoA(atributo_id).peso) 
        msg = {'peso':peso}
    
    msg['success'] = True
    return msg

"""
Function para obtener los atributos y pesos de una actividad
"""
@U.ajax
def get_attrpeso_from_activity(request):
    actividad_id = request.POST["actividad_id"]
    actividad = Actividad.objects.get(pk=actividad_id)
    atributos = Atributo.objects.filter(actividad=actividad)
    msg = {}
    pesos = []
    for atr in atributos:
        pesos.append({"id":atr.id, "atributo": atr.atributo,"peso":str(atr.peso)})
    msg["atributos"] = pesos
    return msg
"""
    AJAX_FORM
"""

@U.ajax
def form_actividad(request):
    
    
    msg = {}
    
    atributo = request.POST.getlist('atributo')
    peso = request.POST.getlist('peso')
    actividad = request.POST['actividad']
    actividad = actividad.strip()
    
    if actividad == "":
        msg['success'] = False
        msg['error'] = "Campo Actividad es obligatorio"
        msg['actividad'] = actividad 
        return msg
    
    if "" in atributo:
        msg['success'] = False
        msg['error'] = "Campo atributo no puede estar en blanco"
        msg['actividad'] = actividad 
        return msg
    
    if "" in peso:
        msg['success'] = False
        msg['error'] = "Campo peso no puede estar en blanco"
        msg['actividad'] = actividad
        return msg
    
    for p in peso:
        p = float(p)
        if p < 0 or p > 1:
            msg['success'] = False
            msg['error'] = "El rango del campo peso es de [0 - 1]"
            return msg
        
    total_peso = 0
    for p in peso:
        total_peso += float(p)
    if total_peso != 1:        
        msg['success'] = False
        msg['error'] = "La sumatoria de los pesos debe ser igual a 1"
        return msg

    sector = SectorForm(request.POST)    
    if sector.is_valid(): 
        usp_id = sector.cleaned_data['sector']
        actividad = ActividadForm(request.POST, usp_id=usp_id)
      
    if actividad.is_valid():
        id_actividad = actividad.save()  
        ##Register activity creation in journal
        detalles = 'creada actividad: '+ request.POST['actividad']
        journal.registerActionActivityCreated(request, detalles)
        
        
        for i in range(len(atributo)):    
            a = Atributo(atributo=atributo[i], peso=Decimal(peso[i]), actividad_id=id_actividad.id)
            a.save()
            ##Register attribute creation in journal
            detalles = 'creado sector: '+ request.POST['atributo']
            journal.registerActionAttributeCreated(request, detalles)
            

        ja = {}             
        actividad = q.getActividad(usp_id)        
        for a in actividad:
            ja[a[0]] = a[1]
        msg['actividad'] = sorted(ja.iteritems(), key=operator.itemgetter(1))
        
        
        jb = {}
        atributo = q.getAtributo(actividad[0][0])        
        for a in atributo:
            jb[a[0]] = a[1]
        msg['atributo'] = sorted(jb.iteritems(), key=operator.itemgetter(1))
        
        jc = {}
        peso = q.getPeso(actividad[0][0])        
        for a in peso:            
            jc[a[0]] = str(a[1])
        msg['peso'] = sorted(jc.iteritems(), key=operator.itemgetter(1))

        msg["success"] = True    
    else:
        msg["success"] = False
        msg["error"] = actividad.errors['actividad']
    
    return msg               

"""
    AJAX GRASS
"""
    
@U.ajax_nan
def grass_permanent(request):
    ups_id = request.POST['ups_id']
    capa = request.POST['capa']
    type_capa = request.POST['type']
    
    location = q.getLocation(ups_id)
    
    gsh.grass_init(location)        
    msg = gsh.info(capa, type_capa)
    
    gsh.grass_init(location)
    img_view, img_zoom = gsh.preview(capa, type_capa, U.getUsrId(request), location)    
    msg['img_view'] = img_view
    msg['img_zoom'] = img_zoom

    return msg

@U.ajax_nan
def grass_mapset(request):
    ups_id = request.POST['ups_id']    
    capa = request.POST['capa']
    
    location = q.getLocation(ups_id)
    
    mapset = q.getMapset(ups_id)
        
    gsh.grass_init(location, mapset)        
    msg = gsh.info(capa, 'r')
    
    gsh.grass_init(location, mapset)
    img_view, img_zoom = gsh.preview(capa, 'r', U.getUsrId(request),location)    
    msg['img_view'] = img_view
    msg['img_zoom'] = img_zoom    
    return msg

#Requesting mapa funcion valor
@U.ajax_nan
def grass_mapset_valor(request):
    ups = request.POST['usp']
    
    location = q.getLocation(ups)
    
    #sectorId = int(request.POST['sector'])
    #sector = Sector.objects.get(pk=sectorId)
    #capa = 'f' + request.POST['capa']
    #capa = sector.prefijo_mapas + '_' + request.POST['capa']
    capa = request.POST['capa']
    id_mapa = request.POST['id_mapa']
        
    mapset = q.getMapset(ups)
    gsh.grass_init(location, mapset)    
    msg = gsh.info(capa, 'r')
    
    gsh.grass_init(location, mapset)  
    img_view, img_zoom = gsh.preview(capa, 'r', U.getUsrId(request), location)    
    msg['img_view'] = img_view
    msg['img_zoom'] = img_zoom
            
    mv = Mapa_Valor.objects.get(id=id_mapa);        
    atr = Atributo.objects.filter(actividad=mv.atributo.actividad.id)
    
    atrs = []
    for a in atr:
        atrs.append((a.id, a.atributo))
    
    msg['typ_fun'] = mv.funcion

    fv = {}
    msg['fv'] = fv            
    
    fv['id_actividad'] = mv.atributo.actividad.id
    fv['atributo'] = atrs
    fv['id_atributo'] = mv.atributo.id
    fv['id_peso'] = "{0:.2f}".format(mv.atributo.peso)
    
    fv['sld_min_max'] = [mv.min_escala, mv.max_escala]    
         
    if mv.funcion == FUNCION.CRECIENTE_CX or mv.funcion == FUNCION.DECRECIENTE_CX or mv.funcion == FUNCION.CRECIENTE_CV or mv.funcion == FUNCION.DECRECIENTE_CV:        
        fv['sld_saturacion'] = mv.saturacion        
    elif mv.funcion == FUNCION.CAMPANA:
        fv['sld_xmax'] = mv.x_max
        fv['sld_amplitud'] = mv.amplitud       
    elif mv.funcion == FUNCION.CAMPANA_INV:
        fv['sld_xmin'] = mv.x_min
        fv['sld_amplitud'] = mv.amplitud         
    elif mv.funcion == FUNCION.DIFUSA: 
        pass
    
    return msg

#Requesting mapa aptitud
@U.ajax_nan
def grass_mapset_aptitud(request):
    
    capa = request.POST['capa'].strip()
    id_aptitud = request.POST['id_aptitud']
    type_capa = 'r'
    
    mapa = q.getMapaAptitudById(id_aptitud)
    ups_id = mapa.user_sector_programa.id    
    
    location = q.getLocation(ups_id)
    mapset = q.getMapset(ups_id)    
    
    gsh.grass_init(location, mapset)        
    msg = gsh.info(capa, type_capa)
    
    gsh.grass_init(location, mapset)
    img_view, img_zoom = gsh.preview(capa, type_capa, U.getUsrId(request), location)   
    msg['img_view'] = img_view
    msg['img_zoom'] = img_zoom

    
    m = Mapa_Aptitud.objects.get(id=id_aptitud)
    
    if m.estatus == "aprobado":
        msg["aprobado"] = True
    else:
        msg["aprobado"] = False
    
    return msg

@U.ajax
def grass_fun_continua(request):
        
    msg = {}
    
    m = request.POST['mapa']
    
    ups_id = int(request.POST['sector'])#Watch Out En realidad es el is de user_programa_sector    
    ups = User_Programa_Sector.objects.get(id=ups_id)    
    sector = ups.sector
        
    #mapa = 'f' + m
    mapa = sector.prefijo_mapas + '_' + m
    id_ups = request.POST['id']
    
    type_fun = int(request.POST['type_fun'])
    capa = request.POST['capa']
    fmin = request.POST['min']
    fmax = request.POST['max']    
    atributo = request.POST['atributo']
    
    min_func = float(request.POST['min_func'])
    max_func = float(request.POST['max_func'])

    mapset = q.getMapset(id_ups)    
    m = Mapa_Valor(nombre=mapa, version=1, funcion=type_fun, min_escala=fmin, max_escala=fmax, atributo_id=atributo)    

    location = q.getLocation(id_ups)
    """
    msg['mapset'] = mapset
    msg['location'] = location
    return msg
    """
    gsh.grass_init(location, mapset)
    
    if type_fun == FUNCION.CRECIENTE_CX:
        p_control = request.POST['parm_control']
        saturacion = request.POST['saturacion']
        m.saturacion = saturacion        
        gsh.fv_creciente_cx(mapa, capa, p_control, min_func, max_func)
        
    elif type_fun == FUNCION.DECRECIENTE_CX: 
        p_control = request.POST['parm_control']
        saturacion = request.POST['saturacion']
        m.saturacion = saturacion
        gsh.fv_decreciente_cx(mapa, capa, p_control, min_func, max_func)
        
    elif type_fun == FUNCION.DECRECIENTE_CV: 
        p_control = request.POST['parm_control']
        saturacion = request.POST['saturacion']
        m.saturacion = saturacion
        gsh.fv_decreciente_cv(mapa, capa, p_control, min_func, max_func)
        
    elif type_fun == FUNCION.CRECIENTE_CV: 
        p_control = request.POST['parm_control']
        saturacion = request.POST['saturacion']
        m.saturacion = saturacion
        gsh.fv_creciente_cv(mapa, capa, p_control, min_func, max_func)
        
    elif type_fun == FUNCION.CAMPANA:
        min_max = request.POST['x']        
        amplitud = request.POST['ampl']
        m.x_max = min_max
        m.amplitud = amplitud
        gsh.fv_campana(mapa, capa, min_max, amplitud, min_func, max_func)
        
    elif type_fun == FUNCION.CAMPANA_INV:
        min_max = request.POST['x'] 
        amplitud = request.POST['ampl']
        m.x_min = min_max
        m.amplitud = amplitud
        gsh.fv_campana_inv(mapa, capa, min_max, amplitud, min_func, max_func)

    elif type_fun == FUNCION.DIFUSA:
        va = request.POST['a']
        vb = request.POST['b']
        vc = request.POST['c']
        vd = request.POST['d']        
        gsh.fv_difusa(mapa, capa, va, vb, vc, vd, min_func, max_func)
        

    m.save()
    
    ##Register creation of funcion valop map in journal 
    detalles = 'mapa funcion valor creado: '+ mapa
    journal.registerActionValueFunctionMapCreated(request, detalles)
        
    location = q.getLocation(id_ups)    
    mapset = q.getMapset(id_ups)
    
    gsh.grass_init(location, mapset)    
    msg = gsh.info(mapa, 'r')
    
    
    gsh.grass_init(location, mapset)  
    img_view, img_zoom = gsh.preview(mapa, 'r', U.getUsrId(request), location)    
    msg['img_view'] = img_view
    msg['img_zoom'] = img_zoom
    
    msg['id'] = m.id
    msg['status'] = True
    msg['mapa_name'] = mapa
    
    return msg 


"""
Genera un archivo para reclasificar, reclasifica y así genera el mapa función discreta
"""
@login_required
@U.ajax
def grass_fun_discreta(request):
    arg = {}
    msg = {}
    if request.method == 'POST':
        newvalues = request.POST["newvalues"]
        nombreCapa = request.POST["nombreCapa"]
        ups_id = int(request.POST["ups_id"])
        #id_sector = request.POST["id_sector"]
        id_actividad = request.POST["id_actividad"]
        id_atributo = request.POST["id_atributo"]
        programa_id = request.session.get('admin_selectd_program_id')
        capa_entrada = request.POST["capa_entrada"]
        
        oldNews = newvalues.split("_")
        fileContent = ""
        for oldNew in oldNews:
            #oldNew = oldNew.replace("*", " = ")
            old_new_vals = oldNew.split("*")
            val = float(old_new_vals[1])* 100
            new_val = int(val)  
            fileContent = fileContent + old_new_vals[0] + " = " + str(new_val) + "\n"  
    
        
    ######################################
    # inicialización de grass
    PERMANENT_PREFIX = "*PER*"
    location = q.getLocation(ups_id)
    mapset_sector = None
    isPermanent = False
    id_usr = U.getUsrId(request)
    #sector = Sector.objects.get(pk=int(id_sector))
    #programa = Programa.objects.get(pk=int(programa_id))
    #usuario = User.objects.get(pk=int(id_usr))
    #ups = User_Programa_Sector.objects.get(user=usuario,programa=programa,sector=sector)
    ups = User_Programa_Sector.objects.get(pk=ups_id)
    sector = ups.sector
    
    mapset_sector = q.getMapset(ups.id) 
    if capa_entrada.startswith(PERMANENT_PREFIX):
        isPermanent = True
        capa_entrada = capa_entrada.replace(PERMANENT_PREFIX,"")
        gsh.grass_init(location)
    else:
        SECTOR_MAPA_SPLIT = "**"                
        mapset_capa = capa_entrada.split(SECTOR_MAPA_SPLIT)
        capa_entrada = mapset_capa[1]
        #mapset_sector = mapset_capa[0]    
    
    nombreCapa = sector.prefijo_mapas + "_" + nombreCapa
    gsh.grass_init(location, mapset_sector)    
    ######################################    
    
    
     
    
    gsh.funcion_discreta_reclass(fileContent,capa_entrada,nombreCapa,id_usr,False,mapset_sector)
    ######### Ya esté generado, ahora lo guardamos
      
    m = Mapa_Valor(nombre=nombreCapa, version=1, funcion=-1, min_escala=-1, max_escala=-1, atributo_id=int(id_atributo))
    m.save()
    ######### Ya que está generado, ahora lo pre-visualizamos##########################333333
    gsh.grass_init(location, mapset_sector)      
    msg = gsh.info(nombreCapa, 'r')
    
    
    gsh.grass_init(location, mapset_sector)    
    img_view, img_zoom = gsh.preview(nombreCapa, 'r', U.getUsrId(request),location)    
    msg['img_view'] = img_view
    msg['img_zoom'] = img_zoom
    
    msg['id'] = m.id
    msg['status'] = True
    msg['mapa_name'] = nombreCapa
    ##############################################33
    
    
    msg["fileContent"] = fileContent
    return msg

@login_required
@U.ajax
def getfdiscretas(request):
    arg = {}
    capa_nombre = request.GET['capa_nombre']
    programa_id = request.session.get('admin_selectd_program_id')
    PERMANENT_PREFIX = "*PER*"
    location = q.getLocationProgram(programa_id)
    mapset_sector = None
    
    if capa_nombre.startswith(PERMANENT_PREFIX):
        capa_nombre = capa_nombre.replace(PERMANENT_PREFIX,"")
        gsh.grass_init(location)
    else:
        SECTOR_MAPA_SPLIT = "**"
        mapset_capa = capa_nombre.split(SECTOR_MAPA_SPLIT)
        capa_nombre = mapset_capa[1]
        mapset_sector = mapset_capa[0]    
    
    if mapset_sector == None:    
        gsh.grass_init(location)
    else:
        gsh.grass_init(location, mapset_sector)
    
    info_vals = gsh.info(capa_nombre,"r")
    
    if info_vals["datatype"] == "CELL":
        arg["isInteger"] = True       
        
        if mapset_sector == None:    
            gsh.grass_init(location)
        else:
            gsh.grass_init(location, mapset_sector)
        val_discretas = gsh.getValoresDiscretos(capa_nombre)    
        
        if len(val_discretas)>200:
            arg["too_much_info"] = True;    
                
        arg["val_discretas"] = val_discretas        
        
    else:
        arg["isInteger"] = False
    
    arg["info_vals"] = info_vals
    return arg
   
@U.ajax
def grass_mapa_aptitud(request):
    msg = {}

    
    ups_id = request.POST['ups_id']
    
    #sectorId = int(request.POST['sector'])
      
    ups = User_Programa_Sector.objects.get(id=ups_id)    
    sector = ups.sector
    
    #nombre_aptitud = request.POST['nombre_aptitud']
    #nombre_aptitud = "f" + request.POST['nombre_aptitud']    
    nombre_aptitud = sector.prefijo_mapas + '_' + request.POST['nombre_aptitud']
    id_mapa_valor = json.loads(request.POST['id_mapa_valor'])
    
    location = q.getLocation(ups_id)
    mapset = q.getMapset(ups_id)
    
    exp = ""
    for id in id_mapa_valor:
        m = Mapa_Valor.objects.get(id=id)
        exp += "(" + m.nombre + "*" + str(m.atributo.peso) + ")+"
    exp = exp[:len(exp) - 1]
    
    #grass
    gsh.grass_init(location, mapset)
    b_aptitud = gsh.mapa_aptitud(nombre_aptitud, exp)
    
    #save bd
    if b_aptitud:
        
        #mapa nombre_aptitud
        mp = Mapa_Aptitud()
        mp.nombre = nombre_aptitud
        mp.estatus = D.STATUS_APTITUD.NO_APROBADO
        mp.user_sector_programa_id = ups_id        
        mp.save()
        
        ##Register creation of funcion valop map in journal 
        detalles = 'mapa aptitud creado: '+ request.POST['nombre_aptitud']
        journal.registerActionAptitudeMapCreated(request, detalles)
        
        for id in id_mapa_valor:            
            m = Mapa_Aptitud_Mapa_Valor(mapa_aptitud_id=mp.id, mapa_valor_id=id)
            m.save()
        
        gsh.grass_init(location, mapset)    
        msg = gsh.info(nombre_aptitud, 'r')
    
        gsh.grass_init(location, mapset)        
        img_view, img_zoom = gsh.preview(nombre_aptitud, 'r', U.getUsrId(request), location)    
        
        msg['img_view'] = img_view
        msg['img_zoom'] = img_zoom
    
        msg['id'] = mp.id
        msg['status'] = True        
    else:
        msg['status'] = False
    
    msg['mapa_name'] = nombre_aptitud
    return msg
 
@U.ajax    
def grass_cmd(request):    
    msg = {}
    type_capa = request.POST['type_capa']
    
    cmd = int(request.POST['cmd'])    
    capa = request.POST['capa_in']
    ups_id = request.POST['id_sector']
    
    location = q.getLocation(ups_id)
    mapset = q.getMapset(ups_id)                
    gsh.grass_init(location, mapset)
            
    if cmd == D.CMD.DESAGRUPAR:
        capa_out = request.POST['capa_out']
        gsh.desagrupar(capa, capa_out)
        
    elif cmd == D.CMD.DISTANCIA:
        capa_out = request.POST['capa_out']
        try:
            gsh.distance(capa, capa_out)
        except:
            gsh.grass_close()
            msg['distance_fail'] = True
            msg['status'] = True
            return msg   
        
    elif cmd == D.CMD.PENDIENTE:
        capa_out = request.POST['capa_out']
        format_ = request.POST['format']
        gsh.pendiente(capa, capa_out, format_)
        
    elif cmd == D.CMD.MASCARA:
        maskcats = request.POST['maskcats']
        gsh.mascara(capa, maskcats)
        
    elif cmd == D.CMD.NULOS:
        setnull = request.POST['setnull']
        capa_out = request.POST['capa_out']
        gsh.nulos(capa, setnull, capa_out, mapset)
        
    elif cmd == D.CMD.ESTADISTICA:        
        msg["estadistica"] = gsh.estadistica(capa)
        
    if cmd != D.CMD.ESTADISTICA:   
        gsh.grass_init(location, mapset)        
        msg = gsh.info(capa_out, 'r')
        
    #preview
    gsh.grass_init(location, mapset)
    #msg = gsh.info(capa, 'r')
    if  cmd == D.CMD.DESAGRUPAR or cmd == D.CMD.DISTANCIA or cmd == D.CMD.PENDIENTE:
        img_view, img_zoom = gsh.preview(capa_out, 'r', U.getUsrId(request), location)            
        msg['img_view'] = img_view
        msg['img_zoom'] = img_zoom
        
    elif cmd == D.CMD.NULOS:        
        img_view, img_zoom = gsh.preview(capa_out, 'r', U.getUsrId(request), location)    
        msg['img_view'] = img_view
        msg['img_zoom'] = img_zoom
    elif cmd == D.CMD.MASCARA:
        msg['img_view'] = ''
        msg['img_zoom'] = ''
           
           
    
    msg['distance_fail'] = False
    msg['status'] = True
    
    
    return msg

@U.ajax
def grass_del_capa(request):
    
    """
    0=cartografica sector 
    *1=cartografica general 
    2=funcion valor 
    3=aptitud
    """ 
    msg = {}
    
    # id sector
    id_ups = request.GET['sectorId']
    #accordion = request.POST['accordion']
    # nombre del mapa
    capa = request.GET['nameCapa']
    
    
    location = q.getLocation(id_ups)
    mapset = q.getMapset(id_ups)        
    
    #Ahora eliminar de la base de datos
    # Checamos si es un mapa de valor
    if 'mapavalorId' in request.GET:
        mapavalorId = request.GET['mapavalorId']
        if(mapavalorId.isnumeric()):
            #eliminar un mapa valor
            """
            Pero primero debemos checar si este mapa ayudó a formar
            un mapa de aptitud, de ser así no se puede eliminar
            """
            mapaValor = Mapa_Valor.objects.get(pk=int(mapavalorId))
            relacion_MapaAptitudValores = Mapa_Aptitud_Mapa_Valor.objects.filter(mapa_valor=mapaValor)
            if(len(relacion_MapaAptitudValores)>0):
                #No puedo borrar este mapa porque existe un mapa de aptitud
                # creado con mapaValor, pirmero se debe eliminar el mapa de aptitud
                nombeAptitud = "'" + relacion_MapaAptitudValores[0].mapa_aptitud.nombre + "'"
                msg["status"] = "fail"
                msg["errorDescription"] = "Este mapa no se puede eliminar porque fue utilizado para crear un mapa de aptitud. Primero elimine el mapa de aptitud " + nombeAptitud
                return msg
            else:  
                mapaValor.delete()
                gsh.grass_init(location, mapset)    
                gsh.remove(capa)                
                msg["status"] = "ok"
    # checamos si es un mapa de aptitud
    elif 'mapaaptitudId' in request.GET:
        mapaaptitudId = request.GET['mapaaptitudId']
        if(mapaaptitudId.isnumeric()):
            """
            eliminar un mapa de aptitud
            Pero debemos también borrar las relaciones con mapas de valor
            que ayudaron a formar este mapa
            @@TODO: se debería checar que este mapa ayudó a construir un Grupo de aptitud
            """
            mapaAptitud = Mapa_Aptitud.objects.get(pk=int(mapaaptitudId))
            relacion_MapaAptitudValores = Mapa_Aptitud_Mapa_Valor.objects.filter(mapa_aptitud=mapaAptitud)
            for rel in relacion_MapaAptitudValores:
                rel.delete()
            mapaAptitud.delete()
            gsh.grass_init(location, mapset)    
            gsh.remove(capa)
            msg["status"] = "ok"
            
            programa_id = request.session.get('admin_selectd_program_id')
            grupo = q.getGrupoAptitudByProgramId(programa_id)    
            if grupo:
                if grupo.estado:
                    if grupo.estado == U.GROUPS_STARTED:
                        grupo.estado = U.GROUPS_CHANGED
                        grupo.save()
                        
                    
    #es una capa del sector        
    else:
        gsh.grass_init(location, mapset)    
        gsh.remove(capa) 
        msg["status"] = "ok"
    return msg


@U.ajax
def grass_aptitud_aprobar(request):
    
    msg = {}
    id_aptitud = request.POST['id_aptitud']
    id_usr = U.getUsrId(request)
    programa_id = request.session.get('admin_selectd_program_id')    
    ups = q.get_idUserProgramaSector_nombreSector(id_usr,programa_id)
    id_ups = ups[0][0]
        
    m = Mapa_Aptitud.objects.get(id=id_aptitud)
        
    grupo = q.getGrupoAptitudByProgramId(programa_id)    
    if grupo:
        if grupo.estado:
            if grupo.estado == U.GROUPS_STARTED:
                grupo.estado = U.GROUPS_CHANGED
                grupo.save()
    
    if m.estatus == "aprobado":
        m.estatus = "no aprobado"
    else:
        m.estatus = "aprobado"
    m.save();
    
    ##TODO: Register map aprobation in journal
    
    msg["status"] = True
    return msg


@U.ajax
def grass_syntax(request):
    lst = []
    msg = {}
    
    
    
    # cmd 0 
    # funcionValor 1
    #funcionAptitud 2
    
    ups_id = request.POST['id_sector'] #Whatch Out:  En realidad es el id del user_programa_sector
    typ_bd = int(request.POST['typ_db'])
    
    ups = User_Programa_Sector.objects.get(id=ups_id)    
    sector = ups.sector
    
    sectorPrefijo = sector.prefijo_mapas 
    capa = sectorPrefijo + "_" + request.POST['capa']
    capaOriginal = request.POST['capa']
    

    location = q.getLocation(ups_id)
    mapset = q.getMapset(ups_id)                
    gsh.grass_init(location, mapset)
        
    msg['status'] = False
    
    #verificar nombre valido
    if not gsh.isVarGrass(capa):    
        msg['error'] = "Los espacios,caracteres especiales no son permitidos. Proporcione otro nombre, utilice guión bajo \"_\" para espacios"
        return msg

    #verificar si existe la capa 
    if capa in gsh.list_raster_sector() and typ_bd == 0:
        msg['error'] = "La capa " + capaOriginal + " ya esta ocupado. Proporcione otra"
        return msg
    
    #funcion valor
    if typ_bd == 1:
        mapa = capa
        #verificar si existe la funcion
        for act in Actividad.objects.select_related('user_sector_programa').filter(user_sector_programa__id=ups_id):
            for atr in Atributo.objects.select_related('actividad').filter(actividad__id=act.id):
                for m in Mapa_Valor.objects.select_related('atributo').filter(atributo__id=atr.id):                
                    lst.append(m.nombre)                 
        if mapa in lst:
            msg['status'] = False
            msg['error'] = "El mapa " + capaOriginal + " ya esta ocupada. Proporcione otro"
            return msg
        
    #funcion aptitud
    if typ_bd == 2:
        mapa = capa#'f' + capa
        #verificar si existe funcion aptitud
        for m in Mapa_Aptitud.objects.filter(user_sector_programa=ups_id): 
            lst.append(m.nombre)
                 
        if mapa in lst:
            msg['status'] = False
            msg['error'] = "El mapa " + capaOriginal + " ya esta ocupada. Proporcione otro"
            return msg
        """
        verificar sumatoria de mapa valor 
        1) actividad igual
        2) atributo desiguales
        3) sumatoria 1
        """
        id_mapa_valor = json.loads(request.POST['id_mapa_valor'])
        lst = []
        lst_p = []
        for id in id_mapa_valor:
            m = Mapa_Valor.objects.get(id=id)
            lst.append(m.atributo_id)
            lst_p.append(m.atributo.peso)
        i = 0
        b = False
        while (i < len(lst)):
            if lst.pop() in lst:
                b = True
                break
            i += 1
        if b:
            msg['status'] = False
            msg['error'] = "No puedes sumar atributos iguales"
            return msg
        suma = 0
        for p in lst_p:
            suma += p
        if suma != 1:
            msg['status'] = False
            msg['error'] = "La sumatoria de los pesos debe ser igual a 1"
            return msg
        
    msg['status'] = True
    return msg

"""
    NO PROGRAMA
"""    
    
@login_required
def no_programa(request):
    arg = {}
    html = 'app/ordenamiento/no_programa.html'
    rol = U.getUsrRol(request)
    arg["rol"] = rol;
    arg["ROL"] = ROL;    
    if rol == ROL.SUPERVISOR or rol == ROL.ROOT2:
        arg['root2_supervisor'] = 1
        arg['root2'] = 0
        if rol == ROL.ROOT2:
            arg['root2'] = 1
    else:
        arg['root2_supervisor'] = 0
        arg['arg'] = 2
    return render_to_response(html, arg, context_instance=RequestContext(request))

"""
Función para mostrar a los operadores relacionados a este programa
"""
@login_required
def seguimiento_operadores(request):
    arg = {}
    html = 'app/ordenamiento/seguimiento_operadores_lista.html'    
    rol = U.getUsrRol(request)
    if rol == ROL.ADMIN:
        if request.method == 'GET':        
            programa_id = request.session.get('admin_selectd_program_id')
            ups = User_Programa_Sector.objects.filter(programa=programa_id)
            if len(ups)>0:
                usrs = {}
                for us in ups:
                    user = us.user;
                    sector = us.sector;
                    active = us.activo
                    if not usrs.has_key(user.id):
                        usrs[user.id] = [user,[sector], active]
                    else:
                        list = usrs[user.id]
                        sector_list = list[1]
                        sector_list.append(sector)
                arg['usrs'] = usrs
                    
            else:
                x=0##@@TODO
        else:
            x=0##@@TODO
    else:
        x=0##@@TODO
        
    return render_to_response(html, arg, context_instance=RequestContext(request))


@login_required
@U.ajax
def generafdiscreta(request):
    arg = {}    
    return arg


@login_required
@U.ajax
def activacion_operador(request):
    arg = {}
    arg["status"] = "fail"
    if request.method == 'POST':
        operation = request.POST['operation']
        operId = request.POST['operId']
        programa_id = request.session.get('admin_selectd_program_id')
        ups_list = User_Programa_Sector.objects.filter(programa=programa_id,user=operId)
        for ups in ups_list:
            ups.activo = 1 - ups.activo
            ups.save()
        
        user = q.getUser(operId)
        detalles = 'operador ' + user.username
        if ups.activo == 0:            
            journal.registerActionUserDisabled(request, detalles)
        else:            
            journal.registerActionUserEnabled(request, detalles)
        
        arg["status"] = "ok"
        arg["activo"] = ups.activo
        
    return arg


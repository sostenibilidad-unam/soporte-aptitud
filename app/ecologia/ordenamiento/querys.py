#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from ordenamiento.models import User_Programa_Sector, Actividad, \
    Atributo, Mapa_Valor, Programa, Mapset, Mapa_Aptitud, Accion, Bitacora, MapsetAdmin, NodoMapaGrupo, Corte,MapaGruposAptitud
    
from django.contrib.auth.models import User
    
"""
Regresa una lista de de tuplas de la forma: (ups_id,sector)
La info de l tupla se obtiene de los objetos  User_Programa_Sector
que hagan match con el id de usurio y el id del programa pasados por param.
Si el id de usuario es None, entonces solamente se busca por id de programa

@param id: id del usuario sobre el cual se buscan sus relaciones
@param programa_id: id del programa en dónde se busca  
"""
APTITUDE_MAP_SUFFIX = "_norm_apt"

def get_idUserProgramaSector_nombreSector(id,programa_id):
    #sector = Sector.objects.select_related("sector").filter(sector__user=id)
    lst=[]
    _ups = None
    if(id==None):
        _ups = User_Programa_Sector.objects.filter(programa=programa_id)
    else:
        _ups = User_Programa_Sector.objects.filter(user=id,programa=programa_id)    
    for ups in _ups:
        lst.append((ups.id,ups.sector))      
    return  lst


def get_UserProgramaSector(usr_id,programa_id):
    ups = User_Programa_Sector.objects.filter(user__id=usr_id,programa=programa_id)          
    return  ups
"""
Obtiene la lista de operadores asignados a un programa
"""
def getOperadoresPrograma(programa_id):
    _ups = User_Programa_Sector.objects.filter(programa=programa_id)
    users = []
    usersKeys = []
    if len(_ups)>0:
        for ups in _ups:            
            user = ups.user
            if usersKeys.count(user.id)==0:
                users.append(user)
                usersKeys.append(user.id)
    return users

def getActividad(id):
    return Actividad.objects.filter(user_sector_programa=id).values_list('id','actividad').order_by('actividad')

def getAtributo(id):
    return Atributo.objects.filter(actividad=id).values_list('id','atributo').order_by('atributo')

def getPeso(id):
    return Atributo.objects.filter(actividad=id).values_list('id','peso').order_by('atributo')

def getPesoA(id):
    return Atributo.objects.get(id=id)

def getUser(id):
    return User.objects.get(id=id)

def getProgram(id):
    return Programa.objects.get(id=id)

def getAction(id):
    return Accion.objects.get(id=id)

def getMovements(users, accion, fromDate, toDate):
       
    restrictions = {}
    restrictions['user__in']=users    
    if accion is not None:
        restrictions['accion']=accion
    
    if fromDate is not None and toDate is not None:
        restrictions['fecha__range'] = (fromDate, toDate)    
    if fromDate is not None:
        restrictions['fecha__gte'] = fromDate
    if toDate is not None:
        restrictions['fecha__lte'] = toDate
        
    
    return Bitacora.objects.filter(**restrictions).order_by('fecha')



def getMapaAptitudById(id):
    return Mapa_Aptitud.objects.get(id=id)


def getMapNames(users, programa_id):
    
    userKeys = [user.id for user in users]    
    prog_sectors = User_Programa_Sector.objects.filter(user__in = userKeys, programa=programa_id)
    
    progSectorsKeys = [ps.id for ps in prog_sectors]    
    mp = Mapa_Aptitud.objects.filter(user_sector_programa__in = progSectorsKeys)
        
    for s in prog_sectors:
        sector_maps = Mapa_Aptitud.objects.filter(user_sector_programa__id = s.id)
        if len(sector_maps)==0:  
            raise MissingAptitudeMapsException('no se han generado todos los mapas de aptitud en todos los sectores')
    
    mmaps = []
                
    for s in prog_sectors:
        approved_maps = Mapa_Aptitud.objects.filter(user_sector_programa__id = s.id, estatus='aprobado')
        if len(approved_maps)==0:  
            raise NotApprovedMapsException('no se han aprobado todos los mapas de aptitud')
        mmaps.append(approved_maps)
        
    maps_dic = {}
    for m in mmaps:
        key = m[0].user_sector_programa.id
        value = []
        for v in m:
            value.append(v.nombre + APTITUDE_MAP_SUFFIX)
        maps_dic[key] = value
     
    mapsets = Mapset.objects.filter(user_programa_sector__in = progSectorsKeys)    
    map_names = []
    
    for mp in mapsets:
    
        key = mp.user_programa_sector.id
        nams = maps_dic[key]
        for nam in nams:
            name = nam + '@' + mp.nombre
            map_names.append(name)        
    
    return map_names

        


"""
    get MAPAS
"""

def getMapaValor(id_ups):
    mapa=[]
    for act in Actividad.objects.select_related('user_sector_programa').filter(user_sector_programa__id=id_ups):
        for atr in Atributo.objects.select_related('actividad').filter(actividad__id=act.id):
            for m in Mapa_Valor.objects.select_related('atributo').filter(atributo__id=atr.id):                
                mapa.append((m.id,m.nombre))
                #mapa.append((m.id,m.nombre[1:]))
    return mapa
    

def getMapaAptitud(id_ups):
    mapa=[]    
    for m in Mapa_Aptitud.objects.filter(user_sector_programa=id_ups):
        #mapa.append((m.id,m.nombre[1:]))
        mapa.append((m.id,m.nombre))
    return mapa    

def getMapaAptitudByPtogram(id_ups):
    return Mapa_Aptitud.objects.filter(user_sector_programa=id_ups)
        
    
def getMapaAptitudAdmin(id_ups):
    mapa=[]    
    for m in Mapa_Aptitud.objects.filter(user_sector_programa=id_ups, estatus='aprobado'):
        #mapa.append((m.id,m.nombre[1:]))
        mapa.append((m.id,m.nombre))
    return mapa

"""
Obtiene el location de un programa a partir del ID del programa
"""
def getLocationProgram(program_id):
    programa = Programa.objects.get(pk=program_id)
    return programa.location
    
"""
    get Location y Mapset deacuerdo al id  user_programa_sector
"""    
def getLocation(ups_id):
    return Programa.objects.select_related('programa').get(programa__id=ups_id).location

def getLocationAdmin(programa_id):
    prog = Programa.objects.get(id=programa_id)    
    loc = prog.location        
    return loc
    
def getMapset(ups_id):
    return Mapset.objects.get(user_programa_sector=ups_id).nombre

def getMapsetAdmin(program):    
    return MapsetAdmin.objects.get(program=program)

def getAptitudeNode(node_id):
    return NodoMapaGrupo.objects.get(id=node_id)

def getNodeCut(parent_node):
    return Corte.objects.get(nodo=parent_node)
        
def getAllAptitudeNodes(programa_id):    
    grupo = MapaGruposAptitud.objects.get(programa__id=programa_id)    
    result = NodoMapaGrupo.objects.filter(grupo=grupo).order_by('nombre')        
    if not result:
        return []
    return result    

def getLeaveNodes(programa_id):
    grupo = MapaGruposAptitud.objects.get(programa__id=programa_id)   
    result = NodoMapaGrupo.objects.filter(grupo=grupo, es_final=True).order_by('nombre')        
    if not result:
        return []
    return result

def getRootNode(programa_id):
    grupo = MapaGruposAptitud.objects.get(programa__id=programa_id)   
    node = NodoMapaGrupo.objects.get(nodo_padre__id=None, grupo=grupo)
    return node
    
    
def getNodeSons(node):
    return NodoMapaGrupo.objects.filter(nodo_padre=node)

def getGrupoAptitudByProgramId(programa_id):    
    return MapaGruposAptitud.objects.get(programa__id=programa_id) 
    
    
    
class MissingAptitudeMapsException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

class NotApprovedMapsException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

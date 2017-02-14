from django.contrib.auth.models import User
from django.core.context_processors import request
from django.db.models.query_utils import Q
from lib.D import ROL
from lib.D import PERMISSION as P 
from ordenamiento.models import Sector, User_Programa_Sector, Programa, \
    Actividad, Atributo

def get_sector_nombre():
    return Sector.objects.order_by('nombre')

def get_view_programa(user_id):
    """
    
    """
    us = User_Programa_Sector.objects.filter(user=user_id)
    us = us.values('programa_id').distinct()           
    #print us.query
    
    programa = []
    for u in us:
        programa.append(u['programa_id'])
    
    #print programa          
    view_programa = []
      
    for id in programa:               
        us = User_Programa_Sector.objects.filter(programa=id, user=user_id)
        us = us.values('sector_id')   
    
        sector = []                     
        for u in us:
            s = Sector.objects.get(id=u['sector_id'])
            sector.append({"nombre":s.nombre, "id":u['sector_id']})                
           
        p = Programa.objects.get(id=id);
        view_programa.append({"id":id, "nombre":p.nombre, "sector":sector, })
        
    #print view_programa[]
    """        
    for v in view_programa:
        #print v['id'] , v['nombre'] ,v['sector']
        for a in v['sector']['id']:
            print a
    """     
    return view_programa

"""
util  
"""

def get_supervisor(grupo):    
    users = User.objects.filter(Q(user_permissions__codename=P.SUPERVISOR) & Q(groups__name=grupo))
    combo = [];
    for user in users:
        combo.append([user.id, user.first_name + " " + user.last_name ])
    return combo
    

            
def get_all_rol(rol):    
    lst=[]    
    usr = User.objects.all()    
    for u in usr:
        if u.has_perm(rol) and not u.is_superuser:
            lst.append((u.id,u.first_name + " " + u.last_name))
    return lst

def get_all_operador():    
    return User.objects.filter(Q(user_permissions__codename=P.OPERADOR)).values_list('id','username')

def get_all_operador_and_operador_grupo(grupo):    
    return User.objects.filter(Q(user_permissions__codename=P.OPERADOR)  & Q(groups__name=grupo)).values_list('id','username') 




"""
"""

"""
Should be @deprecated: 
"""
def get_idUserProgramaSector_nombreSector(id):
    #sector = Sector.objects.select_related("sector").filter(sector__user=id)
    lst=[]
    _ups = User_Programa_Sector.objects.filter(user=id)    
    for ups in _ups:
        lst.append((ups.id,ups.sector))      
    return  lst

def getActividad(id):
    return Actividad.objects.filter(user_sector_programa=id).values_list('id','actividad')



def getAtributo(id):
    return Atributo.objects.filter(actividad=id).values_list('id','atributo')
            
def getCountPrograma(id):
    return User_Programa_Sector.objects.filter(user=id).count()
    


























            
            
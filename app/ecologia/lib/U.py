"""
Util
"""
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import simplejson
from ordenamiento.models import Programa, User_Programa_Sector
from operator import itemgetter
from types import FloatType
import math
import operator
import lib.GrassShell as gsh


NUM_CATEGORIAS = 11
APTITUDE_MAP_SUFFIX = "_norm_apt"

#States for aptitude groups
GROUPS_NEW = None
GROUPS_STARTED = 1
GROUPS_CHANGED = 2


def enum(**enums):
    """
    Enum
    """
    return type('Enum', (), enums)

def ajax(fun):
    """
    Decorador para inicializar ajax
    """ 
    def wrap(request):
            if request.is_ajax():
                #if request.method == 'POST':
                message = fun(request)
                json = simplejson.dumps(message)
                return HttpResponse(json, mimetype='application/json')                         
            #return HttpResponseBadRequest()               
    return wrap


def ajax_nan(fun):
    """
    Decorador para inicializar ajax y sobreescribir NAN
    """ 
    def wrap(request):
            if request.is_ajax():
                if request.method == 'POST':
                    msg = fun(request)
                    for key in msg:        
                        if type(msg[key]) is FloatType:
                            if math.isnan(float(msg[key])):
                                msg[key]="NAN"            
                    json = simplejson.dumps(msg)
                    return HttpResponse(json, mimetype='application/json')                         
            return HttpResponseBadRequest()               
    return wrap


def ajax_order(fun):
    """
    Decorador para inicializar ajax ordenado
    """ 
    def wrap(request):
            if request.is_ajax():
                if request.method == 'POST':                    
                    message = fun(request)                 
                    json = simplejson.dumps(message) 
                    
                    """
                    smsg="{\"status\":true,"                    
                    for m in message:
                        smsg += '\"%s\":\"%s\",' % (m[0],m[1])
                    smsg = smsg[0:len(smsg)-1]+"}"                   
                    json = smsg
                    """
                                         
                    return HttpResponse(json, mimetype='application/json')                         
            return HttpResponseBadRequest()               
    return wrap

"""
    USER
"""

def getUsrId(request):
    return request.session['_auth_user_id']
    
def getUsr(request):      
    return User.objects.get(id=getUsrId(request))

def getUsrRol(request):
    return request.session['rol']      

def getUsrLocation(request,id_sector):
    ups = User_Programa_Sector.objects.get(user=getUsrId(request),sector=id_sector)
    return Programa.objects.get(id=ups.programa_id).location



"""
    GRASS
"""

def getMapsetSector(location,mapset,names_avoid):
    
    gsh.grass_init(location,mapset)
    rast = gsh.g_list('rast', False)   
    
    rast.sort()    
    lst = []
    for r in rast:
        if r not in names_avoid:           
            lst.append(("r" + r, r))
    return lst    
    
def getMapSetPermanent(location):
    
    gsh.grass_init(location)
    rast = gsh.g_list('rast')    
      
    rast.sort()

    lst = []
    for r in rast:                  
        lst.append(('r'+r, r))
        
    return lst    
 
def getPuntoDeCorte(data, numCategorias):
    print data    
    f_t = [0] * numCategorias
    
    for l in data:
        l_contents = l.split(',')
        if '*' is not l_contents[0]:
            idx = int(l_contents[0])
            f_t[idx-1] = int(l_contents[1])    
    sum_f=0
    sum_fx=0
    sum_fx2=0
    li_var_a=[]
    li_d_sig=[]
    corte=0

    for i in range(len(f_t)):
        var_a=0    
        x_=i+1
        f=f_t[i]
        fx=f*x_
        fx2=(x_*x_)*f
        sum_f += float(f)
        sum_fx += float(fx)
        sum_fx2 += float(fx2)
        var_a=(sum_fx2/sum_f)-((sum_fx/sum_f)**2)
        li_var_a.append(var_a)

    var_total=var_a  

    for i in range(len(f_t)):
        var_b=0 
        x_=i+1
        f=f_t[i]
        fx=f*x_
        fx2=(x_*x_)*f
        sum_f -= float(f)
        sum_fx -= float(fx)
        sum_fx2 -= float(fx2)
        if i == 10:
            sum_f=f
            sum_fx=fx
            sum_fx2=fx2
        var_b=(sum_fx2/sum_f)-((sum_fx/sum_f)**2)
        d_sig=var_total-(li_var_a[i]+var_b)
        li_d_sig.append(d_sig)
    
    m=max(li_d_sig)
    lugar_corte=[i for i, j in enumerate(li_d_sig) if j == m]
    if len(lugar_corte) == 1:
        corte=lugar_corte[0]+1    
    elif len(lugar_corte) != 1:
        for ii in range(len(f_t)):
            f_v1=ii
            f_v2=f_t[ii]
            for iii in range(len(lugar_corte)):
                if lugar_corte[iii] == f_v1:
                    if f_v2 == 0:
                        corte = f_v1
                        break
        
    return corte
    
    

def getResidualesGower(a):
        
    #num grupos    
    f=len(a)
    #num sectores
    c=len(a[0]) 

    d = [[0]*c for i in range (0,f)]
    
    #matriz transpuesta = b        
    for i in range(f):
        b=list(zip(*a))
        
    li_prom_f=[]
    for i in range(f):
        prom_f=0
        for j in range(len(a[i])):
            prom_f+=a[i][j]
            if j == len(a[i])-1:
                prom_f=prom_f/len(a[i])
                li_prom_f.append(prom_f)
    
    li_prom_c=[]
    for i in range(c):
        prom_c=0
        for j in range(len(b[i])):
            prom_c+=b[i][j]
            if j == len(b[i])-1:
                prom_c=prom_c/len(b[i])
                li_prom_c.append(prom_c)
                        
    prom2_c=0
    for i in range(len(li_prom_c)):
        prom2_c+=float(li_prom_c[i])
        if i == len(li_prom_c)-1:
            prom2_c=prom2_c/len(li_prom_c)
    
    #resiudales de gower
    for i in range(f):
        for j in range(c):        
            d[i][j] = a[i][j]-li_prom_f[i]-li_prom_c[j] + prom2_c
    
    return d    


def getStringFromNumericArray(array):    
    result = ""
    for a in array:        
        result = result + str(a).strip('\n') + ";"
    return result    
    
def getHistogramData(data):
    values = data.split(';')
    hyst_map = {}    
    for i in range(0,len(values)-2):
        vals = values[i].split(',')
        hyst_map[str(vals[0])] = vals[1]    
    hyst_data = []
    for i in range(0,NUM_CATEGORIAS):
        key = str(i+1)
        if key in hyst_map:
            hyst_data.append(hyst_map[key].strip('\n'))            
        else:
            hyst_data.append('0')    
    return hyst_data

    
    
    
     
    
    
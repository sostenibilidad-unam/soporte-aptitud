from grass.script.setup import init
from django.utils.encoding import smart_str, smart_unicode
import base64
import grass.script as grass
import os
import Image
import U as util
from ordenamiento.models import NodoMapaGrupo, Corte
import ordenamiento.querys as q


"""
    Variables de entorno de GRASS
"""
GISBASE = smart_str(os.environ['GISBASE'])
GISDBASE = smart_str(os.environ['GISDBASE'])

MAPSET = ""
LOCATION = ""

LEFT_NODE = "left"
RIGTH_NODE = "right"

"""
    Conexion a Grass
"""
def grass_init(location, mapset='PERMANENT'):    
    global MAPSET
    global LOCATION
    LOCATION = smart_str(location)
    MAPSET = smart_str(mapset)   
    

def grass_open():
    global MAPSET
    global LOCATION
    init(GISBASE, GISDBASE, LOCATION, MAPSET)
    

def grass_close():
    global MAPSET
    global LOCATION
    
    os.environ['LD_LIBRARY_PATH'] = ""
    os.environ['GIS_LOCK'] = ""
    
    gisrc = os.environ['GISRC'];
    if os.path.exists(gisrc):
        os.remove(gisrc)
    
    gislock = GISDBASE + "/" + LOCATION + "/" + MAPSET + "/.gislock"
    if os.path.exists(gislock):
        os.remove(gislock)
    
    LOCATION = ""
    MAPSET = ""
   

def grass_sh(fun):
    """
        Decorador de conexion a grass
    """
    def f(*args, **kwargs): 
        try:              
            grass_open()
            ff = fun(*args, **kwargs)
        except:
            raise
        finally:
            grass_close()
        return ff                    
    return f


#Validar nombre en grass
def isVarGrass(str):
    if not str:
        return False
    for s in str:
        if not s.isalpha() and not s.isdigit() and not s == '_':
            return False
    return True


# Get location
def getLocation():   
    location = []            
    for i in os.listdir(GISDBASE):
        if os.path.isdir(GISDBASE + "/" + i):
            location.append(i)          
    return location


# get mapset
def getMapSet(location):    
    location = smart_str(location)
    mapset = []               
    for j in os.listdir(GISDBASE + "/" + location):
        if os.path.isdir(GISDBASE + "/" + location + "/" + j):
            mapset.append(j)                       
    return  mapset

    
#create mapset
def create_mapset(name, location):
    name = smart_str(name)
    location = smart_str(location) 
    init(GISBASE, GISDBASE, location, mapset='PERMANENT')   
    grass.run_command('g.mapset', 'c', mapset=name)
    grass_close()


@grass_sh
def info(name, type_capa):
    name = smart_str(name)   
    if type_capa == 'r':      
        #return grass.raster_info(name)
        vals = grass.raster_info(name)
    elif type_capa == 'v':        
        #return grass.vector_info_topo(name)
        vals = grass.vector_info_topo(name)
    #rounding values    
    vals['min'] = round(vals['min']) 
    vals['max'] = round(vals['max'])
    return vals
    
@grass_sh
def remove(capa):    
    capa = smart_str(capa)
    grass.run_command("g.remove", rast=capa)
    
    
# Cambiar mapset
@grass_sh
def swap_mapset(mapset): 
    mapset = smart_str(mapset)
    global MAPSET       
    if (mapset != MAPSET):                                    
            grass.run_command("g.mapset", mapset=mapset)
            MAPSET = mapset
            #os.environ['HISTFILE'] = GISDBASE + "/" + LOCATION + "/" + MAPSET + "/" + ".bash_history"
            
# list de mapas
@grass_sh
def g_list(type, permanent=True):    
    """
    @param type : rast,rast3d,vect,oldvect,asciivect,icon,labels,sites,region,region3d,group,3dvie
    @param permanet si es True muestra permanent de lo contrario muestra mapset
    
    @return list of tuples map
    """
    lst = []    
    
    if(permanent):
        m = "PERMANENT"
    else:
        m = MAPSET    
    
    for pair in grass.list_pairs(type):
        if(pair[1] == m):
            if not util.APTITUDE_MAP_SUFFIX in pair[0]:
                lst.append(pair[0])
    return lst 

# list de mapas
@grass_sh
def list_raster_sector():    
    """    
    @return list of tuples map
    """
    lst = []
    for pair in grass.list_pairs('rast'):
        if(pair[1] == MAPSET and pair[0][0] != 'f'):
            lst.append(pair[0])
    lst.sort()
    return lst

    
#vista previa

@grass_sh
def preview(capa, type_capa, id_usr, location):
    from settings import DJANGO_MEDIA
    
    import hashlib
    m = hashlib.md5(str(id_usr) + capa).hexdigest()
    
    path_img = "/tmp/" + m
    path_img_png = "/tmp/" + m + ".png"
    
    try:              
        grass.run_command("d.mon", start="png7")
        if type_capa == 'r':
            
            grass.run_command("d.his", h_map=capa, i_map="sombra_relieve", brighten="0")
            #grass.run_command("d.rast", map=capa)
            #Se despliega maoa vectorial con las carreteras
            grass.run_command("d.vect", map="ViasComunicacion", type="line", width=1)
            #Se despliega un mapa con las localidades urbanas
            grass.run_command("d.vect", map="LocUrbanas", display="shape", type="area", width=1)
            # Se dibuhja una malla con las latitudes y longitudes
            
            # @@TODO: verificar que funcione asi
            
            try:
                settings_path = DJANGO_MEDIA + "../../opt/grassdata/" + location + "/grid_settings.txt"            
                data_file = open(settings_path, 'r')
                data = data_file.readlines()     
                settings_line = data[0].strip()
                size = settings_line
            except:
                size = '00:05:00'            
            
            grass.run_command("d.grid","gc", size=size, color="black", origin="0,0", textcolor="black")
            # Se dibuja una barra de escalas, escala grafica
            # @@TODO: verificar que funcione asi
            grass.run_command("d.barscale", "t", tcolor="black", at="65,90")            
            # Se dibuj un recuadro dentro del mapa
            grass.run_command("d.frame", frame="label", at="3,25,12.3,30")
            # Se le asigna el color blanco como fondo a ese recuadro
            grass.run_command("d.erase", "white")
            
            
            info_vals = grass.raster_info(capa)    
            
            if info_vals["datatype"] == "CELL":
                # Se muestran las categorias del mapa raster en el recuadro
                grass.run_command("d.legend", map=capa, lines=0, labelnum=5, at="0,100,0,8", flags="fc")                
            else:                
                # Se muestran las categorias del mapa raster en el recuadro
                grass.run_command("d.legend", map=capa, lines=0, labelnum=5, at="0,100,0,8")
                        
        elif type_capa == 'v':
            grass.run_command("d.vect", map=capa)        
                       
        grass.run_command("d.out.png", output=path_img, res="2")
        img_zoom = base64.b64encode(open(path_img_png, "rb").read())
                
        img = Image.open(path_img_png)        
        img = img.resize((640, 480), Image.ANTIALIAS)
        img.save(path_img_png)
        img_view = base64.b64encode(open(path_img_png, "rb").read())
        
        if os.path.exists(path_img_png):
            os.remove(path_img_png)
        
        
    except:
        raise
    finally:
        grass.run_command("d.mon", stop="png7")
            
    return img_view, img_zoom


"""
    Funcion Continua Mapa de valor
"""

@grass_sh
def fv_campana(mapa, capa, min_max, amplitud, min_func, max_func):
    
    mapa = smart_str(mapa)
    capa = smart_str(capa)
    # casting float
    float(min_max)
    float(amplitud)
    
    # funcion    
    grass.mapcalc("$mapa=exp(-exp(($capa-$min_max)/$amplitud, 2))", mapa=mapa, capa=capa, min_max=min_max, amplitud=amplitud)
    
    # normalizar    
    normalizar(mapa, min_func, max_func);

@grass_sh
def fv_campana_inv(mapa, capa, min_max, amplitud, min_func, max_func):
    
    mapa = smart_str(mapa)
    capa = smart_str(capa)
    # casting float
    float(min_max)
    float(amplitud)
    
    # funcion    
    grass.mapcalc("$mapa=1-(exp(-exp(($capa-$min_max)/$amplitud, 2)))", mapa=mapa, capa=capa, min_max=min_max, amplitud=amplitud)
    
    # normalizar    
    normalizar(mapa, min_func, max_func);    

@grass_sh    
def fv_creciente_cv(mapa, capa, p_control, min_func, max_func):
    mapa = smart_str(mapa)
    capa = smart_str(capa)
    # casting float
    float(p_control)    
    
    # funcion
    grass.mapcalc("$mapa=exp($p_control*$capa)", mapa=mapa, capa=capa, p_control=p_control)
    
    # normalizar    
    normalizar(mapa, min_func, max_func);
    
@grass_sh
def fv_creciente_cx(mapa, capa, p_control, min_func, max_func):
    mapa = smart_str(mapa)
    capa = smart_str(capa)
    # casting float
    float(p_control)    
    
    # funcion
    #grass.mapcalc("$mapa=1-(exp(-$p_control*$capa))", mapa=mapa, capa=capa, p_control=p_control)
    grass.mapcalc("$mapa=1-(exp($p_control*$capa))", mapa=mapa, capa=capa, p_control=p_control)
    
    # normalizar    
    normalizar(mapa, min_func, max_func);

@grass_sh
def fv_decreciente_cv(mapa, capa, p_control, min_func, max_func):
    mapa = smart_str(mapa)
    capa = smart_str(capa)
    # casting float
    float(p_control)    
    
    # funcion
    grass.mapcalc("$mapa=exp(-$p_control*$capa)", mapa=mapa, capa=capa, p_control=p_control)
    
    # normalizar    
    normalizar(mapa, min_func, max_func);

@grass_sh
def fv_decreciente_cx(mapa, capa, p_control, min_func, max_func):
    mapa = smart_str(mapa)
    capa = smart_str(capa)
    # casting float
    float(p_control)    
    
    # funcion
    grass.mapcalc("$mapa=1-exp (($capa-30.0)/$p_control)", mapa=mapa, capa=capa, p_control=p_control)
    
    # normalizar    
    normalizar(mapa, min_func, max_func);
    
   
@grass_sh
def fv_difusa(mapa, capa, a, b, c, d, min, max):
    
    mapa = smart_str(mapa)
    capa = smart_str(capa)  
    
    #i = grass.raster_info(capa)
    #min = float(i['min'])
    #max = float(i['max'])
    a = float(a)
    b = float(b)
    c = float(c)
    d = float(d)
        
    a = float((a-min)/(max-min))    
    b = float((b-min)/(max-min))
    c = float((c-min)/(max-min))
    d = float((d-min)/(max-min))
        
    grass.mapcalc("capa_norm_temp=(($capa-$min)/($max - $min))", capa=capa, max=max, min=min)
    grass.mapcalc("alpha1_temp=(1-((capa_norm_temp - $a)/($b - $a)))*(3.14159265358979/2)", a=a, b=b)
    grass.mapcalc("alpha1_gra_temp=(alpha1_temp*180)/3.14159265358979")
    grass.mapcalc("alpha2_temp=((capa_norm_temp - $c)/($d - $c))*(3.14159265358979/2)", c=c, d=d)
    grass.mapcalc("alpha2_gra_temp=(alpha2_temp*180)/3.14159265358979")
    grass.mapcalc("$mapa=if(capa_norm_temp < $a,0,if(capa_norm_temp > $d,0,if(capa_norm_temp >= $a && capa_norm_temp <= $b,(exp(cos(alpha1_gra_temp),2)),if(capa_norm_temp > $b && capa_norm_temp < $c,1,if(capa_norm_temp >= $c && capa_norm_temp <= $d,(exp(cos(alpha2_gra_temp),2)))))))", a=a, b=b, c=c, d=d, mapa=mapa)
    grass.run_command("g.remove", rast='capa_norm_temp')
    grass.run_command("g.remove", rast='alpha1_temp')
    grass.run_command("g.remove", rast='alpha2_temp')  
    grass.run_command("g.remove", rast='alpha1_gra_temp')
    grass.run_command("g.remove", rast='alpha2_gra_temp')  
      
    grass.run_command("r.colors", 'n', map=mapa, color='byg')       
    

def normalizar(mapa, min, max): 
    mapa = smart_str(mapa)
    
    # obtener max y min de r.info    
    #i = grass.raster_info(mapa)
    #_min = i['min']
    #_max = i['max']
    
    
    # normalizar
    grass.mapcalc("$mapa=($mapa-$min)/($max-$min)", mapa=mapa, min=min, max=max)

    #Eliminacion de los datos menores a cero (ya esta normalizada)
    grass.mapcalc("$mapa=if($mapa>=0,$mapa,0)", mapa=mapa)
    #Eliminacion de los datos mayores a uno (ya esta normalizada y la ecuacion de la funcion de valor considera la distancia a partir de 150 metros, es decir, las distancias menores no deben ser tomadas en cuenta)
    grass.mapcalc("$mapa=if($mapa>1.0,0,$mapa)", mapa=mapa)

    #tabla de colores 
    grass.run_command("r.colors", 'n', map=mapa, color='byg')       


"""
    Funcion Discreta Mapa de valor
"""

@grass_sh
def fun_discreta(capa, reclass, discreta):    
    capa = smart_str(capa)
    p1 = grass.pipe_command('r.stats', flags='n', input=capa)
    s = ""
    for i in p1.stdout: 
        i = int(i)
        s += "%s = %s \n" % (i , reclass[i - 1])
    
    grass.write_command('r.reclass', input=capa, output=discreta, stdin=s)


"""
    Mapa aptitud
"""

@grass_sh
def mapa_aptitud(aptitud, exp):
        
    from settings import DJANGO_MEDIA
    
    exp = aptitud + "=" + exp
    grass.mapcalc(exp)

    i = grass.raster_info(aptitud)
    _min = i['min']
    _max = i['max']
    
    mapa_n = aptitud + util.APTITUDE_MAP_SUFFIX    
    # normalizar
    grass.mapcalc("$mapa_n=($mapa-$min)/($max-$min)", mapa=aptitud, min=_min, max=_max, mapa_n=mapa_n)
    
    #Reclasificacion en 5 categorias
    #r.mapcalc "apt_min_5cats=if(aptitud_mineria<0.06,1,if(aptitud_mineria<0.12,2,if(aptitud_mineria<0.25,3,if(aptitud_mineria<0.5,4,5))))"
    #grass.mapcalc("$mapa=if($mapa<0.06,1,if($mapa<0.12,2,if($mapa<0.25,3,if($mapa<0.5,4,5))))", mapa=aptitud)
    grass.mapcalc("$mapa=if($mapa_n<0.06,1,if($mapa_n<0.12,2,if($mapa_n<0.25,3,if($mapa_n<0.5,4,5))))", mapa=aptitud, mapa_n=mapa_n)
    
    #Aplicar paleta de colores
    #r.colors -n  map=apt_min_5cats rules=coloraptitud.txt
    
    #grass.run_command('r.colors', 'n', map=aptitud, rules=DJANGO_MEDIA + "/lib/coloraptitud.txt")
    # Se quita la 'n' para no invertir paleta de colores
    grass.run_command('r.colors', map=aptitud, rules=DJANGO_MEDIA + "/lib/coloraptitud.txt")
    grass.run_command('r.category', map=aptitud, rules=DJANGO_MEDIA + "/lib/cat_labels.txt")
    
    return True

"""
    Grass Comandos
"""

@grass_sh
def desagrupar(capa, output):
    capa = smart_str(capa)
    grass.run_command('r.clump', input=capa, output=output)

@grass_sh
def distance(capa, distance):
    capa = smart_str(capa)
    grass.run_command('r.grow.distance', input=capa, distance=distance, metric='euclidean')
    grass.mapcalc("$distance=$distance*mascara", distance=distance)
    grass.mapcalc("$distance=$distance/1000", distance=distance)
    grass.run_command('r.colors', map=distance, color="rainbow")
    
    
@grass_sh
def pendiente(capa, slope, format_):
    capa = smart_str(capa)
    grass.run_command('r.slope.aspect', elevation=capa, slope=slope, format=format_)

@grass_sh
def mascara(capa, maskcats):
    capa = smart_str(capa)
    grass.run_command('r.mask', input=capa, maskcats=maskcats)

@grass_sh
def nulos(capa, setnull, local_name, mapset):
    capa = smart_str(capa)    
    res = grass.find_file(capa, element='cell', mapset=mapset)
    print res['name']
    if res['name']:
        grass.run_command("g.copy", rast=(capa, local_name))    
        grass.run_command('r.null', map=local_name, setnull=setnull)
    else:
        grass.run_command("g.copy", rast=(capa+"@PERMANENT", local_name))    
        grass.run_command('r.null', map=local_name, setnull=setnull)



@grass_sh
def importa_capa(nombre_capa,user_id,ascii_file):
    import time
    
    millis = int(round(time.time()*1000))
    archivo_ascii_output = "imp_" + nombre_capa + "_" + str(user_id) + "_" + str(millis)  + ".txt"   
    ascii_out = GISDBASE + "/" + LOCATION + "/" + archivo_ascii_output
    with open(ascii_out, 'wb+') as destination:
        for chunk in ascii_file.chunks():
            destination.write(chunk)
    res = grass.run_command('r.in.arc', input=ascii_out, output=nombre_capa)
    
    response = {}
    response["grass_res"] = res
    response["file_temp_fullpath"] = ascii_out
    return response      

@grass_sh
def exporta_capa(capa,user_id, isPermanent, mapset):
    import time
    
    capa_fullname = None
    millis = int(round(time.time()*1000))
    archivo_ascii_output = "exp_" + capa + "_" + str(user_id) + "_" + str(millis)
    
    if isPermanent == True:
        ascii_out = GISDBASE + "/" + LOCATION + "/" + archivo_ascii_output
    else:
        ascii_out = GISDBASE + "/" + LOCATION + "/" + mapset + "/" + archivo_ascii_output    
    res = grass.run_command('r.out.arc', input=capa, output=ascii_out)
    response = {}
    if res==0:
        file_assci = open(ascii_out)
        response["file"] = file_assci
        response["file_size"] = os.path.getsize(ascii_out)         
        response["file_temp_fullpath"] = ascii_out
    else:
        return None
    return response

@grass_sh
def estadistica(capa):
    capa = smart_str(capa)
    p = grass.pipe_command('r.stats', "lan", input=capa)
    res = []
    for i in p.stdout:
        if i.strip().split():
            info = i.strip().split()
            if len(info)==2:
                line = []
                line.append(info[0])
                line.append('                 ')
                line.append(info[1])
                res.append(line)
            elif len(info)==4:
                line = []
                line.append(info[0])
                line.append('                 ')
                line.append(info[3])
                res.append(line)
            else:
                res.append(info)    
    return res


@grass_sh
def funcion_discreta_reclass(fileNewValues,nombre_mapa_entrada,nombre_mapa_salida,user_id,isPermanent, mapset):
    import time
    
    ascii_out = None
    millis = int(round(time.time()*1000))
    archivo_ascii_output = "temp_fdiscreta_" + nombre_mapa_entrada + "_" + str(user_id) + "_" + str(millis)
    if isPermanent == True:
        ascii_out = GISDBASE + "/" + LOCATION + "/" + archivo_ascii_output + ".txt"
    else:
        ascii_out = GISDBASE + "/" + LOCATION + "/" + mapset + "/" + archivo_ascii_output + ".txt"
    # escribe el archivo temporal para realizar reclasificacion
    ascii_file = open(ascii_out, 'wb+')
    ascii_file.write(fileNewValues)
    ascii_file.close()
    p = grass.run_command('r.reclass', input=nombre_mapa_entrada,output=nombre_mapa_salida,rules=ascii_out)    
    grass.mapcalc("$mapa=($mapa/100.0)", mapa=nombre_mapa_salida)    
    # eliminamos el archivo ascii temporal
    os.remove(ascii_out)
    grass.run_command("r.colors", 'n', map=nombre_mapa_salida, color='byg')

@grass_sh
def getValoresDiscretos(capa):    
    capa = smart_str(capa)
    p = grass.pipe_command('r.stats', "ln", input=capa)
    res = []    
    for i in p.stdout:
        print i
        info = i.strip().split()
        
        if info:            
            if len(info)==1:
                line = []
                line.append(info[0])
                line.append('                      ')                
                res.append(line)            
            else:
                res.append(info)                    
    return res




def getGrassMapImage(capa, type_capa, id_usr, location):
    
    from settings import DJANGO_MEDIA    
    import hashlib    
    capa = smart_str(capa)
    m = hashlib.md5(str(id_usr) + capa).hexdigest()    
    path_img = "/tmp/" + m
    path_img_png = "/tmp/" + m + ".png"    
    try:              
        grass.run_command("d.mon", start="png7")
        if type_capa == 'r':
            grass.run_command("d.rast", map=capa)
            #grass.run_command("d.his", i_map=capa, i_map="sombra_relieve", brighten="0")
            
            #Se despliega maoa vectorial con las carreteras
            #grass.run_command("d.vect", map="ViasComunicacion", type="line", width=1)
            #Se despliega un mapa con las localidades urbanas
            #grass.run_command("d.vect", map="LocUrbanas", display="shape", width=1)
            # Se dibuhja una malla con las latitudes y longitudes
            # @@TODO: verificar que funcione asi
            try:
                settings_path = DJANGO_MEDIA + "../../opt/grassdata/" + location + "/grid_settings.txt"            
                data_file = open(settings_path, 'r')
                data = data_file.readlines()     
                settings_line = data[0].strip()
                size = settings_line
            except:
                size = '00:05:00'            
            
            grass.run_command("d.grid","gc", size=size, color="black", origin="0,0", textcolor="black")
            # Se dibuja una barra de escalas, escala grafica
            # @@TODO: verificar que funcione asi
            grass.run_command("d.barscale", "t", tcolor="black", at="65,90")
            # Se dibuj un recuadro dentro del mapa
            grass.run_command("d.frame", frame="label", at="3,25,12.3,30")
            # Se le asigna el color blanco como fondo a ese recuadro
            #grass.run_command("d.erase", "white")
            # Se muestran las categorias del mapa raster en el recuadro
            grass.run_command("d.legend", map=capa, lines=0, labelnum=5, at="0,100,0,8")
                    
                          
        elif type_capa == 'v':
            grass.run_command("d.vect", map=capa)                               
        grass.run_command("d.out.png", output=path_img, res="2")
        img_zoom = base64.b64encode(open(path_img_png, "rb").read())                
        if os.path.exists(path_img_png):
            os.remove(path_img_png)                            
    except:
        raise
    finally:
        grass.run_command("d.mon", stop="png7")            
    return img_zoom
            


def crea_nodo_grupo_aptitud(grupo, localidad, mapset, maps, prefix, numCategorias, nodo_padre_id, user_id, mask, position, final):    
    
    localidad = smart_str(localidad)
    mapset = smart_str(mapset)    
    init(GISBASE, GISDBASE, localidad, mapset=mapset)        
    component = "c"        
    grass.run_command("r.mask", flags="r")
    if mask:
        grass.run_command("r.mask", input=mask, maskcats="1", flags="o")    
    grass.run_command("i.pca", input=maps, output=component)
    
    for i in range(1,len(maps)):
        index = i+1
        current = component + "." + str(index)
        grass.run_command("g.remove", rast=current)
    
    first_component = component + "_" + prefix
    grass.run_command("g.rename", rast=("c.1",first_component))    
    first_component_reescaled = first_component + 'r'
    grass.run_command("r.rescale", flags="-o", input=first_component, output=first_component_reescaled, to=(1,11))
    
    p = grass.pipe_command("r.stats", flags = "c", input = first_component_reescaled, fs = ',')    
    data = []
    for line in p.stdout:        
        if line:                              
            data.append(line)
    
    histogramData = util.getStringFromNumericArray(data)
    if len(data)==1:
        print "No hay categorias suficientes para cortar"        
        raise
    try:
        corte_val = util.getPuntoDeCorte(data,numCategorias)
    except:
        print "error calculando punto de corte division entre cero"
        corte_val = 1
            
    nodo = NodoMapaGrupo(nodo_padre_id=nodo_padre_id, nombre_primer_componente=first_component, nombre_primer_componente_reescalado=first_component_reescaled, es_final=True, histogram_data = histogramData, grupo=grupo, position=position, mascara=mask, nombre=prefix)   
    corte = crea_corte(nodo, prefix, corte_val, user_id, localidad)
    grass_close()
    return nodo, corte



def crea_corte(nodo, prefix, corte_val, user_id, location):
    
    from settings import DJANGO_MEDIA
    color_cut_path = DJANGO_MEDIA + "/lib/cut_colors.txt"        
    mask_a = "ca_" + prefix
    mask_b = "cb_" + prefix
    cut_map = "cut_" + prefix
    nombre_corte = prefix
    grass.mapcalc(mask_a + "=if(" + nodo.nombre_primer_componente_reescalado + " <= " + str(corte_val) + ",1,0)")
    grass.mapcalc(mask_b + "=if(" + nodo.nombre_primer_componente_reescalado + " > " + str(corte_val) + ",1,0)")
    grass.mapcalc(cut_map + '=if('+mask_a+'==1,1,if('+mask_b+'==1,2,0))')
    grass.run_command("r.mask", flags="r")
    grass.run_command("r.null", map=mask_a, setnull="0")
    grass.run_command("r.null", map=mask_b, setnull="0")                
    grass.run_command("r.colors", map=cut_map, rules=color_cut_path)
    imagen = getGrassMapImage(cut_map, 'r', user_id, location)    
    corte_obj = Corte(imagen=imagen, nodo=nodo, valor_corte = corte_val, nombre_mascara_a=mask_a, nombre_mascara_b=mask_b, nombre_corte=nombre_corte,nodo_hijo_a=None, nodo_hijo_b=None, corte_ejecutado=False, selected = True)    
    return corte_obj
   
    
def realiza_cortes(mask_a, mask_b, corte, nodo_padre, prefix, user_id, numCategorias, localidad, mapset, maps, grupo):

    nodo_a, corte_a = realiza_corte_a(mask_a, corte, nodo_padre.id, prefix+'.1', user_id, numCategorias, localidad, mapset, maps, grupo)
    nodo_b, corte_b = realiza_corte_b(mask_b, corte, nodo_padre.id, prefix+'.2', user_id, numCategorias, localidad, mapset, maps, grupo)        
        
    nodo_padre.es_final = False
    nodo_padre.save()
    
    nodo_a.save()
    nodo_b.save()
    
    corte_a.nodo=nodo_a
    corte_b.nodo=nodo_b
    corte_a.save()
    corte_b.save()
    
    corte.corte_ejecutado = True
    corte.nodo_hijo_a = nodo_a
    corte.nodo_hijo_b = nodo_b        
    corte.save()    
    

 
def realiza_corte_a(mask_a, corte, nodo_padre, prefix, user_id, numCategorias, localidad, mapset, maps, grupo):
    nodo_a, corte_a = crea_nodo_grupo_aptitud(grupo, localidad, mapset, maps, prefix, numCategorias, nodo_padre, user_id, mask_a, LEFT_NODE, True)
    return nodo_a, corte_a


    
def realiza_corte_b(mask_b, corte, nodo_padre, prefix, user_id, numCategorias, localidad, mapset, maps, grupo):    
    nodo_b, corte_b = crea_nodo_grupo_aptitud(grupo, localidad, mapset, maps, prefix, numCategorias, nodo_padre, user_id, mask_b, RIGTH_NODE, True)
    return nodo_b, corte_b



def modifica_corte(nodo_id, corte, user_id, localidad, mapset):    
    
    localidad = smart_str(localidad)
    mapset = smart_str(mapset)    
    init(GISBASE, GISDBASE, localidad, mapset=mapset)        
    from settings import DJANGO_MEDIA
    node = q.getAptitudeNode(nodo_id)    
    cut = q.getNodeCut(node)    
    mask_a = cut.nombre_mascara_a
    mask_b = cut.nombre_mascara_b
    cut_map = "cut_" + cut.nombre_corte                       
    component = node.nombre_primer_componente_reescalado
    color_cut_path = DJANGO_MEDIA + "/lib/cut_colors.txt"
    grass.run_command("r.mask", flags="r")    
    grass.mapcalc(mask_a + '=if(' + component + ' <= ' + str(corte) + ',1,0)')
    grass.mapcalc(mask_b + '=if(' + component + ' > ' + str(corte) + ',1,0)')    
    grass.mapcalc(cut_map + '=if(' + mask_a + '==1,1,if(' + mask_b + '==1,2,0))')    
    grass.run_command("r.null", map=mask_a, setnull="0")
    grass.run_command("r.null", map=mask_b, setnull="0")                
    grass.run_command("r.colors", map=cut_map, rules=color_cut_path)
    imagen = getGrassMapImage(cut_map, 'r', user_id, localidad)    
        
    if cut.corte_ejecutado:
        remove_sons(node)
    grass_close()    
    node.es_final = True    
    node.save()
    cut.imagen = imagen
    cut.valor_corte = corte
    cut.nodo_hijo_a = None
    cut.nodo_hijo_b = None
    cut.corte_ejecutado = False
    cut.selected = False
    cut.save()  


def eliminate_root(nodo_id, localidad, mapset):
    
    localidad = smart_str(localidad)
    mapset = smart_str(mapset)    
    init(GISBASE, GISDBASE, localidad, mapset=mapset)
        
    node = q.getAptitudeNode(nodo_id)    
    cut = q.getNodeCut(node)    
        
    mask_a = cut.nombre_mascara_a
    mask_b = cut.nombre_mascara_b
    comp = "c_"+cut.nombre_corte
    compr = "c_"+cut.nombre_corte+"r"
    cut_map = "cut_" + cut.nombre_corte
    grass.run_command("g.remove", rast=mask_a)
    grass.run_command("g.remove", rast=mask_b)
    grass.run_command("g.remove", rast=cut_map)
    grass.run_command("g.remove", rast=compr)
    grass.run_command("g.remove", rast=comp)    
    
    grass_close()
    node.delete()
    cut.delete()    
    


def eliminate_sons(nodo_id, localidad, mapset):
    
    localidad = smart_str(localidad)
    mapset = smart_str(mapset)    
    init(GISBASE, GISDBASE, localidad, mapset=mapset)
        
    node = q.getAptitudeNode(nodo_id)    
    cut = q.getNodeCut(node)    
        
    if cut.corte_ejecutado:
        remove_sons(node)
    grass_close()    
    node.es_final = True    
    node.save()
    cut.nodo_hijo_a = None
    cut.nodo_hijo_b = None
    cut.corte_ejecutado = False
    cut.selected = False
    cut.save()

    
    
def remove_sons(node):
    
    hijos = q.getNodeSons(node)
    for n in hijos:        
        remove_sons(n)
        cut = q.getNodeCut(n)    
        mask_a = cut.nombre_mascara_a
        mask_b = cut.nombre_mascara_b
        comp = "c_"+cut.nombre_corte
        compr = "c_"+cut.nombre_corte+"r"
        cut_map = "cut_" + cut.nombre_corte
        grass.run_command("g.remove", rast=mask_a)
        grass.run_command("g.remove", rast=mask_b)
        grass.run_command("g.remove", rast=cut_map)
        grass.run_command("g.remove", rast=compr)
        grass.run_command("g.remove", rast=comp)
        cut.delete()
        n.delete()
    return    
        
        
def get_residuals(programa_id, maps, localidad, mapset, usr_id):
    
    from lib import U        
    localidad = smart_str(localidad)
    mapset = smart_str(mapset)
        
    init(GISBASE, GISDBASE, localidad, mapset=mapset)           
    
    nodes = q.getLeaveNodes(programa_id)
    grupo = q.getGrupoAptitudByProgramId(programa_id)
    
    if len(nodes)<=1:
        grass_close()        
        return [], "db"
    
    if grupo.nodos:
        actual_nodes = getArrayFromString(grupo.nodos)
    else:
        actual_nodes = []    
        
    if compare_nodes(nodes, actual_nodes):
        results = []
        res = getMatrixFromString(grupo.residuales) 
        for i in range(0,len(res)):
            nombre = nodes[i].nombre
            results.append({'nombre':nombre, 'data':res[i]})
        grass_close()    
        return results, "db"            
        
    masks = []    
    command_string = 'X'    
    for n in nodes:
        print n.nombre
        grass.run_command("r.null", map=n.mascara, null="0")
        masks.append(n.mascara)
    for i in range(0,len(masks)):
        current_command = 'if('+ masks[i] +'==1,'+str(i+1)+',X)'
        command_string = command_string.replace('X', current_command)         
    
    command_string = command_string.replace('X', '0')
    print command_string   
    grass.run_command("g.remove", rast="grupos")
    grass.mapcalc('grupos=' + command_string)
    averages_data = []
    
    for m in maps:        
        temp = m.split('@')
        local_name = temp[0]                
        print " current map: ",local_name
        grass.run_command("r.average", base="grupos", cover = local_name, output="averages", flags="-o")
        curr_data = get_averages()
        averages_data.append(curr_data)
        
    averages_data = zip(*averages_data)
    residuals = U.getResidualesGower(averages_data)
    results = []
    for i in range(0,len(residuals)):
        nombre = nodes[i].nombre
        results.append({'nombre':nombre, 'data':residuals[i]})
    
    grass.run_command("r.null", map="grupos", setnull="0")        
    imagen = getGrassMapImage("grupos", 'r', usr_id, localidad)
    grass_close()        
    save_residuals_data(programa_id, averages_data, residuals, nodes, maps, imagen)    
                    
    return results, "processed"
    
    
def save_residuals_data(programa_id, averages_data, residuals, nodes, maps, imagen):
    
    grupo = q.getGrupoAptitudByProgramId(programa_id)    
    averages_str = ''
    residuals_str = ''
    nodes_str = ''
    maps_str = ''    
    for a in averages_data:
        averages_str += util.getStringFromNumericArray(a) +'#'
    for r in residuals:
        residuals_str += util.getStringFromNumericArray(r) +'#'
    for n in nodes:
        nodes_str += n.nombre + '#'
    #for m in maps:
    #    maps_str += m + '#'    
    grupo.residuales = residuals_str
    grupo.promedios = averages_str
    grupo.nodos = nodes_str
    #grupo.mapas = maps_str
    grupo.imagen = imagen    
    grupo.save()

def compare_nodes(new, actual):
    if len(new)!=len(actual):
        return False
    map_n = dict([ (n.nombre, n.nombre) for n in new])            
    for a in actual:
        if not map_n[a]:
            return False
    return True    



def getMatrixFromString(str_matrix):
    rows = str_matrix.split('#')
    matrix = []
    for r in rows:
        if r:
            cells = r.split(';')
            new_line = []
            for c in cells:
                if c:
                    new_line.append(c) 
            matrix.append(new_line)
    return matrix


def getArrayFromString(str_array):
    elements = str_array.split('#')
    result = []
    for e in elements:
        if e:
            result.append(e)
    return result
        
        
    
def import_maps_to_local_mapset(maps, localidad, mapset):
    
    localidad = smart_str(localidad)
    mapset = smart_str(mapset)    
    init(GISBASE, GISDBASE, localidad, mapset=mapset)    
    
    for m in maps:        
        temp = m.split('@')
        local_name = temp[0]
        grass.run_command("g.copy", rast=(m,local_name))
    
    grass_close()
    
        
        
def remove_mask():
    grass.run_command("r.mask", flags="r")
    
    
def get_averages():    
    import re
    regex = re.compile('[0-9]+:[0-9]+:')
    p = grass.pipe_command("r.info", map="averages", flags="h")    
    averages = []
    
    for line in p.stdout:        
        if line:                              
            if re.search(regex, line):
                line_array = line.split(':')
                if line_array[0].strip(' ')!='0':
                    averages.append(float(line_array[2].strip(' ')))        
    
    return averages

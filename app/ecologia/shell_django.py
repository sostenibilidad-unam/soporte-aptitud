# -*- coding: utf-8 -*-
import os

os.environ['DJANGO_SETTINGS_MODULE'] = "settings"

from django.contrib.auth.models import User,Group
from django.db.models.query_utils import Q
from ordenamiento.models import *
import lib.GrassShell as gsh


m = Mapa_Valor.objects.get(id=9)

print m.atributo_id
print m.atributo.actividad_id
print m.atributo.peso


a=["1","2","3"]
i=0
while (i < len(a)):
	if a.pop() in a:
		print "si"
		break
	i+=1
print "no"
"""
a = Atributo.objects.filter(actividad=3).values_list('id','peso').order_by('atributo')
print a.query
print a
"""

#u = User.objects.filter(Q(user_permissions__codename=P.ROOT2) | Q(is_superuser=True))
#return Atributo.objects.filter(actividad=id).values_list('id','peso').order_by('atributo')
"""
lst=[]
for m in Mapa_Aptitud.objects.filter(user_sector_programa=7): 
	lst.append(m.nombre)


if "ffa_con" in lst:
	print "hola"
"""
"""
location = "Salsipuedes"
mapset = "sector7"

gsh.grass_init(location,mapset)
lst = gsh.list_raster_sector()
print lst

if "dist_campamento_pes" in lst:
	print "si"
"""


#print Actividad.objects.filter(actividad="conser",user_sector_programa=5).exists() 

"""
u = User_Programa_Sector.objects.get(user=6)
print u.user.username
"""
 
 
"""
import base64
b64img = base64.b64encode(open("/tmp/map.png","rb").read())
print b64img
"""


"""
usr = User.objects.filter(groups__name='daniela')
for u in usr:
	print u.username
"""

"""
usr = User.objects.filter(Q(user_permissions__codename='can_operador') & Q(groups__name='')).values_list('id','username')

for u in usr:
	print u
"""














"""
usr = UserPermission.objects.all();

for u in usr:
	print u.user.email
"""

	


"""
usr = User.objects.all() 
  
for u in usr:
	if u.has_perm('ordenamiento.can_root2'):
		print u.username,
"""


"""
mm = Mapa_Aptitud.objects.filter(user_sector_programa=11)

for m in mm:
	print m.nombre
"""
"""
m = Mapa_Aptitud_Mapa_Valor(mapa_aptitud_id=3,mapa_valor_id=3)
m.save()
"""

"""
mp = Mapa_Aptitud()

mp.user_sector_programa_id=1
mp.nombre ="fun"
mp.estatus="no aprobado"

mp.save()
"""
"""
location = "Salsipuedes"
mapset = "sector33"

re =[0.0,0.0,0.0,0.33,0.18,0.0,0.1,0.7,0.4,0.6]

gsh.grass_init(location,mapset)
gsh.fun_discreta('USV_r',re,'re_usv')
"""





"""


from decimal import Decimal
from django.contrib.auth.models import User, Permission
from oe.models import *


 


location = "Salsipuedes"
mapset = "Demo"


gsh.grass(location)
print gsh.info('sector10')
gsh.close()
"""

"""
from ordenamiento.models import *


sector = Sector.objects.select_related("sector").filter(sector__user=3,sector__programa=13)
for p in sector:
	print p.nombre,p.id
"""
"""
lst=[]	
usr = User.objects.all()	
for u in usr:
	if u.has_perm("ordenamiento.can_admin") and not u.is_superuser:
		lst.append((u.id,u.username))


print lst

"""

"""
m = Permission.objects.get(codename="delete_rol")
user = User.objects.get(username="operador")
user.user_permissions.add(m)
user.save()
"""

"""
print datetime.now()

p = Programa(fecha_inicio="2012-2-7",fecha_fin="2012-2-7")
p.save()

"""

#user = User.objects.create_user(username='operador', email='operador@d.com', password='operador')

""""
id=62;
usr = User.objects.get(id)
print usr
#print usr.has_perm('oe.can_operador')
print usr.user_permissions.all()
"""

"""
usr = User.objects.get(id=2)
usr.user_permissions.clear()
"""






"""
us = User_Programa_Sector.objects.filter(programa=6,user=63)

print us

for s in us:
	print s.sector_id

"""




# -*- coding: utf-8 -*-
import os
os.environ['DJANGO_SETTINGS_MODULE']="settings"

from ordenamiento.models import Sector
from ordenamiento.models import Accion

sector=["Conservación","Energía","Agricultura","Acuacultura","Pesca"]

#for s in sector:
#	s = Sector(nombre=s)
#	s.save()

acciones = ["login","creacion usuario","creacion proceso","asignacion sector", "creacion actividad", "edicion actividad", "eliminacion actividad", "creacion atributo","creacion capa","creacion mapa funcion valor","creacion mapa aptitud","actualizacion datos","sector creado","usuario deshabilitado","usuario habilitado"]

for a in acciones:
	a = Accion(descripcion=a)
	a.save()







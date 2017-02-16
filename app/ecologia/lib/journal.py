from lib.D import ACCION as accion
from ordenamiento.models import Bitacora
from datetime import datetime
import ordenamiento.querys as q
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from lib.D import ACCION


def getUserFromRequest(request):
    sessionId = request.session.session_key
    session = Session.objects.get(session_key=sessionId)
    userId = session.get_decoded().get('_auth_user_id')    
    user = q.getUser(userId)
    return user

def registerAction(request, accionId, detalles):        
    user = getUserFromRequest(request)          
    accion = q.getAction(accionId)
    bitacora = Bitacora(accion=accion, fecha=datetime.now(), user=user, detalles=detalles)
    bitacora.save()     


def registerActionUserLogin(request, detalles):
    registerAction(request, ACCION.LOGIN, detalles)
    

def registerActionUserCreated(request, detalles):    
    registerAction(request, ACCION.CREATE_USER, detalles)
    
def registerActionUserDeleted(request, detalles):    
    registerAction(request, ACCION.UPDATE_USER, detalles)    
    
def registerActionProgramCreated(request, detalles):    
    registerAction(request, ACCION.CREATE_PROGRAM, detalles)
    
def registerActionSectorAssignated(request, detalles):    
    registerAction(request, ACCION.ASSIGN_SECTOR, detalles)

def registerActionSectorCreated(request, detalles):    
    registerAction(request, ACCION.CREATE_SECTOR, detalles)

def registerActionActivityCreated(request, detalles):    
    registerAction(request, ACCION.CREATE_ACTIVITY, detalles)

def registerActionActivityEdited(request, detalles):    
    registerAction(request, ACCION.EDIT_ACTIVITY, detalles)

def registerActionActivityDeleted(request, detalles):    
    registerAction(request, ACCION.DELETE_ACTIVITY, detalles)
    
def registerActionAttributeCreated(request, detalles):    
    registerAction(request, ACCION.CREATE_ATTRIBUTE, detalles)
    
def registerActionUserDisabled(request, detalles):    
    registerAction(request, ACCION.DISABLE_USER, detalles)
    
def registerActionUserEnabled(request, detalles):    
    registerAction(request, ACCION.ENABLE_USER, detalles)    

def registerActionLayerMapCreated(request, detalles):    
    registerAction(request, ACCION.CREATE_LAYER_MAP, detalles)

def registerActionValueFunctionMapCreated(request, detalles):    
    registerAction(request, ACCION.CREATE_VALUE_FUNCTION_MAP, detalles)

def registerActionAptitudeMapCreated(request, detalles):    
    registerAction(request, ACCION.CREATE_APTITUDE_MAP, detalles)


    
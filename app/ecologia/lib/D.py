"""
Define
"""
from U import enum

MENU = enum(PROGRAMA=0, EXPORTAR_IMPORTAR=1, MAPA=2, BITACORA=3, ROL=4, GRASS=5)

PERMISSION = enum(ROOT="can_root",ROOT2="can_root2",ADMIN="can_admin", OPERADOR="can_operador", OPERADOR_PRIVILEGIOS="can_operador_privilegios", SUPERVISOR="can_supervisor")
ROL = enum(ROOT="ordenamiento.can_root",ROOT2="ordenamiento.can_root2", ADMIN="ordenamiento.can_admin", OPERADOR="ordenamiento.can_operador", OPERADOR_PRIVILEGIOS="ordenamiento.can_operador_privilegios", SUPERVISOR="ordenamiento.can_supervisor")


FUNCION = enum(CRECIENTE_CX=0, DECRECIENTE_CX=1, DECRECIENTE_CV=2, CRECIENTE_CV=3, CAMPANA=4, CAMPANA_INV=5, DIFUSA=6)
CMD = enum( DESAGRUPAR=0,DISTANCIA=1,PENDIENTE=2,MASCARA=3,NULOS=4,ESTADISTICA=5)
CMD_ATTR = enum(GRADOS='degrees',PORCENTAJE='percent')

STATUS_APTITUD = enum(NO_APROBADO="no aprobado",APROBADO="aprobado")
ACCION = enum(LOGIN='1', CREATE_USER='2', CREATE_PROGRAM='3', ASSIGN_SECTOR='4', CREATE_ACTIVITY='5', EDIT_ACTIVITY='6', DELETE_ACTIVITY='7', CREATE_ATTRIBUTE='8', CREATE_LAYER_MAP='9', CREATE_VALUE_FUNCTION_MAP='10', CREATE_APTITUDE_MAP='11', UPDATE_USER='12', CREATE_SECTOR='13',DISABLE_USER='14',ENABLE_USER='15')
        
    
    
     
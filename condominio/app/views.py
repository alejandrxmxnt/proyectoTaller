from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface 
from .models import Departamento, Persona, Estacionamiento, Vehiculo, EmpresaMensajeria, Paquete
from . import appbuilder

class DepartamentoModelView(ModelView):
    datamodel = SQLAInterface(Departamento)
    label_columns = {
        "numero": "Numero",
        "torre": "Torre",
        "piso": "Piso",
        "capacidad_residentes": "Capacidad de Residentes",
        "estado": "Estado"
    }
    list_columns = ["numero", "torre", "piso", "capacidad_residentes", "estado"]
    show_columns = ["departamento", "numero", "torre", "piso", "capacidad_residentes", "estado"]

    add_columns = ["numero", "torre", "piso", "capacidad_residentes", "estado"]

    edit_columns = ["numero", "torre", "piso", "capacidad_residentes", "estado"]

class PersonaModelView(ModelView):
    datamodel = SQLAInterface(Persona)
    label_columns = {
        "nombre_completo": "Nombre Completo",
        "cedula": "Cédula",
        "celular": "Celular",
        "correo": "Correo",
        "tipo_persona": "Tipo de Persona", #propietario / arrendatario / familiar
        "departamento": "Departamento"
    }
    list_columns = ["nombre_completo", "cedula", "celular", "correo", "tipo_persona", "departamento"]
    
    show_columns = ["nombre_completo", "cedula", "celular", "correo", "tipo_persona", "departamento"]
    
    add_columns = ["nombre_completo", "cedula", "celular", "correo", "tipo_persona", "departamento"]

    edit_columns = add_columns

    search_columns = ["nombre_completo"]
    order_columns = ["nombre_completo"]

class EstacionamientoModelView(ModelView):
    datamodel = SQLAInterface(Estacionamiento)
    label_columns = {
        "numero": "Número",
        "ubicacion": "Ubicación",
        "departamento": "Departamento",
        "estado": "Estado"
    }
    list_columns = ["numero", "ubicacion", "departamento", "estado"]    
    show_columns = ["numero", "ubicacion", "departamento", "estado"]
    add_columns = ["numero", "ubicacion", "departamento", "estado"]
    edit_columns = ["numero", "ubicacion", "departamento", "estado"]
    search_columns = ["numero"]
    order_columns = ["numero"]

class VehiculoModelView(ModelView):
    datamodel = SQLAInterface(Vehiculo)
    label_columns = {
        "patente": "Patente",
        "marca": "Marca",
        "modelo": "Modelo",
        "color": "Color",
        "persona": "Propietario",
        "estacionamiento": "Estacionamiento"
    }
    list_columns = ["patente", "marca", "modelo", "color", "persona", "estacionamiento"]
    show_columns = ["patente", "marca", "modelo", "color", "persona", "estacionamiento"]
    add_columns = ["patente", "marca", "modelo", "color", "persona", "estacionamiento"]
    edit_columns = ["patente", "marca", "modelo", "color", "persona", "estacionamiento"]
    search_columns = ["patente"]
    order_columns = ["patente"]


class PaqueteModelView(ModelView):
    datamodel = SQLAInterface(Paquete)

    label_columns = {
        "empresa": "Empresa de Mensajería",
        "departamento": "Departamento",
        "destinatario": "Destinatario",
        "cantidad": "Cantidad",
        "fecha_recepcion": "Fecha de Recepción",
        "hora_recepcion": "Hora de Recepción",
        "estado": "Estado"
    }

    list_columns = [
        "empresa",
        "departamento",
        "destinatario",
        "cantidad",
        "fecha_recepcion",
        "estado"
    ]

    show_columns = [
        "empresa",
        "departamento",
        "destinatario",
        "cantidad",
        "fecha_recepcion",
        "hora_recepcion",
        "estado"
    ]

    add_columns = [
        "empresa",
        "departamento",
        "destinatario",
        "cantidad",
        "fecha_recepcion",
        "hora_recepcion",
        "estado"
    ]

    edit_columns = add_columns


class EmpresaMensajeriaModelView(ModelView):
    datamodel = SQLAInterface(EmpresaMensajeria)

    label_columns = {
        "nombre_empresa": "Nombre de la Empresa",
        "datos_empresa": "Datos de la Empresa",
        "telefono": "Teléfono",
        "correo": "Correo"
    }

    list_columns = [
        "nombre_empresa",
        "telefono",
        "correo"
    ]

    show_columns = [
        "nombre_empresa",
        "datos_empresa",
        "telefono",
        "correo"
    ]

    add_columns = [
        "nombre_empresa",
        "datos_empresa",
        "telefono",
        "correo"
    ]

    edit_columns = add_columns

    search_columns = ["nombre_empresa"]
    order_columns = ["nombre_empresa"]

#REGISTRO
appbuilder.add_view(
    DepartamentoModelView,
    "Modulo de Departamentos",
    icon="fa-building",
    category="Departamentos" 
)
appbuilder.add_view(
    PersonaModelView,
    "Modulo de Personas",
    icon="fa-users",
    category="Residentes"
)
appbuilder.add_view(
    EstacionamientoModelView,
    "Modulo de Estacionamientos",
    icon="fa-car",
    category="Estacionamientos"
)
appbuilder.add_view(
    VehiculoModelView,
    "Modulo de Vehiculos",
    icon="fa-car",
    category="Vehiculos"
)

appbuilder.add_view(
    EmpresaMensajeriaModelView,
    "Modulo de Empresas de Mensajería",
    icon="fa-truck",
    category="Paquetes"
)

appbuilder.add_view(
    PaqueteModelView,
    "Modulo de Paquetes",
    icon="fa-box",
    category="Paquetes"
)   


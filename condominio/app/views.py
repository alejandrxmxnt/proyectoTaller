from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface 
from .models import Departamento, Persona, Estacionamiento, Vehiculo, Paquete
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
    show_columns = ["id_departamento", "numero", "torre", "piso", "capacidad_residentes", "estado"]

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


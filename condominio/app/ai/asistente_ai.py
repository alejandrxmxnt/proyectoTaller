#
#import os
#import logging
#import unicodedata
#
#from datetime import date
#from flask import Blueprint, request, jsonify
#from openai import OpenAI
#
#from app.extensions import db
#from app.models import Paquete
#
#logger = logging.getLogger(__name__)
#
#asistente_bp = Blueprint(
#    "asistente_ai",
#    __name__,
#    url_prefix="/api"
#)
#
#def obtenerInformacion():
#
#    api_key = os.getenv("AI_API_KEY")
#    base_url = os.getenv("AI_URL")
#
#    if not api_key:
#        raise ValueError("No se encontró AI_API_KEY")
#
#    if not base_url:
#        raise ValueError("No se encontró AI_URL")
#
#    return OpenAI(
#        api_key=api_key,
#        base_url=base_url
#    )
#
## NORMALIZAR TEXTO
#
#def normalizar_texto(texto):
#
#    texto = texto.lower()
#
#    texto = unicodedata.normalize("NFD", texto)
#
#    texto = "".join(
#        caracter for caracter in texto
#        if unicodedata.category(caracter) != "Mn"
#    )
#
#    return texto
#
## CONSULTAR BASE DE DATOS
#
#def obtener_datos_condominio(pregunta):
#
#    pregunta = normalizar_texto(pregunta)
#
#    # Consultar paquetes pendientes
#    if any(palabra in pregunta for palabra in [
#        "pendiente", "sin retirar", "por retirar"
#    ]):
#
#        total = db.session.query(Paquete).filter(
#            Paquete.estado.is_(False)
#        ).count()
#
#        return (
#            f"Hay {total} paquetes pendientes de retiro."
#        )
#
#    # Consultar paquetes entregados
#    elif any(palabra in pregunta for palabra in [
#        "entregado", "retirado"
#    ]):
#
#        total = db.session.query(Paquete).filter(
#            Paquete.estado.is_(True)
#        ).count()
#
#        return (
#            f"Hay {total} paquetes entregados."
#        )
#
#    # Consultar paquetes recibidos hoy
#    elif any(palabra in pregunta for palabra in [
#        "hoy", "este dia"
#    ]):
#
#        total = db.session.query(Paquete).filter(
#            Paquete.fecha_recepcion == date.today()
#        ).count()
#
#        return (
#            f"Hoy se recibieron {total} paquetes."
#        )
#
#    # Consultar total de paquetes
#    elif "paquete" in pregunta:
#
#        total = db.session.query(Paquete).count()
#
#        return (
#            f"El sistema tiene registrados {total} paquetes en total."
#        )
#
#    return None
#
#
#
#@asistente_bp.route("/asistente", methods=["POST"])
#def consultar_asistente():
#
#    try:
#
#        data = request.get_json(silent=True) or {}
#
#        mensaje = data.get("mensaje", "").strip()
#        historial = data.get("history", [])
#
#        if not mensaje:
#
#            return jsonify({
#                "error": "Debe ingresar una pregunta."
#            }), 400
#
#        # Consultar información de la base de datos
#        informacion_bd = obtener_datos_condominio(mensaje)
#
#        if informacion_bd is None:
#            informacion_bd = (
#                "No se realizó ninguna consulta a la base de datos "
#                "para esta pregunta. No inventes cantidades ni "
#                "información administrativa."
#            )
#
#        # Instrucciones de la IA
#        mensajes = [
#            {
#                "role": "system",
#                "content": f"""
#                Eres un asistente inteligente especializado
#                en la administración de condominios.
#
#                Responde siempre en español, de forma clara,
#                cordial y sencilla.
#
#                INFORMACIÓN DE LA BASE DE DATOS:
#
#                {informacion_bd}
#
#                REGLAS:
#                - Utiliza los resultados proporcionados.
#                - No inventes cantidades ni estadísticas.
#                - No inventes información administrativa.
#                - Si no tienes información suficiente,
#                  indícalo claramente.
#                - No afirmes que consultaste datos si no lo hiciste.
#                """
#            }
#        ]
#
#        # Incorporar historial
#        if isinstance(historial, list):
#
#            for elemento in historial[-20:]:
#
#                if not isinstance(elemento, dict):
#                    continue
#
#                rol = elemento.get("role")
#                contenido = elemento.get("content")
#
#                if (
#                    rol in ("user", "assistant")
#                    and isinstance(contenido, str)
#                ):
#
#                    mensajes.append({
#                        "role": rol,
#                        "content": contenido[:4000]
#                    })
#
#        # Pregunta actual
#        mensajes.append({
#            "role": "user",
#            "content": mensaje
#        })
#
#        # Consultar API
#        cliente = obtenerInformacion()
#
#        respuesta = cliente.chat.completions.create(
#            model=os.getenv("AI_MODEL", "gpt-4o-mini"),
#            messages=mensajes,
#            temperature=0.3
#        )
#
#        texto_respuesta = respuesta.choices[0].message.content
#
#        if not texto_respuesta:
#            raise ValueError("La IA devolvió una respuesta vacía.")
#
#        return jsonify({
#            "respuesta": texto_respuesta
#        }), 200
#
#    except Exception:
#
#        logger.exception("Error al consultar el asistente IA")
#
#        return jsonify({
#            "error": "No fue posible obtener una respuesta del asistente."
#        }), 500






import os
import json
import logging
from datetime import date

from flask import Blueprint, request, jsonify
from openai import OpenAI
from sqlalchemy import func, cast, String

from app.extensions import db
from app.models import (
    Departamento, Persona, Estacionamiento,
    Vehiculo, EmpresaMensajeria, Paquete
)

logger = logging.getLogger(__name__)

asistente_bp = Blueprint("asistente_ai", __name__, url_prefix="/api")

MAX_FILAS = 20
MAX_RONDAS_TOOLS = 4


def obtenerInformacion():
    api_key = os.getenv("AI_API_KEY")
    base_url = os.getenv("AI_URL")
    if not api_key:
        raise ValueError("No se encontró AI_API_KEY")
    if not base_url:
        raise ValueError("No se encontró AI_URL")
    return OpenAI(api_key=api_key, base_url=base_url)


# ---------- utilidades ----------

def _txt(valor):
    """Convierte enums/booleanos/fechas a texto."""
    return str(getattr(valor, "value", valor))


def _filtro_estado(columna, estado):
    # Compara por texto, así funciona con ENUM o booleano
    return func.lower(cast(columna, String)) == str(estado).lower()


def _conteo_por_estado(modelo):
    filas = (
        db.session.query(modelo.estado, func.count())
        .group_by(modelo.estado).all()
    )
    return {_txt(e): n for e, n in filas}


# ---------- consultas (una por necesidad) ----------

def resumen_general():
    return {
        "departamentos": {
            "total": db.session.query(Departamento).count(),
            "por_estado": _conteo_por_estado(Departamento),
        },
        "personas": {
            "total": db.session.query(Persona).count(),
            "por_tipo": {
                _txt(t): n for t, n in db.session.query(
                    Persona.tipo_persona, func.count()
                ).group_by(Persona.tipo_persona).all()
            },
        },
        "estacionamientos": {
            "total": db.session.query(Estacionamiento).count(),
            "por_estado": _conteo_por_estado(Estacionamiento),
        },
        "vehiculos": {"total": db.session.query(Vehiculo).count()},
        "empresas_mensajeria": {
            "total": db.session.query(EmpresaMensajeria).count()
        },
        "paquetes": {
            "total": db.session.query(Paquete).count(),
            "por_estado": _conteo_por_estado(Paquete),
            "recibidos_hoy": db.session.query(Paquete).filter(
                Paquete.fecha_recepcion == date.today()
            ).count(),
        },
    }


def buscar_departamento(numero, torre=None):
    q = db.session.query(Departamento).filter(
        Departamento.numero == str(numero)
    )
    if torre:
        q = q.filter(Departamento.torre == str(torre))
    deptos = q.limit(5).all()

    if not deptos:
        existentes = [
            d.numero for d in
            db.session.query(Departamento).order_by(Departamento.numero).limit(30)
        ]
        return {
            "mensaje": f"No existe un departamento con número {numero}.",
            "numeros_existentes": existentes,
        }

    resultado = []
    for d in deptos:
        # Personas del departamento
        residentes = db.session.query(Persona).filter(
            Persona.id_departamento == d.id_departamento
        ).limit(MAX_FILAS).all()

        # Estacionamientos del departamento
        parkings = db.session.query(Estacionamiento).filter(
            Estacionamiento.id_departamento == d.id_departamento
        ).all()

        # Vehículos: de sus personas O ubicados en sus estacionamientos
        condiciones = []
        ids_personas = [p.id_persona for p in residentes]
        ids_parkings = [e.id_estacionamiento for e in parkings]
        if ids_personas:
            condiciones.append(Vehiculo.id_persona.in_(ids_personas))
        if ids_parkings:
            condiciones.append(Vehiculo.id_estacionamiento.in_(ids_parkings))

        vehiculos = []
        if condiciones:
            vehiculos = (
                db.session.query(Vehiculo, Persona, Estacionamiento)
                .outerjoin(Persona, Vehiculo.id_persona == Persona.id_persona)
                .outerjoin(Estacionamiento,
                           Vehiculo.id_estacionamiento == Estacionamiento.id_estacionamiento)
                .filter(or_(*condiciones))
                .limit(MAX_FILAS).all()
            )

        # Paquetes del departamento
        paquetes = (
            db.session.query(Paquete, EmpresaMensajeria, Persona)
            .join(EmpresaMensajeria,
                  Paquete.id_empresa == EmpresaMensajeria.id_empresa)
            .outerjoin(Persona, Paquete.id_destinatario == Persona.id_persona)
            .filter(Paquete.id_departamento == d.id_departamento)
            .order_by(Paquete.fecha_recepcion.desc())
            .limit(MAX_FILAS).all()
        )
        sin_entregar = db.session.query(Paquete).filter(
            Paquete.id_departamento == d.id_departamento,
            Paquete.fecha_entrega.is_(None)
        ).count()

        resultado.append({
            "departamento": d.numero, "torre": d.torre, "piso": d.piso,
            "capacidad_residentes": d.capacidad_residentes,
            "estado": _txt(d.estado),
            "personas": [
                {"nombre": p.nombre_completo, "tipo": _txt(p.tipo_persona)}
                for p in residentes
            ],
            "estacionamientos": [
                {"numero": e.numero, "ubicacion": e.ubicacion,
                 "estado": _txt(e.estado)} for e in parkings
            ],
            "vehiculos": [{
                "patente": v.patente, "marca": v.marca, "modelo": v.modelo,
                "color": v.color,
                "propietario": p.nombre_completo if p else None,
                "estacionamiento": e.numero if e else None,
            } for v, p, e in vehiculos],
            "paquetes_sin_entregar": sin_entregar,
            "ultimos_paquetes": [{
                "empresa": em.nombre_empresa,
                "destinatario": dest.nombre_completo if dest else None,
                "cantidad": pq.cantidad,
                "fecha_recepcion": pq.fecha_recepcion,
                "fecha_entrega": pq.fecha_entrega,
                "estado": _txt(pq.estado),
            } for pq, em, dest in paquetes],
        })
    return resultado

def buscar_persona(nombre):
    filas = (
        db.session.query(Persona, Departamento)
        .outerjoin(Departamento,
                   Persona.id_departamento == Departamento.id_departamento)
        .filter(Persona.nombre_completo.ilike(f"%{nombre}%"))
        .limit(MAX_FILAS).all()
    )
    resultado = []
    for p, d in filas:
        vehiculos = db.session.query(Vehiculo).filter(
            Vehiculo.id_persona == p.id_persona
        ).all()
        resultado.append({
            "nombre": p.nombre_completo,
            "tipo": _txt(p.tipo_persona),
            "departamento": f"{d.numero} (torre {d.torre})" if d else None,
            "vehiculos": [
                {"patente": v.patente, "marca": v.marca,
                 "modelo": v.modelo, "color": v.color} for v in vehiculos
            ],
        })
    return resultado or {"mensaje": "No se encontró a esa persona."}


def buscar_vehiculo(patente=None, marca=None):
    q = (
        db.session.query(Vehiculo, Persona, Estacionamiento)
        .outerjoin(Persona, Vehiculo.id_persona == Persona.id_persona)
        .outerjoin(Estacionamiento,
                   Vehiculo.id_estacionamiento == Estacionamiento.id_estacionamiento)
    )
    if patente:
        q = q.filter(Vehiculo.patente.ilike(f"%{patente}%"))
    if marca:
        q = q.filter(Vehiculo.marca.ilike(f"%{marca}%"))
    filas = q.limit(MAX_FILAS).all()
    resultado = [{
        "patente": v.patente, "marca": v.marca, "modelo": v.modelo,
        "color": v.color,
        "propietario": p.nombre_completo if p else None,
        "estacionamiento": e.numero if e else None,
    } for v, p, e in filas]
    return resultado or {"mensaje": "No se encontraron vehículos."}


def listar_estacionamientos(estado=None):
    q = db.session.query(Estacionamiento)
    if estado:
        q = q.filter(_filtro_estado(Estacionamiento.estado, estado))
    total = q.count()
    filas = q.limit(MAX_FILAS).all()
    return {
        "total": total,
        "estacionamientos": [
            {"numero": e.numero, "ubicacion": e.ubicacion,
             "estado": _txt(e.estado)} for e in filas
        ],
    }


def listar_paquetes(estado=None, fecha_recepcion=None,
                    departamento=None, empresa=None):
    q = (
        db.session.query(Paquete, Departamento, Persona, EmpresaMensajeria)
        .join(Departamento,
              Paquete.id_departamento == Departamento.id_departamento)
        .join(EmpresaMensajeria,
              Paquete.id_empresa == EmpresaMensajeria.id_empresa)
        .outerjoin(Persona, Paquete.id_destinatario == Persona.id_persona)
    )
    if estado:
        q = q.filter(_filtro_estado(Paquete.estado, estado))
    if fecha_recepcion:
        f = date.today() if fecha_recepcion == "hoy" \
            else date.fromisoformat(fecha_recepcion)
        q = q.filter(Paquete.fecha_recepcion == f)
    if departamento:
        q = q.filter(Departamento.numero == str(departamento))
    if empresa:
        q = q.filter(EmpresaMensajeria.nombre_empresa.ilike(f"%{empresa}%"))

    total = q.count()
    filas = q.order_by(Paquete.fecha_recepcion.desc()).limit(MAX_FILAS).all()
    return {
        "total_coincidencias": total,
        "paquetes": [{
            "id": pq.id_paquete,
            "empresa": em.nombre_empresa,
            "departamento": d.numero,
            "destinatario": p.nombre_completo if p else None,
            "cantidad": pq.cantidad,
            "fecha_recepcion": pq.fecha_recepcion,
            "hora_recepcion": pq.hora_recepcion,
            "fecha_entrega": pq.fecha_entrega,
            "estado": _txt(pq.estado),
        } for pq, d, p, em in filas],
    }


def resumen_empresas():
    filas = (
        db.session.query(EmpresaMensajeria.nombre_empresa, func.count(Paquete.id_paquete))
        .outerjoin(Paquete, Paquete.id_empresa == EmpresaMensajeria.id_empresa)
        .group_by(EmpresaMensajeria.nombre_empresa).all()
    )
    return [{"empresa": n, "paquetes": c} for n, c in filas]


# ---------- registro de herramientas ----------

FUNCIONES = {
    "resumen_general": resumen_general,
    "buscar_departamento": buscar_departamento,
    "buscar_persona": buscar_persona,
    "buscar_vehiculo": buscar_vehiculo,
    "listar_estacionamientos": listar_estacionamientos,
    "listar_paquetes": listar_paquetes,
    "resumen_empresas": resumen_empresas,
}

def _tool(nombre, descripcion, props=None, requeridos=None):
    return {"type": "function", "function": {
        "name": nombre, "description": descripcion,
        "parameters": {"type": "object",
                       "properties": props or {},
                       "required": requeridos or []},
    }}

S = {"type": "string"}

TOOLS = [
    _tool("resumen_general",
          "Totales y conteos por estado de departamentos, personas, "
          "estacionamientos, vehículos, empresas y paquetes."),
    _tool("buscar_departamento",
          "Datos de un departamento: residentes, estacionamientos y "
          "paquetes sin entregar.",
          {"numero": S, "torre": S}, ["numero"]),
    _tool("buscar_persona",
          "Busca personas por nombre; devuelve tipo, departamento y vehículos.",
          {"nombre": S}, ["nombre"]),
    _tool("buscar_vehiculo",
          "Busca vehículos por patente o marca.",
          {"patente": S, "marca": S}),
    _tool("listar_estacionamientos",
          "Lista estacionamientos, opcionalmente filtrados por estado.",
          {"estado": S}),
    _tool("listar_paquetes",
          "Lista paquetes filtrando por estado, fecha de recepción "
          "('hoy' o YYYY-MM-DD), número de departamento o empresa.",
          {"estado": S, "fecha_recepcion": S,
           "departamento": S, "empresa": S}),
    _tool("resumen_empresas",
          "Cantidad de paquetes por empresa de mensajería."),
]


def ejecutar_tool(nombre, argumentos):
    funcion = FUNCIONES.get(nombre)
    if not funcion:
        return {"error": "Herramienta desconocida."}
    try:
        return funcion(**argumentos)
    except Exception:
        logger.exception("Error en la herramienta %s", nombre)
        db.session.rollback()
        return {"error": "No se pudo consultar esa información."}


# ---------- endpoint ----------

@asistente_bp.route("/asistente", methods=["POST"])
def consultar_asistente():
    try:
        data = request.get_json(silent=True) or {}
        mensaje = data.get("mensaje", "").strip()
        historial = data.get("history", [])

        if not mensaje:
            return jsonify({"error": "Debe ingresar una pregunta."}), 400

        mensajes = [{
            "role": "system",
            "content": f"""
Eres un asistente especializado en la administración de un condominio.
Responde siempre en español, de forma clara, cordial y sencilla.
Hoy es {date.today().isoformat()}.

REGLAS:
- Para cualquier dato del condominio (departamentos, personas,
  estacionamientos, vehículos, empresas o paquetes) usa las herramientas.
- No inventes cantidades, nombres ni datos. Usa solo lo que devuelvan
  las herramientas.
- Si la herramienta no devuelve datos o la pregunta está fuera de lo
  que puedes consultar, indícalo claramente.
- Nunca reveles cédulas, celulares ni correos de personas.
- Si hay más resultados que los mostrados, dilo.
"""
        }]

        if isinstance(historial, list):
            for el in historial[-20:]:
                if not isinstance(el, dict):
                    continue
                rol, contenido = el.get("role"), el.get("content")
                if rol in ("user", "assistant") and isinstance(contenido, str):
                    mensajes.append({"role": rol, "content": contenido[:4000]})

        mensajes.append({"role": "user", "content": mensaje})

        cliente = obtenerInformacion()
        modelo = os.getenv("AI_MODEL", "gpt-4o-mini")

        texto_respuesta = None
        for _ in range(MAX_RONDAS_TOOLS):
            respuesta = cliente.chat.completions.create(
                model=modelo,
                messages=mensajes,
                tools=TOOLS,
                temperature=0.2,
            )
            msg = respuesta.choices[0].message

            if not msg.tool_calls:
                texto_respuesta = msg.content
                break

            mensajes.append(msg)  # la petición de herramientas
            for call in msg.tool_calls:
                try:
                    args = json.loads(call.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                resultado = ejecutar_tool(call.function.name, args)
                mensajes.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(resultado, default=str,
                                          ensure_ascii=False),
                })

        if not texto_respuesta:
            raise ValueError("La IA no devolvió una respuesta final.")

        return jsonify({"respuesta": texto_respuesta}), 200

    except Exception:
        logger.exception("Error al consultar el asistente IA")
        return jsonify({
            "error": "No fue posible obtener una respuesta del asistente."
        }), 500
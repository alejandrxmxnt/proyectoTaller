
#import os
#import logging
#import flask 
#from openai import OpenAI
#import Blueprint, request, jsonify
#logger = logging.getLogger(__name__)
#
#asistente_bp = Blueprint(
#    "asistente_ai", 
#    __name__,
#    url = "/api"
#)
#
##llamar a nuestra configuracion .env
#def obtenerInformacion ():
#    api_key = os.getenv("AI_API_KEY").strip()
#    base_url = os.getenv("AI_URL").strip()
#
#    cliente = OpenAI(api_key=api_key, base_url=base_url)
#    return cliente
#@asistente_bp.post("/asistente")
#
#def consultar_asistente():
#    data = request.get_json(Silent=True)
#    mensaje = data.get()("mensaje","")
#    mensaje = mensaje.strip()
#
#    mensaje = [
#        {
#            "role": "system", 
#            "content": "Eres un asistente de IA que ayuda a los residentes de un condominio a responder preguntas sobre la administración del condominio, reglas, servicios y cualquier otra consulta relacionada con la vida en el condominio. Proporciona respuestas claras y útiles."
#            }
#    ]




import os
import logging

from flask import Blueprint, request, jsonify
from openai import OpenAI

logger = logging.getLogger(__name__)

asistente_bp = Blueprint(
    "asistente_ai",
    __name__,
    url_prefix="/api"
)


# Crear cliente de inteligencia artificial
def obtenerInformacion():

    api_key = os.getenv("AI_API_KEY")
    base_url = os.getenv("AI_URL")

    if not api_key:
        raise ValueError("No se encontró AI_API_KEY en el archivo .env")

    if not base_url:
        raise ValueError("No se encontró AI_URL en el archivo .env")

    cliente = OpenAI(
        api_key=api_key,
        base_url=base_url
    )

    return cliente


# Endpoint para consultar al asistente
@asistente_bp.route("/asistente", methods=["POST"])
def consultar_asistente():

    try:
        data = request.get_json(silent=True) or {}

        mensaje = data.get("mensaje", "").strip()
        historial = data.get("history", [])

        if not mensaje:
            return jsonify({
                "error": "Debe ingresar una pregunta."
            }), 400

        # Instrucciones principales de la IA
        mensajes = [
            {
                "role": "system",
                "content": """
                Eres un asistente inteligente especializado en la
                administración de condominios.

                Ayudas a los residentes a resolver consultas sobre:

                - Administración del condominio.
                - Recepción y retiro de paquetes.
                - Normas de convivencia.
                - Uso de áreas comunes.
                - Servicios disponibles.
                - Consultas generales de los residentes.

                Responde siempre en español, de manera clara,
                cordial y sencilla.

                No inventes reglamentos, horarios, datos de
                residentes ni información administrativa.

                Si desconoces algún dato específico del condominio,
                indícalo y recomienda consultar con administración.
                """
            }
        ]

        # Incorporar el historial de conversación
        if isinstance(historial, list):

            for elemento in historial[-20:]:

                if not isinstance(elemento, dict):
                    continue

                rol = elemento.get("role")
                contenido = elemento.get("content")

                if rol in ("user", "assistant") and isinstance(contenido, str):
                    mensajes.append({
                        "role": rol,
                        "content": contenido[:4000]
                    })

        # Agregar pregunta actual
        mensajes.append({
            "role": "user",
            "content": mensaje
        })

        # Consultar API
        cliente = obtenerInformacion()

        respuesta = cliente.chat.completions.create(
            model=os.getenv("AI_MODEL", "gpt-4o-mini"),
            messages=mensajes,
            temperature=0.7
        )

        texto_respuesta = respuesta.choices[0].message.content

        return jsonify({
            "respuesta": texto_respuesta
        }), 200

    except Exception:
        logger.exception("Error al consultar el asistente IA")

        return jsonify({
            "error": "No fue posible obtener una respuesta del asistente."
        }), 500


import os
import logging
import unicodedata

from datetime import date
from flask import Blueprint, request, jsonify
from openai import OpenAI

from app.extensions import db
from app.models import Paquete

logger = logging.getLogger(__name__)

asistente_bp = Blueprint(
    "asistente_ai",
    __name__,
    url_prefix="/api"
)

def obtenerInformacion():

    api_key = os.getenv("AI_API_KEY")
    base_url = os.getenv("AI_URL")

    if not api_key:
        raise ValueError("No se encontró AI_API_KEY")

    if not base_url:
        raise ValueError("No se encontró AI_URL")

    return OpenAI(
        api_key=api_key,
        base_url=base_url
    )

# NORMALIZAR TEXTO

def normalizar_texto(texto):

    texto = texto.lower()

    texto = unicodedata.normalize("NFD", texto)

    texto = "".join(
        caracter for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )

    return texto

# CONSULTAR BASE DE DATOS

def obtener_datos_condominio(pregunta):

    pregunta = normalizar_texto(pregunta)

    # Consultar paquetes pendientes
    if any(palabra in pregunta for palabra in [
        "pendiente", "sin retirar", "por retirar"
    ]):

        total = db.session.query(Paquete).filter(
            Paquete.estado.is_(False)
        ).count()

        return (
            f"Hay {total} paquetes pendientes de retiro."
        )

    # Consultar paquetes entregados
    elif any(palabra in pregunta for palabra in [
        "entregado", "retirado"
    ]):

        total = db.session.query(Paquete).filter(
            Paquete.estado.is_(True)
        ).count()

        return (
            f"Hay {total} paquetes entregados."
        )

    # Consultar paquetes recibidos hoy
    elif any(palabra in pregunta for palabra in [
        "hoy", "este dia"
    ]):

        total = db.session.query(Paquete).filter(
            Paquete.fecha_recepcion == date.today()
        ).count()

        return (
            f"Hoy se recibieron {total} paquetes."
        )

    # Consultar total de paquetes
    elif "paquete" in pregunta:

        total = db.session.query(Paquete).count()

        return (
            f"El sistema tiene registrados {total} paquetes en total."
        )

    return None



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

        # Consultar información de la base de datos
        informacion_bd = obtener_datos_condominio(mensaje)

        if informacion_bd is None:
            informacion_bd = (
                "No se realizó ninguna consulta a la base de datos "
                "para esta pregunta. No inventes cantidades ni "
                "información administrativa."
            )

        # Instrucciones de la IA
        mensajes = [
            {
                "role": "system",
                "content": f"""
                Eres un asistente inteligente especializado
                en la administración de condominios.

                Responde siempre en español, de forma clara,
                cordial y sencilla.

                INFORMACIÓN DE LA BASE DE DATOS:

                {informacion_bd}

                REGLAS:
                - Utiliza los resultados proporcionados.
                - No inventes cantidades ni estadísticas.
                - No inventes información administrativa.
                - Si no tienes información suficiente,
                  indícalo claramente.
                - No afirmes que consultaste datos si no lo hiciste.
                """
            }
        ]

        # Incorporar historial
        if isinstance(historial, list):

            for elemento in historial[-20:]:

                if not isinstance(elemento, dict):
                    continue

                rol = elemento.get("role")
                contenido = elemento.get("content")

                if (
                    rol in ("user", "assistant")
                    and isinstance(contenido, str)
                ):

                    mensajes.append({
                        "role": rol,
                        "content": contenido[:4000]
                    })

        # Pregunta actual
        mensajes.append({
            "role": "user",
            "content": mensaje
        })

        # Consultar API
        cliente = obtenerInformacion()

        respuesta = cliente.chat.completions.create(
            model=os.getenv("AI_MODEL", "gpt-4o-mini"),
            messages=mensajes,
            temperature=0.3
        )

        texto_respuesta = respuesta.choices[0].message.content

        if not texto_respuesta:
            raise ValueError("La IA devolvió una respuesta vacía.")

        return jsonify({
            "respuesta": texto_respuesta
        }), 200

    except Exception:

        logger.exception("Error al consultar el asistente IA")

        return jsonify({
            "error": "No fue posible obtener una respuesta del asistente."
        }), 500

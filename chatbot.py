import streamlit as st
import json
import os

# --- BASE DE DATOS (Simulada con un archivo JSON) ---
DB_FILE = "pasteleria_db.json"

def cargar_db():
    if not os.path.exists(DB_FILE):
        db_inicial = {
            "conocimiento": {
                "hola": "¡Hola! Bienvenido a Pastelería Dulce Código, ¿En qué puedo ayudarte?",
                "como estas?": "¡Horneando con mucha energía! ¿Y tú?",
                "de que te gustaria hablar?": "Me encanta hablar de pasteles, recetas, o puedo tomar tu pedido."
            },
            "pedidos": {}
        }
        with open(DB_FILE, 'w') as f:
            json.dump(db_inicial, f, indent=4)
            
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def guardar_db(db):
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=4)

# --- CONFIGURACIÓN DE LA INTERFAZ WEB ---
st.set_page_config(page_title="Pastelería Bot", page_icon="🍰")
st.title("🍰 Chatbot: Pastelería Dulce Código")
st.write("Haz tu pedido, consúltalo, cancélalo, o pregúntame algo nuevo para aprender.")

# --- MANEJO DEL ESTADO DE LA CONVERSACIÓN ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = [{"role": "assistant", "content": "¡Hola! Bienvenido a Pastelería Dulce Código, ¿En qué puedo ayudarte?"}]
if "estado" not in st.session_state:
    # Agregamos el nuevo estado: CANCELANDO_NOMBRE
    st.session_state.estado = "NORMAL" 
if "temp_data" not in st.session_state:
    st.session_state.temp_data = "" 

db = cargar_db()

# --- MOSTRAR EL HISTORIAL DEL CHAT ---
for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- LÓGICA PRINCIPAL DEL CHAT ---
user_input = st.chat_input("Escribe tu mensaje aquí...")

if user_input:
    # 1. Mostrar lo que el usuario escribió
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.mensajes.append({"role": "user", "content": user_input})
    
    texto_limpio = user_input.lower().strip()
    respuesta = ""

    # --- MÁQUINA DE ESTADOS DEL BOT ---
    
    if st.session_state.estado == "APRENDIENDO":
        pregunta_nueva = st.session_state.temp_data
        db["conocimiento"][pregunta_nueva] = user_input
        guardar_db(db)
        respuesta = f"¡Excelente! He aprendido algo nuevo. Cuando me pregunten '{pregunta_nueva}', responderé: '{user_input}'."
        st.session_state.estado = "NORMAL"
        
    elif st.session_state.estado == "PIDIENDO_ITEM":
        st.session_state.temp_data = user_input 
        respuesta = f"Listo, agendé: {user_input}. ¿A nombre de quién estaría el pedido?"
        st.session_state.estado = "PIDIENDO_NOMBRE"

    elif st.session_state.estado == "PIDIENDO_NOMBRE":
        nombre_cliente = texto_limpio
        pastel = st.session_state.temp_data
        db["pedidos"][nombre_cliente] = pastel 
        guardar_db(db)
        respuesta = f"¡Perfecto! Registré a {user_input} con {pastel}."
        st.session_state.estado = "NORMAL"

    elif st.session_state.estado == "CONSULTANDO_NOMBRE":
        nombre_cliente = texto_limpio
        if nombre_cliente in db["pedidos"]:
            respuesta = f"¡Aquí está! El pedido a nombre de {user_input} es: {db['pedidos'][nombre_cliente]}."
        else:
            respuesta = f"Lo siento, no encontré ningún pedido a nombre de {user_input}."
        st.session_state.estado = "NORMAL"

    # NUEVO ESTADO: ELIMINANDO UN PEDIDO
    elif st.session_state.estado == "CANCELANDO_NOMBRE":
        nombre_cliente = texto_limpio
        if nombre_cliente in db["pedidos"]:
            # La función .pop() elimina el registro del diccionario y nos devuelve qué pastel era
            pastel_cancelado = db["pedidos"].pop(nombre_cliente)
            guardar_db(db) # Guardamos los cambios en el archivo JSON
            respuesta = f"Listo. El pedido de '{pastel_cancelado}' a nombre de {user_input} ha sido cancelado y eliminado con éxito."
        else:
            respuesta = f"Lo siento, no encontré ningún pedido a nombre de {user_input} para cancelar."
        st.session_state.estado = "NORMAL"

    # ESTADO 0: CONVERSACIÓN NORMAL
    else:
        if texto_limpio == "quiero hacer un pedido":
            respuesta = "¡Perfecto! ¿Qué te gustaría pedir?"
            st.session_state.estado = "PIDIENDO_ITEM"
            
        elif texto_limpio == "consultar pedido":
            respuesta = "Claro, por favor dime el nombre a quien se registró el pedido:"
            st.session_state.estado = "CONSULTANDO_NOMBRE"

        # NUEVO DISPARADOR: CANCELAR PEDIDO
        elif texto_limpio == "cancelar pedido" or texto_limpio == "eliminar pedido":
            respuesta = "Entendido. Para cancelar tu orden, por favor dime el nombre a quien se registró:"
            st.session_state.estado = "CANCELANDO_NOMBRE"
            
        elif texto_limpio in db["conocimiento"]:
            respuesta = db["conocimiento"][texto_limpio]
            
        else:
            respuesta = f"Mmm... No tengo una respuesta registrada para '{user_input}'. ¿Qué te gustaría que te responda cuando me digan esto?"
            st.session_state.temp_data = texto_limpio
            st.session_state.estado = "APRENDIENDO"

    # 2. Mostrar la respuesta del bot
    with st.chat_message("assistant"):
        st.markdown(respuesta)
    st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
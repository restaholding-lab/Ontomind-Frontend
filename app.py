"""
app.py — Interfaz de usuario ONTOMIND
Chat ontológico con diseño cuidado para Streamlit.
"""
import streamlit as st
import httpx
import uuid
import os
from datetime import datetime

API_URL = os.getenv("ONTOMIND_API_URL", "https://ontomind-production.up.railway.app")

# ─── Configuración de página ──────────────────────────────
st.set_page_config(
    page_title      = "ONTOMIND",
    page_icon       = "◈",
    layout          = "centered",
    initial_sidebar_state = "collapsed"
)

# ─── CSS personalizado ────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300&family=DM+Mono:wght@300;400&display=swap');

:root {
    --bg:        #0e0e10;
    --surface:   #16161a;
    --border:    #2a2a32;
    --accent:    #c8a97e;
    --accent2:   #7e9cc8;
    --text:      #e8e4dc;
    --text-dim:  #7a7570;
    --user-bg:   #1a1a20;
    --agent-bg:  #131318;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Cormorant Garamond', Georgia, serif !important;
}

[data-testid="stHeader"] { display: none; }
[data-testid="stSidebar"] { background: var(--surface) !important; }
.stTextInput > div > div > input { display: none; }

/* Título */
.ontomind-header {
    text-align: center;
    padding: 2.5rem 0 1rem 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
}
.ontomind-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.8rem;
    font-weight: 300;
    letter-spacing: 0.35em;
    color: var(--accent);
    margin: 0;
}
.ontomind-subtitle {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    color: var(--text-dim);
    margin-top: 0.4rem;
    text-transform: uppercase;
}

/* Mensajes */
.msg-container {
    margin: 1.2rem 0;
    animation: fadeIn 0.4s ease;
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; } }

.msg-user {
    background: var(--user-bg);
    border-left: 2px solid var(--accent2);
    padding: 1rem 1.4rem;
    border-radius: 0 8px 8px 0;
    font-size: 1.05rem;
    line-height: 1.7;
    color: var(--text);
}
.msg-agent {
    background: var(--agent-bg);
    border-left: 2px solid var(--accent);
    padding: 1.2rem 1.6rem;
    border-radius: 0 8px 8px 0;
    font-size: 1.1rem;
    line-height: 1.85;
    color: var(--text);
    font-style: italic;
}
.msg-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-dim);
    margin-bottom: 0.5rem;
}
.msg-label-agent { color: var(--accent); }

/* Protocolo badge */
.protocolo-badge {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 0.55rem;
    letter-spacing: 0.12em;
    padding: 2px 8px;
    border-radius: 20px;
    margin-left: 0.5rem;
    text-transform: uppercase;
    vertical-align: middle;
}
.p-normal    { background: #1a2a1a; color: #6a9a6a; border: 1px solid #2a4a2a; }
.p-silencio  { background: #1a1a2a; color: #6a6a9a; border: 1px solid #2a2a4a; }
.p-incoherencia { background: #2a1a1a; color: #9a6a4a; border: 1px solid #4a2a1a; }
.p-vigil     { background: #2a1a1a; color: #c85a5a; border: 1px solid #5a1a1a; }

/* Input area */
.input-area {
    position: fixed;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 100%;
    max-width: 720px;
    background: linear-gradient(transparent, var(--bg) 30%);
    padding: 1.5rem 1rem 1.5rem 1rem;
    z-index: 100;
}
.stTextArea textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1rem !important;
    resize: none !important;
}
.stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 1px var(--accent) !important;
}
.stButton button {
    background: transparent !important;
    border: 1px solid var(--accent) !important;
    color: var(--accent) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    padding: 0.5rem 1.5rem !important;
    border-radius: 4px !important;
    transition: all 0.2s !important;
}
.stButton button:hover {
    background: var(--accent) !important;
    color: var(--bg) !important;
}

/* Spinner */
.stSpinner { color: var(--accent) !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

/* Separador */
.session-info {
    font-family: 'DM Mono', monospace;
    font-size: 0.55rem;
    color: var(--text-dim);
    text-align: center;
    letter-spacing: 0.1em;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)


# ─── Estado de sesión ─────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []
if "turno" not in st.session_state:
    st.session_state.turno = 0


def nueva_sesion():
    try:
        r = httpx.post(f"{API_URL}/sesion/nueva", timeout=10)
        return r.json().get("session_id")
    except Exception:
        return str(uuid.uuid4())


def enviar_mensaje(session_id: str, mensaje: str) -> dict:
    try:
        r = httpx.post(
            f"{API_URL}/chat",
            json={"session_id": session_id, "mensaje": mensaje},
            timeout=120
        )
        if r.status_code == 200:
            return r.json()
        return {"respuesta": "Error de conexión. Intenta de nuevo.", "protocolo": "error"}
    except Exception as e:
        return {"respuesta": f"Error: {str(e)}", "protocolo": "error"}


def badge_protocolo(protocolo: str) -> str:
    clases = {
        "normal":      "p-normal",
        "silencio":    "p-silencio",
        "incoherencia":"p-incoherencia",
        "vigil":       "p-vigil",
    }
    cls = clases.get(protocolo, "p-normal")
    return f'<span class="protocolo-badge {cls}">{protocolo}</span>'


# ─── Inicializar sesión ───────────────────────────────────
if not st.session_state.session_id:
    st.session_state.session_id = nueva_sesion()

# ─── Header ───────────────────────────────────────────────
st.markdown("""
<div class="ontomind-header">
    <h1 class="ontomind-title">ONTOMIND</h1>
    <p class="ontomind-subtitle">Coaching Ontológico · Echeverría · Pinotti</p>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="session-info">
    sesión {st.session_state.session_id[:8]}... · turno {st.session_state.turno}
</div>
""", unsafe_allow_html=True)

# ─── Historial de mensajes ────────────────────────────────
chat_container = st.container()
with chat_container:
    if not st.session_state.mensajes:
        st.markdown("""
        <div style="text-align:center; padding: 3rem 2rem; color: #3a3a42;">
            <div style="font-size: 2rem; margin-bottom: 1rem;">◈</div>
            <div style="font-family: 'Cormorant Garamond', serif; font-size: 1.2rem; font-style: italic;">
                ¿Qué está ocurriendo en tu vida que te trae aquí hoy?
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.mensajes:
            if msg["rol"] == "user":
                st.markdown(f"""
                <div class="msg-container">
                    <div class="msg-label">Tú</div>
                    <div class="msg-user">{msg["contenido"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                protocolo = msg.get("protocolo", "normal")
                badge = badge_protocolo(protocolo)
                st.markdown(f"""
                <div class="msg-container">
                    <div class="msg-label msg-label-agent">ONTOMIND {badge}</div>
                    <div class="msg-agent">{msg["contenido"]}</div>
                </div>
                """, unsafe_allow_html=True)

# Espaciado para el input fijo
st.markdown("<div style='height: 140px'></div>", unsafe_allow_html=True)

# ─── Input de mensaje ─────────────────────────────────────
with st.container():
    col1, col2 = st.columns([5, 1])
    with col1:
        mensaje = st.text_area(
            label     = "mensaje",
            label_visibility = "collapsed",
            placeholder = "Escribe lo que quieras compartir...",
            height    = 80,
            key       = "input_msg"
        )
    with col2:
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        enviar = st.button("Enviar", use_container_width=True)
        if st.button("Nueva\nsesión", use_container_width=True):
            st.session_state.session_id = nueva_sesion()
            st.session_state.mensajes   = []
            st.session_state.turno      = 0
            st.rerun()

# ─── Procesar envío ───────────────────────────────────────
if enviar and mensaje and mensaje.strip():
    st.session_state.mensajes.append({
        "rol":       "user",
        "contenido": mensaje.strip()
    })

    with st.spinner(""):
        resultado = enviar_mensaje(
            st.session_state.session_id,
            mensaje.strip()
        )

    st.session_state.mensajes.append({
        "rol":       "agent",
        "contenido": resultado.get("respuesta", ""),
        "protocolo": resultado.get("protocolo", "normal")
    })
    st.session_state.turno = resultado.get("turno", st.session_state.turno + 1)
    st.rerun()

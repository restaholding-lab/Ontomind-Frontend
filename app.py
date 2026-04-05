"""
app.py — Interfaz de usuario ONTOMIND v2
Correcciones: legibilidad, botones, limpieza input, UX.
"""
import streamlit as st
import httpx
import uuid
import os

API_URL = os.getenv("ONTOMIND_API_URL", "https://ontomind-production.up.railway.app")

st.set_page_config(
    page_title="ONTOMIND",
    page_icon="◈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500&family=DM+Mono:wght@300;400&display=swap');

:root {
    --bg:       #0e0e10;
    --surface:  #16161a;
    --border:   #2a2a32;
    --accent:   #c8a97e;
    --accent2:  #7e9cc8;
    --text:     #e8e4dc;
    --text-dim: #7a7570;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
[data-testid="stHeader"] { display: none; }
[data-testid="stSidebar"] { background: var(--surface) !important; }

.ontomind-header {
    text-align: center;
    padding: 2rem 0 1rem 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.5rem;
}
.ontomind-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.8rem;
    font-weight: 400;
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
.session-info {
    font-family: 'DM Mono', monospace;
    font-size: 0.55rem;
    color: var(--text-dim);
    text-align: center;
    letter-spacing: 0.1em;
    margin-bottom: 1rem;
}

/* MENSAJES */
.msg-container { margin: 1rem 0; animation: fadeIn 0.35s ease; }
@keyframes fadeIn { from { opacity:0; transform:translateY(5px); } to { opacity:1; } }

.msg-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-dim);
    margin-bottom: 0.4rem;
}
.msg-label-agent { color: var(--accent); }

.msg-user {
    background: #1a1a20;
    border-left: 2px solid var(--accent2);
    padding: 0.9rem 1.3rem;
    border-radius: 0 6px 6px 0;
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.15rem;
    font-weight: 400;
    line-height: 1.65;
    color: var(--text);
    font-style: normal;
}
/* Respuesta: NO cursiva, mayor tamaño, mejor contraste */
.msg-agent {
    background: #131318;
    border-left: 2px solid var(--accent);
    padding: 1.1rem 1.5rem;
    border-radius: 0 6px 6px 0;
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.25rem;
    font-weight: 400;
    line-height: 1.9;
    color: #f0ece4;
    font-style: normal;
    letter-spacing: 0.01em;
}

.protocolo-badge {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 0.55rem;
    letter-spacing: 0.1em;
    padding: 2px 7px;
    border-radius: 20px;
    margin-left: 0.4rem;
    text-transform: uppercase;
}
.p-normal     { background:#1a2a1a; color:#6a9a6a; border:1px solid #2a4a2a; }
.p-silencio   { background:#1a1a2a; color:#6a6a9a; border:1px solid #2a2a4a; }
.p-incoherencia { background:#2a1a1a; color:#9a6a4a; border:1px solid #4a2a1a; }
.p-vigil      { background:#2a1a1a; color:#c85a5a; border:1px solid #5a1a1a; }

/* INPUT AREA */
.stTextArea textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1.05rem !important;
    resize: none !important;
}
.stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 1px var(--accent) !important;
}

/* BOTONES — una línea, sin corte */
.stButton button {
    background: transparent !important;
    border: 1px solid var(--accent) !important;
    color: var(--accent) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    padding: 0.55rem 0.8rem !important;
    border-radius: 4px !important;
    white-space: nowrap !important;
    width: 100% !important;
    line-height: 1.2 !important;
}
.stButton button:hover {
    background: var(--accent) !important;
    color: var(--bg) !important;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)


# ─── Estado ───────────────────────────────────────────────
if "session_id"  not in st.session_state: st.session_state.session_id  = None
if "mensajes"    not in st.session_state: st.session_state.mensajes    = []
if "turno"       not in st.session_state: st.session_state.turno       = 0
if "input_key"   not in st.session_state: st.session_state.input_key   = 0


def nueva_sesion():
    try:
        r = httpx.post(f"{API_URL}/sesion/nueva", timeout=10)
        return r.json().get("session_id")
    except Exception:
        return str(uuid.uuid4())


def enviar_mensaje(session_id, mensaje):
    try:
        r = httpx.post(f"{API_URL}/chat",
            json={"session_id": session_id, "mensaje": mensaje},
            timeout=120)
        if r.status_code == 200:
            return r.json()
        return {"respuesta": "Error de conexión. Intenta de nuevo.", "protocolo": "error"}
    except Exception as e:
        return {"respuesta": f"Error: {str(e)}", "protocolo": "error"}


def badge(protocolo):
    cls = {"normal":"p-normal","silencio":"p-silencio",
           "incoherencia":"p-incoherencia","vigil":"p-vigil"}.get(protocolo,"p-normal")
    return f'<span class="protocolo-badge {cls}">{protocolo}</span>'


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

# ─── Historial ────────────────────────────────────────────
if not st.session_state.mensajes:
    st.markdown("""
    <div style="text-align:center; padding:3rem 2rem; color:#3a3a42;">
        <div style="font-size:2rem; margin-bottom:1rem;">◈</div>
        <div style="font-family:'Cormorant Garamond',serif; font-size:1.25rem; color:#6a6560;">
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
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msg-container">
                <div class="msg-label msg-label-agent">ONTOMIND {badge(msg.get("protocolo","normal"))}</div>
                <div class="msg-agent">{msg["contenido"]}</div>
            </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:160px'></div>", unsafe_allow_html=True)

# ─── Input ────────────────────────────────────────────────
col1, col2 = st.columns([5, 1])

with col1:
    # La key cambia al enviar → Streamlit recrea el widget vacío
    mensaje = st.text_area(
        label="mensaje",
        label_visibility="collapsed",
        placeholder="Escribe lo que quieras compartir...",
        height=90,
        key=f"input_{st.session_state.input_key}"
    )

with col2:
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    enviar = st.button("Enviar", use_container_width=True)
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    with st.expander("?", expanded=False):
        st.markdown("""
        <div style="font-family:'DM Mono',monospace; font-size:0.6rem; color:#7a7570; line-height:1.6;">
        <b>Nueva Sesión</b> borra el historial y crea una conversación desde cero.<br><br>
        Úsalo cuando quieras explorar un tema diferente o empezar sin contexto previo.<br><br>
        La conversación actual <b>no se pierde</b> en el sistema — solo en esta pantalla.
        </div>
        """, unsafe_allow_html=True)

    if st.button("Nueva sesión", use_container_width=True):
        st.session_state.session_id = nueva_sesion()
        st.session_state.mensajes   = []
        st.session_state.turno      = 0
        st.session_state.input_key += 1
        st.rerun()

# ─── Procesar envío ───────────────────────────────────────
if enviar and mensaje and mensaje.strip():
    texto = mensaje.strip()
    st.session_state.mensajes.append({"rol": "user", "contenido": texto})

    with st.spinner(""):
        resultado = enviar_mensaje(st.session_state.session_id, texto)

    st.session_state.mensajes.append({
        "rol":       "agent",
        "contenido": resultado.get("respuesta", ""),
        "protocolo": resultado.get("protocolo", "normal")
    })
    st.session_state.turno    = resultado.get("turno", st.session_state.turno + 1)
    st.session_state.input_key += 1  # limpia el campo de texto
    st.rerun()

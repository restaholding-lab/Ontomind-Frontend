"""
app.py — ONTOMIND v4 — Chat de coaching
Frontend público para usuarios. Dashboard en /pages/ con URL separada.
"""
import streamlit as st
import httpx
import html as _html
import uuid
import os
import time

API_URL = os.getenv("ONTOMIND_API_URL", "https://ontomind-production.up.railway.app")

st.set_page_config(
    page_title="ONTOMIND",
    page_icon="◈",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CSS — Diseño responsive, legible, alto contraste
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Source+Sans+3:wght@300;400;500;600&display=swap');

:root {
    --bg: #1a1a2e;
    --surface: #222240;
    --surface2: #1e1e36;
    --border: #3a3a5c;
    --accent: #d4a855;
    --accent-soft: #e8c97d;
    --accent2: #8eaadc;
    --text: #eeeef2;
    --text-soft: #c0c0d0;
    --dim: #8888a0;
}

/* === GLOBAL === */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
}

/* Ocultar header y sidebar de Streamlit para usuarios finales */
[data-testid="stHeader"] { display: none; }
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stSidebarNav"] { display: none !important; }
button[kind="headerNoPadding"] { display: none !important; }
.css-1rs6os { display: none !important; }
.css-17lntkn { display: none !important; }

/* === HEADER === */
.om-header {
    text-align: center;
    padding: 2rem 1rem 1.2rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.5rem;
}
.om-title {
    font-family: 'Libre Baskerville', Georgia, serif;
    font-size: clamp(1.8rem, 6vw, 2.6rem);
    font-weight: 700;
    letter-spacing: 0.2em;
    color: var(--accent);
    margin: 0;
    white-space: nowrap;
}
.om-subtitle {
    font-family: 'Source Sans 3', sans-serif;
    font-size: clamp(0.7rem, 2.5vw, 0.85rem);
    font-weight: 300;
    letter-spacing: 0.25em;
    color: var(--dim);
    margin-top: 0.5rem;
    text-transform: uppercase;
}
.om-session {
    font-family: 'Source Sans 3', sans-serif;
    font-size: 0.7rem;
    color: var(--dim);
    text-align: center;
    letter-spacing: 0.08em;
    margin-bottom: 1rem;
    opacity: 0.6;
}

/* === MENSAJES === */
.om-chat {
    max-width: 720px;
    margin: 0 auto;
    padding: 0 0.5rem;
}
.om-msg {
    margin: 1.2rem 0;
    animation: fadeIn 0.3s ease;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
}
.om-label {
    font-family: 'Source Sans 3', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--dim);
    margin-bottom: 0.4rem;
}
.om-label-coach {
    color: var(--accent);
}

/* Mensaje del usuario */
.om-user {
    background: var(--surface);
    border-left: 3px solid var(--accent2);
    padding: 1rem 1.2rem;
    border-radius: 0 8px 8px 0;
    font-family: 'Source Sans 3', sans-serif;
    font-size: clamp(1rem, 3.5vw, 1.1rem);
    line-height: 1.7;
    color: var(--text);
}

/* Mensaje del coach */
.om-coach {
    background: var(--surface2);
    border-left: 3px solid var(--accent);
    padding: 1.2rem 1.4rem;
    border-radius: 0 8px 8px 0;
    font-family: 'Libre Baskerville', Georgia, serif;
    font-size: clamp(1.05rem, 3.5vw, 1.15rem);
    line-height: 1.9;
    color: var(--text);
    font-style: italic;
}

/* Badge del protocolo */
.om-badge {
    display: inline-block;
    font-family: 'Source Sans 3', sans-serif;
    font-size: 0.6rem;
    font-weight: 500;
    padding: 2px 8px;
    border-radius: 12px;
    margin-left: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.om-b-normal { background: #1e3a1e; color: #7abf7a; border: 1px solid #2e5a2e; }
.om-b-silencio { background: #1e1e3a; color: #7a7abf; border: 1px solid #2e2e5a; }
.om-b-incoherencia { background: #3a2a1a; color: #bf9a5a; border: 1px solid #5a3a1a; }
.om-b-vigil { background: #3a1a1a; color: #d06060; border: 1px solid #6a2a2a; }

/* === BIENVENIDA === */
.om-welcome {
    text-align: center;
    padding: 4rem 2rem;
}
.om-welcome-icon {
    font-size: 2.5rem;
    color: var(--border);
    margin-bottom: 1rem;
}
.om-welcome-text {
    font-family: 'Libre Baskerville', Georgia, serif;
    font-size: clamp(1.1rem, 4vw, 1.35rem);
    color: var(--text-soft);
    line-height: 1.8;
}

/* === INPUT === */
.stTextArea textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: clamp(0.95rem, 3.5vw, 1.05rem) !important;
    line-height: 1.6 !important;
    resize: none !important;
    padding: 0.8rem 1rem !important;
}
.stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 1px var(--accent) !important;
}
.stTextArea textarea::placeholder {
    color: #5a5a70 !important;
    font-style: italic !important;
}

/* === BOTÓN ENVIAR === */
div[data-testid="stButton"] button {
    background: var(--accent) !important;
    border: none !important;
    color: #1a1a2e !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    padding: 0.6rem 1rem !important;
    border-radius: 8px !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stButton"] button:hover {
    background: var(--accent-soft) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(212, 168, 85, 0.3) !important;
}

/* === SPACER === */
.om-spacer { height: 140px; }

/* === RESPONSIVE MOBILE === */
@media (max-width: 768px) {
    .om-header { padding: 1.5rem 0.5rem 1rem; }
    .om-user, .om-coach { padding: 0.9rem 1rem; }
    .om-chat { padding: 0 0.2rem; }
    .om-spacer { height: 120px; }
    div[data-testid="stButton"] button {
        padding: 0.7rem 0.5rem !important;
        font-size: 0.8rem !important;
    }
}

@media (max-width: 400px) {
    .om-title { letter-spacing: 0.12em; }
    .om-user, .om-coach { font-size: 1rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Estado de sesión
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
for k, v in [("session_id", None), ("mensajes", []), ("turno", 0),
             ("input_key", 0), ("user_code", "")]:
    if k not in st.session_state:
        st.session_state[k] = v


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Funciones de backend
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def nueva_sesion():
    try:
        r = httpx.post(f"{API_URL}/sesion/nueva", timeout=10)
        return r.json().get("session_id")
    except:
        return str(uuid.uuid4())


def chat(session_id, msg, user_code="anonimo"):
    """Flujo asíncrono: POST /chat → polling /chat/status/{job_id}"""
    try:
        r = httpx.post(
            f"{API_URL}/chat",
            json={"session_id": session_id, "mensaje": msg,
                  "user_code": user_code or "anonimo"},
            timeout=15,
        )
        data = r.json()
        job_id = data.get("job_id")
        if not job_id:
            return data

        for _ in range(90):
            time.sleep(2)
            sr = httpx.get(f"{API_URL}/chat/status/{job_id}", timeout=10)
            sd = sr.json()
            status = sd.get("status", "")
            if status == "COMPLETED":
                return sd.get("result", {"respuesta": "", "protocolo": "error"})
            elif status == "FAILED":
                return {"respuesta": f"Error: {sd.get('error','')}", "protocolo": "error"}

        return {"respuesta": "Tiempo de espera agotado. Intenta de nuevo.", "protocolo": "error"}
    except Exception as e:
        return {"respuesta": f"Error de conexión: {e}", "protocolo": "error"}


def badge(protocolo):
    css_map = {
        "normal": "om-b-normal",
        "silencio": "om-b-silencio",
        "incoherencia": "om-b-incoherencia",
        "vigil": "om-b-vigil",
    }
    return f'<span class="om-badge {css_map.get(protocolo, "om-b-normal")}">{protocolo}</span>'


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Inicializar sesión
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if not st.session_state.session_id:
    st.session_state.session_id = nueva_sesion()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Header
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown(
    '<div class="om-header">'
    '<h1 class="om-title">ONTOMIND</h1>'
    '<p class="om-subtitle">Crecimiento personal</p>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    f'<div class="om-session">sesión {st.session_state.session_id[:8]} · turno {st.session_state.turno}</div>',
    unsafe_allow_html=True,
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Chat — renderizado en un único bloque HTML
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if not st.session_state.mensajes:
    st.markdown(
        '<div class="om-welcome">'
        '<div class="om-welcome-icon">◈</div>'
        '<div class="om-welcome-text">'
        '¿Qué está ocurriendo en tu vida<br>que te trae aquí hoy?'
        '</div></div>',
        unsafe_allow_html=True,
    )
else:
    msgs_html = []
    for msg in st.session_state.mensajes:
        if msg["rol"] == "user":
            contenido = _html.escape(msg["contenido"])
            msgs_html.append(
                f'<div class="om-msg">'
                f'<div class="om-label">Tú</div>'
                f'<div class="om-user">{contenido}</div>'
                f'</div>'
            )
        else:
            contenido = msg["contenido"]
            proto = msg.get("protocolo", "normal")
            msgs_html.append(
                f'<div class="om-msg">'
                f'<div class="om-label om-label-coach">ONTOMIND {badge(proto)}</div>'
                f'<div class="om-coach">{contenido}</div>'
                f'</div>'
            )
    st.markdown(
        '<div id="om-chat" class="om-chat">' + "".join(msgs_html) + '</div>',
        unsafe_allow_html=True,
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Input area
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown('<div class="om-spacer"></div>', unsafe_allow_html=True)

c1, c2 = st.columns([5, 1])
with c1:
    mensaje = st.text_area(
        "m",
        label_visibility="collapsed",
        placeholder="Escribe lo que quieras compartir...",
        height=90,
        key=f"i_{st.session_state.input_key}",
    )
with c2:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    enviar = st.button("Enviar", use_container_width=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Enviar mensaje
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if enviar and mensaje and mensaje.strip():
    t = mensaje.strip()
    st.session_state.mensajes.append({"rol": "user", "contenido": t})
    with st.spinner(""):
        res = chat(st.session_state.session_id, t, st.session_state.user_code)
    respuesta = res.get("respuesta", "")
    respuesta = respuesta.replace("——", "—")
    st.session_state.mensajes.append({
        "rol": "agent",
        "contenido": respuesta,
        "protocolo": res.get("protocolo", "normal"),
    })
    st.session_state.turno = res.get("turno", st.session_state.turno + 1)
    st.session_state.input_key += 1
    st.rerun()

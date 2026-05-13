"""
chat_v2.py — ONTOMIND v5 — Chat + Dashboard de Cierre (Test A/B)
Coloca este archivo en: C:\\Ontomind-Frontend\\pages\\chat_v2.py
URL resultante: /chat_v2

Cambios respecto a app.py:
  - layout="wide" para panel derecho
  - Panel dashboard con 4 enunciados + barra de progreso
  - Botón de valoración con flujo de confirmación
  - Llamada a /evaluar/{session_id} al confirmar
  - Expansión del panel con resultados completos
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
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CSS COMPLETO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Source+Sans+3:wght@300;400;500;600&display=swap');

:root {
    --bg:           #0e0e10;
    --surface:      #1a1a20;
    --surface2:     #141418;
    --border:       #2a2a32;
    --accent:       #d4a855;
    --accent-soft:  #e8c97d;
    --accent2:      #8eaadc;
    --text:         #eeeef2;
    --text-soft:    #c0c0d0;
    --dim:          #8a8580;
    /* Dashboard inactivo */
    --dash-dim:     #303038;
    --dash-border:  #1e1e26;
    --dash-text:    #3a3a48;
}

/* === GLOBAL === */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
}
[data-testid="stHeader"]     { display: none; }
[data-testid="stSidebar"]    { display: none !important; }
[data-testid="stSidebarNav"] { display: none !important; }
button[kind="headerNoPadding"] { display: none !important; }

/* Quitar padding lateral del wide layout */
[data-testid="stAppViewContainer"] > .main > .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
[data-testid="stVerticalBlock"] { gap: 0 !important; }

/* === LAYOUT COLUMNAS === */
.chat-col {
    padding: 0 2rem 0 2rem;
    min-height: 100vh;
    border-right: 1px solid var(--border);
}
.dash-col {
    padding: 0 1.5rem;
    min-height: 100vh;
    background: var(--bg);
}

/* === HEADER === */
.om-header {
    text-align: center;
    padding: 2rem 1rem 1.2rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.5rem;
}
.om-title {
    font-family: 'Libre Baskerville', Georgia, serif;
    font-size: clamp(1.8rem, 4vw, 2.4rem);
    font-weight: 700;
    letter-spacing: 0.2em;
    color: var(--accent);
    margin: 0;
    white-space: nowrap;
}
.om-subtitle {
    font-family: 'Source Sans 3', sans-serif;
    font-size: 0.8rem;
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
    max-width: 680px;
    margin: 0 auto;
    padding: 0 0.5rem;
}
.om-msg { margin: 1.2rem 0; animation: fadeIn 0.3s ease; }
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
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
.om-label-coach { color: var(--accent); }
.om-user {
    background: var(--surface);
    border-left: 3px solid var(--accent2);
    padding: 1rem 1.2rem;
    border-radius: 0 8px 8px 0;
    font-family: 'Source Sans 3', sans-serif;
    font-size: clamp(1rem, 2.5vw, 1.1rem);
    line-height: 1.7;
    color: var(--text);
}
.om-coach {
    background: var(--surface2);
    border-left: 3px solid var(--accent);
    padding: 1.2rem 1.4rem;
    border-radius: 0 8px 8px 0;
    font-family: 'Libre Baskerville', Georgia, serif;
    font-size: clamp(1.05rem, 2.5vw, 1.15rem);
    line-height: 1.9;
    color: var(--text);
    font-style: italic;
}
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
.om-b-normal      { background:#1e3a1e; color:#7abf7a; border:1px solid #2e5a2e; }
.om-b-silencio    { background:#1e1e3a; color:#7a7abf; border:1px solid #2e2e5a; }
.om-b-incoherencia{ background:#3a2a1a; color:#bf9a5a; border:1px solid #5a3a1a; }
.om-b-vigil       { background:#3a1a1a; color:#d06060; border:1px solid #6a2a2a; }

.om-welcome {
    text-align: center;
    padding: 4rem 2rem;
}
.om-welcome-icon  { font-size: 2.5rem; color: var(--border); margin-bottom: 1rem; }
.om-welcome-text  {
    font-family: 'Libre Baskerville', Georgia, serif;
    font-size: clamp(1.1rem, 3vw, 1.35rem);
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
    font-size: 1rem !important;
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
    box-shadow: 0 4px 12px rgba(212,168,85,0.3) !important;
}
div[data-testid="stButton"] button:disabled {
    background: var(--dash-dim) !important;
    color: var(--dash-text) !important;
    transform: none !important;
    box-shadow: none !important;
    cursor: not-allowed !important;
}

.om-spacer { height: 140px; }

[data-testid="stExpander"] {
    max-width: 280px !important;
    margin: 0 auto 1rem !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    background: var(--surface) !important;
}
[data-testid="stExpander"] summary {
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 0.75rem !important;
    color: var(--dim) !important;
    letter-spacing: 0.05em !important;
}
[data-testid="stExpander"] [data-testid="stTextInput"] input {
    background: var(--bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    color: var(--text) !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 0.85rem !important;
    text-align: center !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   DASHBOARD — Panel derecho
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.dash-panel {
    padding: 19rem 0 2rem;
    font-family: 'Source Sans 3', sans-serif;
}

/* Título del panel */
.dash-title {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--dash-text);
    margin-bottom: 1.8rem;
    padding-bottom: 0.8rem;
    border-bottom: 1px solid var(--dash-border);
    transition: color 0.5s ease, border-color 0.5s ease;
}
.dash-title.active {
    color: var(--dim);
    border-color: var(--border);
}

/* Enunciados */
.dash-enunciado {
    margin-bottom: 1.4rem;
    transition: all 0.5s ease;
}
.dash-enunciado-label {
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--dash-text);
    margin-bottom: 0.35rem;
    transition: color 0.5s ease;
}
.dash-enunciado-label.active { color: var(--dim); }

.dash-enunciado-valor {
    font-size: 0.85rem;
    color: var(--dash-text);
    line-height: 1.5;
    font-style: italic;
    min-height: 1.2rem;
    transition: color 0.5s ease;
}
.dash-enunciado-valor.active  { color: var(--text-soft); }
.dash-enunciado-valor.revealed { color: var(--text); font-style: normal; }
.dash-enunciado-valor.gold    { color: var(--accent); font-style: normal; font-weight: 600; }

/* Puntos de placeholder */
.dash-dots {
    display: inline-flex;
    gap: 5px;
    align-items: center;
    margin-top: 4px;
}
.dash-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--dash-dim);
    transition: background 0.5s ease;
}
.dash-dot.active { background: var(--border); }

/* Separador */
.dash-sep {
    border: none;
    border-top: 1px solid var(--dash-border);
    margin: 1.6rem 0;
    transition: border-color 0.5s ease;
}
.dash-sep.active { border-color: var(--border); }

/* Barra de progreso */
.dash-bar-label {
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--dash-text);
    margin-bottom: 0.8rem;
    transition: color 0.5s ease;
}
.dash-bar-label.active { color: var(--dim); }

.dash-bar-track {
    position: relative;
    height: 4px;
    background: var(--dash-dim);
    border-radius: 2px;
    margin-bottom: 0.6rem;
    transition: background 0.5s ease;
}
.dash-bar-track.active { background: #252530; }

.dash-bar-fill {
    height: 100%;
    border-radius: 2px;
    background: linear-gradient(90deg, #3a5a3a, var(--accent));
    transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
    width: 0%;
}

.dash-bar-nodes {
    display: flex;
    justify-content: space-between;
    margin-top: 0.5rem;
}
.dash-bar-node {
    font-size: 0.52rem;
    color: var(--dash-text);
    text-align: center;
    width: 18%;
    line-height: 1.3;
    transition: color 0.5s ease;
}
.dash-bar-node.active   { color: #504a44; }
.dash-bar-node.current  { color: var(--accent); font-weight: 600; }

/* Bloque expandido: Lo que se movió / Semilla */
.dash-reveal {
    margin-top: 1.6rem;
    animation: revealDown 0.5s ease;
}
@keyframes revealDown {
    from { opacity: 0; transform: translateY(-8px); }
    to   { opacity: 1; transform: translateY(0); }
}
.dash-reveal-block {
    margin-bottom: 1.4rem;
}
.dash-reveal-label {
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.5rem;
}
.dash-reveal-text {
    font-family: 'Libre Baskerville', Georgia, serif;
    font-size: 0.9rem;
    color: var(--text);
    line-height: 1.7;
    font-style: italic;
    border-left: 2px solid var(--accent);
    padding-left: 0.8rem;
}
.dash-reveal-text.semilla {
    border-color: var(--accent2);
    color: var(--text-soft);
}

/* Advertencia de confirmación */
.dash-warning {
    background: #1a1610;
    border: 1px solid #3a3010;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
    font-size: 0.8rem;
    color: #c8a84a;
    line-height: 1.6;
    animation: fadeIn 0.3s ease;
}
.dash-warning strong { color: var(--accent); }

@media (max-width: 768px) {
    .chat-col { padding: 0 1rem; }
    .dash-col  { padding: 1.5rem 1rem; border-top: 1px solid var(--border); }
}
</style>
""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Estado de sesión
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DEFAULTS = {
    "session_id":          None,
    "mensajes":            [],
    "turno":               0,
    "input_key":           0,
    "user_code":           "",
    # Dashboard
    "valoracion_usada":    False,   # True cuando el usuario confirmó
    "confirmacion_pend":   False,   # True cuando mostrar advertencia
    "evaluacion":          None,    # Dict con resultado del evaluador
}
for k, v in DEFAULTS.items():
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
        return {"respuesta": "Tiempo de espera agotado.", "protocolo": "error"}
    except Exception as e:
        return {"respuesta": f"Error de conexión: {e}", "protocolo": "error"}


def evaluar_sesion(session_id: str) -> dict:
    """Llama al endpoint de evaluación final de la sesión."""
    try:
        r = httpx.post(
            f"{API_URL}/evaluar",
            json={"session_id": session_id},
            timeout=30,
        )
        return r.json()
    except Exception as e:
        # Fallback: resultado vacío si el endpoint aún no existe
        return {
            "posicion_inicial":      "mixto",
            "posicion_final":        "mixto",
            "arco_detectado":        "estable",
            "score_condiciones":     30,
            "posibilidad_nueva":     False,
            "creencia_en_movimiento":"no",
            "declaracion_detectada": False,
            "declaracion_texto":     "",
            "semilla_plantada":      "no",
            "llave_maestra_dominante": "—",
            "nivel_riesgo_max":      "ninguno",
            "recomendacion":         "",
            "_error": str(e),
        }


def badge(protocolo):
    css_map = {
        "normal":       "om-b-normal",
        "silencio":     "om-b-silencio",
        "incoherencia": "om-b-incoherencia",
        "vigil":        "om-b-vigil",
    }
    return f'<span class="om-badge {css_map.get(protocolo, "om-b-normal")}">{protocolo}</span>'


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Helpers del dashboard
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NIVELES = [
    (0,  20, "Supervivencia"),
    (21, 40, "Brecha de efectividad"),
    (41, 60, "Exploración"),
    (61, 80, "Declaración"),
    (81, 100,"Compromiso elegido"),
]

POSICION_LABEL = {
    "victima":     "Posición víctima",
    "mixto":       "En transición",
    "protagonista":"Posición protagonista",
}

def nivel_actual(score: int) -> int:
    """Devuelve el índice (0-4) del nivel según el score."""
    for i, (lo, hi, _) in enumerate(NIVELES):
        if lo <= score <= hi:
            return i
    return 0

def porcentaje_barra(score: int) -> float:
    """Convierte score 0-100 en porcentaje de barra (10%-100%)."""
    return max(10.0, min(100.0, score))

def dots_html(n=5):
    return '<div class="dash-dots">' + ''.join(
        f'<div class="dash-dot"></div>' for _ in range(n)
    ) + '</div>'

def dots_html_active(n=5):
    return '<div class="dash-dots">' + ''.join(
        f'<div class="dash-dot active"></div>' for _ in range(n)
    ) + '</div>'


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Renderizado del dashboard
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def render_dashboard(col, turno: int, ev: dict | None, valorada: bool, conf_pend: bool):
    """Renderiza el panel derecho en todos sus estados."""
    with col:
        st.markdown('<div class="dash-panel">', unsafe_allow_html=True)

        activo = turno >= 4

        # ── Título ──────────────────────────────────────
        titulo_cls = "dash-title active" if activo else "dash-title"
        st.markdown(f'<div class="{titulo_cls}">SESIÓN EN CURSO</div>',
                    unsafe_allow_html=True)

        # ── 4 Enunciados ─────────────────────────────────
        enunciados = [
            ("Desde dónde llegaste",
             POSICION_LABEL.get(ev.get("posicion_inicial",""), "—") if ev else None),
            ("Hasta dónde llegaste",
             POSICION_LABEL.get(ev.get("posicion_final",""), "—") if ev else None),
            ("Lo que se abrió",
             ev.get("llave_maestra_dominante","—") if ev else None),
            ("Lo que se movió",
             (ev.get("declaracion_texto","") or
              ev.get("creencia_en_movimiento","") or "—") if ev else None),
        ]

        for label, valor in enunciados:
            lbl_cls = "dash-enunciado-label active" if activo else "dash-enunciado-label"
            if ev and valor:
                val_cls = "dash-enunciado-valor gold" if label in ("Desde dónde llegaste","Hasta dónde llegaste") else "dash-enunciado-valor revealed"
                val_html = f'<div class="{val_cls}">{_html.escape(str(valor))}</div>'
            elif activo:
                val_html = dots_html_active()
            else:
                val_html = dots_html()

            st.markdown(
                f'<div class="dash-enunciado">'
                f'<div class="{lbl_cls}">{label}</div>'
                f'{val_html}'
                f'</div>',
                unsafe_allow_html=True,
            )

        # ── Separador ────────────────────────────────────
        sep_cls = "dash-sep active" if activo else "dash-sep"
        st.markdown(f'<hr class="{sep_cls}">', unsafe_allow_html=True)

        # ── Barra de progreso ─────────────────────────────
        bar_lbl_cls = "dash-bar-label active" if activo else "dash-bar-label"
        st.markdown(f'<div class="{bar_lbl_cls}">Progreso de sesión</div>',
                    unsafe_allow_html=True)

        score = ev.get("score_condiciones", 0) if ev else 0
        pct   = porcentaje_barra(score) if ev else 0
        idx   = nivel_actual(score) if ev else -1

        track_cls = "dash-bar-track active" if activo else "dash-bar-track"
        st.markdown(
            f'<div class="{track_cls}">'
            f'<div class="dash-bar-fill" style="width:{pct}%"></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Nodos de la barra
        nodos_html = '<div class="dash-bar-nodes">'
        for i, (_, _, nombre) in enumerate(NIVELES):
            node_cls = "dash-bar-node"
            if ev and i == idx:
                node_cls += " current"
            elif activo:
                node_cls += " active"
            nodos_html += f'<div class="{node_cls}">{nombre}</div>'
        nodos_html += '</div>'
        st.markdown(nodos_html, unsafe_allow_html=True)

        # ── Separador ────────────────────────────────────
        sep_cls = "dash-sep active" if activo else "dash-sep"
        st.markdown(f'<hr class="{sep_cls}">', unsafe_allow_html=True)

        # ── Advertencia de confirmación ───────────────────
        if conf_pend and not valorada:
            st.markdown(
                '<div class="dash-warning">'
                '<strong>Solo puedes valorar una vez por sesión.</strong><br>'
                'Pulsa confirmar cuando sientas que la conversación ha llegado '
                'a su momento natural de cierre.'
                '</div>',
                unsafe_allow_html=True,
            )
            confirmar = st.button("Confirmar valoración", key="btn_confirmar",
                                  use_container_width=True)
            cancelar  = st.button("Cancelar", key="btn_cancelar",
                                  use_container_width=True)
            if confirmar:
                with st.spinner(""):
                    ev_result = evaluar_sesion(st.session_state.session_id)
                st.session_state.evaluacion     = ev_result
                st.session_state.valoracion_usada  = True
                st.session_state.confirmacion_pend = False
                st.rerun()
            if cancelar:
                st.session_state.confirmacion_pend = False
                st.rerun()

        # ── Botón principal ───────────────────────────────
        elif not valorada and not conf_pend:
            boton_activo = activo
            if boton_activo:
                valorar = st.button("Valorar sesión", key="btn_valorar",
                                    use_container_width=True)
                if valorar:
                    st.session_state.confirmacion_pend = True
                    st.rerun()
            else:
                st.button("Valorar sesión", key="btn_valorar_dis",
                          use_container_width=True, disabled=True)
                turnos_faltan = 4 - turno
                st.markdown(
                    f'<div style="text-align:center;font-size:0.62rem;'
                    f'color:var(--dash-text);margin-top:0.4rem;letter-spacing:0.06em;">'
                    f'Disponible en {turnos_faltan} turno{"s" if turnos_faltan!=1 else ""} más'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        # ── Resultado revelado ────────────────────────────
        elif valorada and ev:
            st.markdown(
                '<div style="text-align:center;font-size:0.62rem;color:#4a6a4a;'
                'letter-spacing:0.1em;margin-bottom:1rem;">✓ SESIÓN VALORADA</div>',
                unsafe_allow_html=True,
            )

            # Lo que se movió
            movido = ev.get("declaracion_texto","") or ev.get("creencia_en_movimiento","")
            if movido and movido not in ("no","—",""):
                st.markdown(
                    '<div class="dash-reveal">'
                    '<div class="dash-reveal-block">'
                    '<div class="dash-reveal-label">Lo que se movió</div>'
                    f'<div class="dash-reveal-text">{_html.escape(movido)}</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )

            # Semilla
            semilla = ev.get("semilla_plantada","")
            if semilla and semilla not in ("no","—",""):
                st.markdown(
                    '<div class="dash-reveal-block">'
                    '<div class="dash-reveal-label">Semilla para esta semana</div>'
                    f'<div class="dash-reveal-text semilla">{_html.escape(semilla)}</div>'
                    '</div></div>',
                    unsafe_allow_html=True,
                )

        st.markdown('</div>', unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Inicializar sesión
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if not st.session_state.session_id:
    st.session_state.session_id = nueva_sesion()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Layout: columna chat (izq) + dashboard (der)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
col_chat, col_dash = st.columns([3, 1.2], gap="small")

# ── COLUMNA CHAT ──────────────────────────────────────
with col_chat:
    st.markdown('<div class="chat-col">', unsafe_allow_html=True)

    # Header
    st.markdown(
        '<div class="om-header">'
        '<h1 class="om-title">ONTOMIND</h1>'
        '<p class="om-subtitle">Crecimiento personal</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="om-session">sesión {st.session_state.session_id[:8]} · '
        f'turno {st.session_state.turno}</div>',
        unsafe_allow_html=True,
    )

    # Identificador de usuario
    with st.expander("👤 Identificarme", expanded=False):
        uci = st.text_input(
            "Código de usuario",
            label_visibility="collapsed",
            placeholder="ej: JAVIER-01",
            value=st.session_state.user_code,
            key="user_code_input",
        )
        if uci != st.session_state.user_code:
            st.session_state.user_code = uci.strip().upper()
        if st.session_state.user_code:
            st.markdown(
                f'<div style="font-family:\'Source Sans 3\',sans-serif;font-size:0.65rem;'
                f'color:#4ac17a;margin-top:0.2rem;">● Conectado como {st.session_state.user_code}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="font-family:\'Source Sans 3\',sans-serif;font-size:0.65rem;'
                'color:var(--dim);margin-top:0.2rem;">Sin identificar — el historial no se guardará</div>',
                unsafe_allow_html=True,
            )

    # Mensajes
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

    # Input
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
        enviar = st.button("Enviar", use_container_width=True, key="btn_enviar")

    st.markdown('</div>', unsafe_allow_html=True)

# ── COLUMNA DASHBOARD ──────────────────────────────────
render_dashboard(
    col         = col_dash,
    turno       = st.session_state.turno,
    ev          = st.session_state.evaluacion,
    valorada    = st.session_state.valoracion_usada,
    conf_pend   = st.session_state.confirmacion_pend,
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Enviar mensaje
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if enviar and mensaje and mensaje.strip():
    t = mensaje.strip()
    st.session_state.mensajes.append({"rol": "user", "contenido": t})
    with st.spinner(""):
        res = chat(st.session_state.session_id, t, st.session_state.user_code)
    respuesta = res.get("respuesta", "").replace("——", "—")
    st.session_state.mensajes.append({
        "rol":       "agent",
        "contenido":  respuesta,
        "protocolo":  res.get("protocolo", "normal"),
    })
    st.session_state.turno = res.get("turno", st.session_state.turno + 1)
    st.session_state.input_key += 1
    st.rerun()

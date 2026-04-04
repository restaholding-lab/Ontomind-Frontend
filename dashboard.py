"""
dashboard.py — Dashboard de supervisores ONTOMIND
Monitorización de sesiones, alertas VIGIL y métricas ontológicas.
"""
import streamlit as st
import httpx
import os
import json
from datetime import datetime

API_URL      = os.getenv("ONTOMIND_API_URL", "https://ontomind-production.up.railway.app")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

st.set_page_config(
    page_title  = "ONTOMIND · Supervisores",
    page_icon   = "⬡",
    layout      = "wide",
    initial_sidebar_state = "expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Cormorant+Garamond:wght@300;400&display=swap');

:root {
    --bg:       #0a0c10;
    --surface:  #12151c;
    --surface2: #181c26;
    --border:   #232840;
    --accent:   #4a7fc1;
    --warn:     #c17a4a;
    --danger:   #c14a4a;
    --ok:       #4ac17a;
    --text:     #cdd3e0;
    --text-dim: #5a6280;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
}
[data-testid="stHeader"] { display: none; }
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

.dash-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.2rem;
}
.dash-subtitle {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.6rem;
    font-weight: 300;
    color: var(--text);
    margin-bottom: 2rem;
}

/* Métricas */
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1.2rem;
    text-align: center;
}
.metric-value {
    font-size: 2rem;
    font-weight: 500;
    margin-bottom: 0.2rem;
}
.metric-label {
    font-size: 0.55rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-dim);
}

/* Alertas */
.alerta-card {
    background: #1a0f0f;
    border: 1px solid #3a1515;
    border-left: 3px solid var(--danger);
    border-radius: 0 6px 6px 0;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
}
.alerta-session {
    font-size: 0.6rem;
    color: var(--text-dim);
    margin-bottom: 0.3rem;
}
.alerta-nivel {
    display: inline-block;
    font-size: 0.55rem;
    padding: 2px 8px;
    border-radius: 20px;
    background: #2a0f0f;
    color: var(--danger);
    border: 1px solid var(--danger);
    letter-spacing: 0.1em;
    margin-bottom: 0.4rem;
}
.alerta-msg {
    font-size: 0.8rem;
    color: var(--text);
    font-family: 'Cormorant Garamond', serif;
    font-style: italic;
}

/* Sesiones */
.sesion-row {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.8rem 1rem;
    margin: 0.4rem 0;
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr;
    align-items: center;
    font-size: 0.7rem;
}
.pos-victima   { color: var(--danger); }
.pos-protagonista { color: var(--ok); }
.pos-mixto     { color: var(--warn); }

/* Tabla */
.stDataFrame { font-family: 'DM Mono', monospace !important; font-size: 0.7rem !important; }

/* Botones */
.stButton button {
    background: transparent !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.6rem !important;
    letter-spacing: 0.1em !important;
}
.stButton button:hover { border-color: var(--accent) !important; color: var(--accent) !important; }
</style>
""", unsafe_allow_html=True)


# ─── Funciones de datos ───────────────────────────────────
def supabase_get(tabla: str, params: str = "") -> list:
    if not SUPABASE_URL or not SUPABASE_KEY:
        return []
    try:
        r = httpx.get(
            f"{SUPABASE_URL}/rest/v1/{tabla}?{params}",
            headers={
                "apikey":        SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            },
            timeout=10
        )
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []


def marcar_revisado(alerta_id: int) -> bool:
    try:
        r = httpx.patch(
            f"{SUPABASE_URL}/rest/v1/alertas_vigil?id=eq.{alerta_id}",
            headers={
                "apikey":        SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type":  "application/json"
            },
            json={"revisado": True},
            timeout=10
        )
        return r.status_code in (200, 204)
    except Exception:
        return False


def api_health() -> bool:
    try:
        r = httpx.get(f"{API_URL}/health", timeout=5)
        return r.status_code == 200
    except Exception:
        return False


# ─── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("**◈ ONTOMIND**")
    st.markdown("---")
    vista = st.radio(
        "Vista",
        ["Resumen", "Alertas VIGIL", "Sesiones", "Consultar sesión"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    if st.button("Actualizar datos"):
        st.rerun()

    st.markdown(f"""
    <div style='margin-top:2rem; font-size:0.55rem; color:#3a4060;'>
    API: {"● ACTIVA" if api_health() else "● INACTIVA"}<br>
    {datetime.now().strftime("%H:%M:%S")}
    </div>
    """, unsafe_allow_html=True)


# ─── Header ───────────────────────────────────────────────
st.markdown('<div class="dash-title">Panel de Supervisión</div>', unsafe_allow_html=True)
st.markdown('<div class="dash-subtitle">ONTOMIND · Monitor Ontológico</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# VISTA: RESUMEN
# ════════════════════════════════════════════════════════════
if vista == "Resumen":
    mapas    = supabase_get("mapa_observador", "limit=1000")
    alertas  = supabase_get("alertas_vigil", "revisado=eq.false&limit=100")

    victimas     = [m for m in mapas if m.get("ultima_posicion") == "victima"]
    protagonistas= [m for m in mapas if m.get("ultima_posicion") == "protagonista"]
    ancora_act   = [m for m in mapas if m.get("ancora_activado")]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:#4a7fc1">{len(mapas)}</div>
            <div class="metric-label">Sesiones totales</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:#c14a4a">{len(alertas)}</div>
            <div class="metric-label">Alertas VIGIL activas</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        pct = round(len(protagonistas)/len(mapas)*100) if mapas else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:#4ac17a">{pct}%</div>
            <div class="metric-label">Posición protagonista</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:#c14a4a">{len(ancora_act)}</div>
            <div class="metric-label">ANCORA activados</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if alertas:
        st.markdown("### ⚠ Alertas VIGIL pendientes de revisión")
        for a in alertas[:5]:
            st.markdown(f"""
            <div class="alerta-card">
                <div class="alerta-session">sesión {a.get('session_id','?')[:12]}... · {a.get('timestamp','')[:16]}</div>
                <div class="alerta-nivel">{a.get('nivel','?').upper()}</div>
                <div class="alerta-msg">{a.get('mensaje','')[:200]}</div>
            </div>
            """, unsafe_allow_html=True)

    if not mapas and not alertas:
        st.markdown("""
        <div style="text-align:center; padding:3rem; color:#3a4060;">
            <div style="font-size:2rem">⬡</div>
            <div style="margin-top:1rem; font-family:'Cormorant Garamond',serif; font-style:italic;">
                Aún no hay sesiones registradas.<br>
                Los datos aparecerán aquí cuando los usuarios interactúen con ONTOMIND.
            </div>
        </div>
        """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# VISTA: ALERTAS VIGIL
# ════════════════════════════════════════════════════════════
elif vista == "Alertas VIGIL":
    st.markdown("### Alertas VIGIL — Protocolo de crisis")

    mostrar = st.radio("Mostrar", ["Sin revisar", "Todas"], horizontal=True)
    params  = "revisado=eq.false&order=timestamp.desc" if mostrar == "Sin revisar" else "order=timestamp.desc"
    alertas = supabase_get("alertas_vigil", params + "&limit=50")

    if not alertas:
        st.success("No hay alertas pendientes de revisión.")
    else:
        for a in alertas:
            col1, col2 = st.columns([5, 1])
            with col1:
                nivel_color = {"critico": "#c14a4a", "alto": "#c17a4a", "latente": "#c1c14a"}.get(a.get("nivel",""), "#5a6280")
                st.markdown(f"""
                <div class="alerta-card">
                    <div class="alerta-session">
                        ID: {a.get('session_id','?')[:16]}... &nbsp;·&nbsp; {a.get('timestamp','')[:16]}
                    </div>
                    <div class="alerta-nivel" style="color:{nivel_color}; border-color:{nivel_color}">
                        {a.get('nivel','?').upper()}
                    </div>
                    <div class="alerta-msg">{a.get('mensaje','')}</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
                if not a.get("revisado") and st.button("Marcar\nrevisado", key=f"rev_{a.get('id')}"):
                    if marcar_revisado(a.get("id")):
                        st.success("Marcado")
                        st.rerun()


# ════════════════════════════════════════════════════════════
# VISTA: SESIONES
# ════════════════════════════════════════════════════════════
elif vista == "Sesiones":
    st.markdown("### Mapa del Observador — Sesiones activas")
    mapas = supabase_get("mapa_observador", "order=updated_at.desc&limit=100")

    if not mapas:
        st.info("No hay sesiones registradas aún.")
    else:
        for m in mapas:
            pos = m.get("ultima_posicion", "desconocido")
            pos_color = {"victima": "pos-victima", "protagonista": "pos-protagonista",
                         "mixto": "pos-mixto"}.get(pos, "")
            ancora = "⚠ ANCORA" if m.get("ancora_activado") else ""
            quiebre = m.get("ultimo_quiebre", "—")
            updated = m.get("updated_at", "")[:16] if m.get("updated_at") else "—"

            st.markdown(f"""
            <div class="sesion-row">
                <div style="font-size:0.65rem">
                    <span style="color:#3a5080">{m.get('session_id','')[:8]}...</span>
                    <span style="color:#c14a4a; margin-left:0.5rem">{ancora}</span>
                </div>
                <div class="{pos_color}">{pos}</div>
                <div style="color:#5a6280">{quiebre}</div>
                <div style="color:#3a4060; font-size:0.6rem">{updated}</div>
            </div>
            """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# VISTA: CONSULTAR SESIÓN
# ════════════════════════════════════════════════════════════
elif vista == "Consultar sesión":
    st.markdown("### Consultar sesión específica")
    session_id = st.text_input("Session ID", placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")

    if session_id and len(session_id) > 8:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Mapa del Observador**")
            try:
                r = httpx.get(f"{API_URL}/sesion/{session_id}/mapa", timeout=10)
                if r.status_code == 200:
                    mapa = r.json().get("mapa", {})
                    st.json({
                        "ultima_posicion":    mapa.get("ultima_posicion"),
                        "ultimo_quiebre":     mapa.get("ultimo_quiebre"),
                        "ancora_activado":    mapa.get("ancora_activado"),
                        "turnos_desde_ancora":mapa.get("turnos_desde_ancora"),
                    })
            except Exception as e:
                st.error(f"Error: {e}")

        with col2:
            st.markdown("**Historial de conversación**")
            try:
                r = httpx.get(f"{API_URL}/sesion/{session_id}/historial", timeout=10)
                if r.status_code == 200:
                    mensajes = r.json().get("mensajes", [])
                    for msg in mensajes:
                        rol = msg.get("rol", "?")
                        contenido = msg.get("contenido", "")
                        if rol == "user":
                            st.markdown(f"**Tú:** {contenido}")
                        else:
                            st.markdown(f"*ONTOMIND:* {contenido}")
                        st.markdown("---")
            except Exception as e:
                st.error(f"Error: {e}")

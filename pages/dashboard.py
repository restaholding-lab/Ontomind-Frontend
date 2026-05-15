"""
dashboard.py v2 - ONTOMIND Supervisor Dashboard con Log de Nodos
"""
import streamlit as st
import httpx
import os
import json

API_URL      = os.getenv("ONTOMIND_API_URL", "https://ontomind-production.up.railway.app")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

st.set_page_config(page_title="ONTOMIND Supervisores", page_icon="⬡",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Cormorant+Garamond:wght@400&display=swap');
:root{--bg:#0a0c10;--s:#12151c;--b:#232840;--a:#4a7fc1;--w:#c17a4a;--d:#c14a4a;--ok:#4ac17a;--t:#cdd3e0;--dim:#5a6280;}
html,body,[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:var(--t)!important;font-family:'DM Mono',monospace!important;font-size:15px!important;}
[data-testid="stHeader"]{display:none;}
[data-testid="stSidebar"]{background:var(--s)!important;border-right:1px solid var(--b)!important;}
.mc{background:var(--s);border:1px solid var(--b);border-radius:6px;padding:1.1rem;text-align:center;margin-bottom:0.5rem;}
.mv{font-size:2rem;font-weight:500;}
.ml{font-size:0.55rem;letter-spacing:0.15em;text-transform:uppercase;color:var(--dim);margin-top:0.2rem;}
.nc{background:var(--s);border:1px solid var(--b);border-radius:6px;padding:0.9rem;margin:0.4rem 0;}
.nt{font-size:0.6rem;letter-spacing:0.15em;text-transform:uppercase;color:var(--a);margin-bottom:0.6rem;font-weight:500;}
.nk{color:var(--dim);font-size:0.68rem;}
.nv{color:var(--t);font-size:0.82rem;}
.ui-box{background:#13151f;border-left:2px solid #7e9cc8;padding:0.7rem 1rem;border-radius:0 6px 6px 0;font-family:'Cormorant Garamond',serif;font-size:1.05rem;color:var(--t);margin:0.4rem 0;}
.re-box{background:#0f1218;border-left:2px solid var(--a);padding:0.8rem 1rem;border-radius:0 6px 6px 0;font-family:'Cormorant Garamond',serif;font-size:1.05rem;color:#e8e4dc;margin:0.4rem 0;}
.ac{background:#1a0f0f;border:1px solid #3a1515;border-left:3px solid var(--d);border-radius:0 6px 6px 0;padding:1rem 1.2rem;margin:0.5rem 0;}
.stButton button{background:transparent!important;border:1px solid var(--b)!important;color:var(--t)!important;font-family:'DM Mono',monospace!important;font-size:0.65rem!important;white-space:nowrap!important;}
.stButton button:hover{border-color:var(--a)!important;color:var(--a)!important;}
</style>""", unsafe_allow_html=True)


def sb(tabla, params="", limit=100):
    import urllib.parse, time
    try:
        ts = int(time.time())
        url = f"{API_URL}/admin/tabla/{tabla}?limit={limit}&_ts={ts}"
        if params:
            url += "&params=" + urllib.parse.quote(params)
        r = httpx.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                return [item if isinstance(item, dict) else {} for item in data]
            return []
        return []
    except Exception as e:
        st.error(f"Error cargando {tabla}: {e}")
        return []

def sb_count(tabla, params=""):
    """Cuenta total real de filas sin límite de paginación."""
    import urllib.parse
    try:
        url = f"{SUPABASE_URL.strip()}/rest/v1/{tabla}?select=id"
        if params:
            url += "&" + params
        r = httpx.get(url, headers={
            "apikey": SUPABASE_KEY.strip(),
            "Authorization": f"Bearer {SUPABASE_KEY.strip()}",
            "Prefer": "count=exact",
            "Range": "0-0",
        }, timeout=10)
        cr = r.headers.get("content-range", "")
        if "/" in cr:
            return int(cr.split("/")[-1])
        return None
    except:
        return None

def pj(v):
    if isinstance(v,dict): return v
    if isinstance(v,str):
        try: return json.loads(v)
        except: return {}
    return {}

def cc(v):
    try:
        f=float(v)
        if f>=0.75: return "#4ac17a"
        if f>=0.45: return "#c17a4a"
        return "#c14a4a"
    except: return "#5a6280"

PC={"normal":"#4ac17a","silencio":"#6a6a9a","incoherencia":"#c17a4a","vigil":"#c14a4a"}
DC={"transformacion":"#4ac17a","regresion":"#c14a4a","estable":"#5a6280"}
POSC={"victima":"#c14a4a","protagonista":"#4ac17a","mixto":"#c17a4a"}

def badge(txt,color):
    return f'<span style="display:inline-block;font-size:0.5rem;padding:2px 6px;border-radius:20px;letter-spacing:0.08em;text-transform:uppercase;color:{color};border:1px solid {color};background:#0a0c10;">{txt}</span>'

def api_ok():
    try: return httpx.get(f"{API_URL}/health",timeout=4).status_code==200
    except: return False


with st.sidebar:
    st.markdown("**◈ ONTOMIND**")
    st.markdown("---")
    VISTAS = ["Resumen","Usuarios","Conversaciones","Log de Nodos","Etiquetado DPO","Alertas VIGIL","Sesiones","Consultar sesion"]
    if "vista_radio" not in st.session_state:
        st.session_state["vista_radio"] = "Resumen"
    # Aplicar navegación pendiente ANTES de crear el widget
    if st.session_state.get("_nav_pending"):
        st.session_state["vista_radio"] = st.session_state.pop("_nav_pending")
    vista = st.radio("Vista", VISTAS, label_visibility="collapsed", key="vista_radio")
    st.markdown("---")
    if st.button("Actualizar", type="primary"): st.cache_data.clear(); st.rerun()
    ok=api_ok()
    st.markdown(f'<div style="margin-top:1.5rem;font-size:0.55rem;color:#3a4060;">API: {"● ACTIVA" if ok else "● INACTIVA"}</div>',unsafe_allow_html=True)

st.markdown('<div style="font-size:0.7rem;letter-spacing:0.3em;text-transform:uppercase;color:#4a7fc1;margin-bottom:0.2rem;">Panel de Supervision</div>',unsafe_allow_html=True)
st.markdown('<div style="font-family:Cormorant Garamond,serif;font-size:1.6rem;color:#cdd3e0;margin-bottom:1.5rem;">ONTOMIND · Monitor Ontologico</div>',unsafe_allow_html=True)


if vista == "Resumen":
    mapas=sb("mapa_observador","order=updated_at.desc")
    alertas=sb("alertas_vigil","revisado=eq.false")
    # Contadores reales (sin límite de paginación)
    total_sesiones  = sb_count("mapa_observador") or len(mapas)
    total_alertas   = sb_count("alertas_vigil", "revisado=eq.false") or len(alertas)
    logs=sb("log_nodos","order=timestamp.desc",limit=500)
    protags=[m for m in mapas if m.get("ultima_posicion")=="protagonista"]
    ancoras=[m for m in mapas if m.get("ancora_activado")]
    c1,c2,c3,c4=st.columns(4)
    for col,val,lbl,color in [(c1,total_sesiones,"Sesiones","#4a7fc1"),(c2,total_alertas,"Alertas VIGIL","#c14a4a"),
        (c3,f"{round(len(protags)/len(mapas)*100) if mapas else 0}%","Protagonismo","#4ac17a"),(c4,len(ancoras),"ANCORA","#c14a4a")]:
        with col:
            st.markdown(f'<div class="mc"><div class="mv" style="color:{color}">{val}</div><div class="ml">{lbl}</div></div>',unsafe_allow_html=True)
    if logs:
        st.markdown("#### Distribucion de protocolos y llaves maestras")
        protos={}; llaves={}
        for l in logs:
            p=l.get("protocolo","normal"); protos[p]=protos.get(p,0)+1
            d=pj(l.get("dictamen",{})); lm=d.get("llave_maestra","")
            if lm: llaves[lm]=llaves.get(lm,0)+1
        ca,cb=st.columns(2)
        with ca:
            for p,n in protos.items(): st.markdown(f'`{p}` — {n} ({round(n/len(logs)*100)}%)')
        # Score medio de recompensa
        scores = [pj(l.get("evaluacion",{})).get("score_total",0) for l in logs if l.get("evaluacion")]
        if scores:
            avg = round(sum(scores)/len(scores),1)
            sc = "#4ac17a" if avg>=50 else "#c17a4a" if avg>=30 else "#c14a4a"
            st.markdown(f'Score medio recompensa: <span style="color:{sc};font-weight:600">{avg}/75</span>', unsafe_allow_html=True)
        # Score conversacional medio
        convs_all = sb("evaluaciones_conversacion", "order=timestamp.desc", limit=200)
        if convs_all:
            scores_conv = [c.get("score_condiciones",0) for c in convs_all]
            avg_conv = round(sum(scores_conv)/len(scores_conv),1)
            sc_conv = "#4ac17a" if avg_conv>=61 else "#c17a4a" if avg_conv>=41 else "#c14a4a"
            st.markdown(f'Score medio transformacion: <span style="color:{sc_conv};font-weight:600">{avg_conv}/100</span>', unsafe_allow_html=True)
        with cb:
            for lm,n in sorted(llaves.items(),key=lambda x:-x[1])[:6]: st.markdown(f'`{lm}` — {n}x')
    else:
        st.info("Aun no hay sesiones. Los datos apareceran cuando los usuarios interactuen con ONTOMIND.")


elif vista == "Usuarios":
    st.markdown("### Usuarios — Historial Multi-Conversación")
    st.markdown('<div style="font-size:0.7rem;color:#5a6280;margin-bottom:1.2rem;line-height:1.6;">Evolución longitudinal de cada usuario a lo largo de todas sus conversaciones.<br>Permite identificar patrones recurrentes, velocidad de transformación y temas dominantes.</div>', unsafe_allow_html=True)

    # Cargar todas las evaluaciones de conversacion
    convs_all = sb("evaluaciones_conversacion", "order=timestamp.desc", limit=500)

    if not convs_all:
        st.info("No hay usuarios con historial aun. Los datos apareceran cuando los usuarios realicen multiples sesiones con su codigo.")
    else:
        # Agrupar por user_code
        from collections import defaultdict
        usuarios_data = defaultdict(list)
        for c in convs_all:
            uc = c.get("user_code","anonimo")
            usuarios_data[uc].append(c)

        # Filtro
        user_list = sorted(usuarios_data.keys())
        selected = st.selectbox("Seleccionar usuario", ["todos"] + user_list)
        if selected != "todos":
            usuarios_data = {selected: usuarios_data[selected]}

        for user_code, sesiones in usuarios_data.items():
            if not sesiones: continue
            sesiones_ord = sorted(sesiones, key=lambda x: x.get("timestamp",""))

            scores    = [s.get("score_condiciones",0) for s in sesiones_ord]
            arcos     = [s.get("arco_detectado","estable") for s in sesiones_ord]
            pos_final = [s.get("posicion_final","victima") for s in sesiones_ord]
            llaves    = [s.get("llave_maestra_dominante","") for s in sesiones_ord if s.get("llave_maestra_dominante")]
            declaraciones = sum(1 for s in sesiones_ord if s.get("declaracion_detectada"))
            turnos_totales = sum(s.get("total_turnos",0) for s in sesiones_ord)

            # Score medio y tendencia
            score_medio = round(sum(scores)/len(scores)) if scores else 0
            score_inicio = scores[0] if scores else 0
            score_final  = scores[-1] if scores else 0
            tendencia = score_final - score_inicio

            def eje_lbl(s):
                if s>=81: return "TRANSFORMACIÓN"
                if s>=61: return "PROTAGONISMO"
                if s>=41: return "TRANSICIÓN"
                if s>=21: return "CONCIENCIA"
                return "SUPERVIVENCIA"

            tend_color = "#4ac17a" if tendencia>0 else "#c14a4a" if tendencia<0 else "#5a6280"
            tend_txt   = f"+{tendencia}" if tendencia>0 else str(tendencia)

            POS_COLOR = {"protagonista":"#4ac17a","mixto":"#c17a4a","victima":"#c14a4a"}
            ultima_pos = pos_final[-1] if pos_final else "victima"
            pos_color  = POS_COLOR.get(ultima_pos, "#5a6280")

            with st.expander(f"👤 {user_code}  ·  {len(sesiones)} sesion(es)  ·  Score medio: {score_medio}/100  ·  {eje_lbl(score_medio)}", expanded=True if selected != "todos" else False):

                # Métricas resumen
                um1,um2,um3,um4,um5 = st.columns(5)
                with um1:
                    sc = "#4ac17a" if score_medio>=61 else "#c17a4a" if score_medio>=41 else "#c14a4a"
                    st.markdown(f'<div class="nc" style="text-align:center"><div style="font-size:1.5rem;font-weight:700;color:{sc}">{score_medio}</div><div class="nk">Score medio</div></div>', unsafe_allow_html=True)
                with um2:
                    st.markdown(f'<div class="nc" style="text-align:center"><div style="font-size:1.3rem;font-weight:600;color:{tend_color}">{tend_txt}</div><div class="nk">Tendencia</div></div>', unsafe_allow_html=True)
                with um3:
                    st.markdown(f'<div class="nc" style="text-align:center"><div style="font-size:1rem;font-weight:600;color:{pos_color}">{ultima_pos}</div><div class="nk">Posicion actual</div></div>', unsafe_allow_html=True)
                with um4:
                    st.markdown(f'<div class="nc" style="text-align:center"><div style="font-size:1.4rem;font-weight:600;color:#4a7fc1">{len(sesiones)}</div><div class="nk">Sesiones</div></div>', unsafe_allow_html=True)
                with um5:
                    decl_c = "#4ac17a" if declaraciones>0 else "#5a6280"
                    st.markdown(f'<div class="nc" style="text-align:center"><div style="font-size:1.4rem;font-weight:600;color:{decl_c}">{declaraciones}</div><div class="nk">Declaraciones</div></div>', unsafe_allow_html=True)

                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

                # Línea de tiempo de scores — barra HTML visual
                st.markdown("**Evolución del Score de Transformación**")
                timeline_html = '<div style="display:flex;gap:6px;align-items:flex-end;height:80px;margin:8px 0">'
                for i, (sc_val, arc, ts) in enumerate(zip(scores, arcos, [s.get("timestamp","")[:10] for s in sesiones_ord])):
                    h_pct = max(8, sc_val)
                    c = "#4ac17a" if sc_val>=61 else "#c17a4a" if sc_val>=41 else "#c14a4a" if sc_val>=21 else "#8a3a3a"
                    timeline_html += f'<div style="display:flex;flex-direction:column;align-items:center;flex:1;gap:3px">'
                    timeline_html += f'<div style="font-size:0.55rem;color:#5a6280">{sc_val}</div>'
                    timeline_html += f'<div style="background:{c};height:{h_pct}%;width:100%;border-radius:3px 3px 0 0;min-height:6px"></div>'
                    timeline_html += f'<div style="font-size:0.5rem;color:#3a4060">{ts[-5:]}</div>'
                    timeline_html += '</div>'
                timeline_html += '</div>'
                st.markdown(timeline_html, unsafe_allow_html=True)

                # Marcas del eje
                eje_html = '<div style="display:flex;justify-content:space-between;font-size:0.5rem;color:#3a4060;margin-bottom:8px;border-top:1px solid #1a1a2a;padding-top:3px">'
                eje_html += '<span>SUPERVIVENCIA</span><span>CONCIENCIA</span><span>TRANSICIÓN</span><span>PROTAGONISMO</span><span>TRANSFORMACIÓN</span>'
                eje_html += '</div>'
                st.markdown(eje_html, unsafe_allow_html=True)

                # Temas recurrentes
                if llaves:
                    from collections import Counter
                    llave_count = Counter(llaves)
                    st.markdown("**Temas dominantes recurrentes**")
                    lc1, lc2 = st.columns(2)
                    for i, (llave, count) in enumerate(llave_count.most_common(6)):
                        col = lc1 if i%2==0 else lc2
                        with col:
                            pct = round(count/len(llaves)*100)
                            st.markdown(f'<div style="font-size:0.7rem;color:#9a9eb0;margin:3px 0">`{llave}` — {count}x ({pct}%)</div>', unsafe_allow_html=True)

                # Historial de sesiones
                st.markdown("**Historial de sesiones**")
                for i, s in enumerate(sesiones_ord):
                    sc_v = s.get("score_condiciones",0)
                    arc  = s.get("arco_detectado","estable")
                    ts   = s.get("timestamp","")[:16]
                    pf   = s.get("posicion_final","?")
                    sid  = s.get("session_id","?")[:8]
                    decl = "✓ Declaración" if s.get("declaracion_detectada") else ""
                    sc_c = "#4ac17a" if sc_v>=61 else "#c17a4a" if sc_v>=41 else "#c14a4a"
                    arc_c = ARCO_COLOR.get(arc,"#5a6280") if "ARCO_COLOR" in dir() else "#5a6280"
                    st.markdown(
                        f'<div style="background:var(--s);border:1px solid var(--b);border-radius:6px;padding:0.5rem 0.8rem;margin:0.2rem 0;display:flex;gap:1.5rem;align-items:center;font-size:0.7rem;">' +
                        f'<span style="color:#3a5080">#{i+1}</span>' +
                        f'<span style="color:{sc_c};font-weight:600">{sc_v}/100</span>' +
                        f'<span style="color:#5a6280">{eje_lbl(sc_v)}</span>' +
                        f'<span style="color:{POS_COLOR.get(pf,"#5a6280")}">{pf}</span>' +
                        f'<span style="color:#4ac17a;font-size:0.65rem">{decl}</span>' +
                        f'<span style="color:#3a4060;margin-left:auto">{ts}</span>' +
                        '</div>', unsafe_allow_html=True)

                # Última recomendación
                ultima_recom = sesiones_ord[-1].get("recomendacion","") if sesiones_ord else ""
                if ultima_recom:
                    st.markdown(f'<div style="background:#1a1a2a;border-left:3px solid #4a7fc1;border-radius:0 6px 6px 0;padding:0.7rem 1rem;margin-top:0.8rem;font-size:0.8rem;color:#9a9eb0;font-style:italic;">Proxima sesion: {ultima_recom}</div>', unsafe_allow_html=True)

elif vista == "Conversaciones":
    st.markdown("### Conversaciones — Arco de Transformación")
    st.markdown('<div style="font-size:0.7rem;color:#5a6280;margin-bottom:1rem;line-height:1.6;">Evaluación del arco completo de cada conversación. Score 0-100 según el Eje de Transformación del observador.<br>0=Supervivencia · 20=Conciencia · 40=Transición · 60=Protagonismo · 80=Transformación</div>', unsafe_allow_html=True)

    # Filtros
    cf1, cf2 = st.columns([2,1])
    with cf1: ufilt = st.text_input("Filtrar por User Code (vacio = todos)", placeholder="JAVIER-01...")
    with cf2: arco_filt = st.selectbox("Arco", ["todos","transformacion","avance","estable","regresion"])

    params = "order=timestamp.desc"
    if ufilt: params += f"&user_code=like.{ufilt}%25"
    if arco_filt != "todos": params += f"&arco_detectado=eq.{arco_filt}"
    convs = sb("evaluaciones_conversacion", params, limit=50)

    if not convs:
        st.info("No hay conversaciones evaluadas aun. Realiza una sesion completa para ver los datos.")
    else:
        st.markdown(f"**{len(convs)} conversacion(es)**")

        ARCO_COLOR = {"transformacion":"#4ac17a","avance":"#7ec17a","estable":"#5a6280","regresion":"#c14a4a"}
        POS_COLOR  = {"protagonista":"#4ac17a","mixto":"#c17a4a","victima":"#c14a4a"}

        def score_bar(score):
            pct = min(100, max(0, score))
            if pct >= 61: color = "#4ac17a"
            elif pct >= 41: color = "#c17a4a"
            elif pct >= 21: color = "#c1a44a"
            else: color = "#c14a4a"
            return f'<div style="background:#1a1a24;border-radius:4px;height:8px;margin:4px 0"><div style="background:{color};width:{pct}%;height:8px;border-radius:4px;transition:width 0.3s"></div></div>'

        def eje_label(score):
            if score >= 81: return "TRANSFORMACIÓN"
            if score >= 61: return "PROTAGONISMO"
            if score >= 41: return "TRANSICIÓN"
            if score >= 21: return "CONCIENCIA"
            return "SUPERVIVENCIA"

        for conv_idx, conv in enumerate(convs):
            score = conv.get("score_condiciones", 0)
            arco  = conv.get("arco_detectado", "estable")
            user  = conv.get("user_code", "anonimo")
            sid   = conv.get("session_id", "?")[:8]
            ts    = conv.get("timestamp", "")[:16]
            pos_i = conv.get("posicion_inicial", "?")
            pos_f = conv.get("posicion_final", "?")
            turnos= conv.get("total_turnos", 0)
            decl  = conv.get("declaracion_detectada", False)
            dictamen = conv.get("semilla_plantada", "")
            recom    = conv.get("recomendacion", "")
            llave    = conv.get("llave_maestra_dominante", "—")
            riesgo   = conv.get("nivel_riesgo_max", "ninguno")

            arco_c = ARCO_COLOR.get(arco, "#5a6280")
            pi_c   = POS_COLOR.get(pos_i, "#5a6280")
            pf_c   = POS_COLOR.get(pos_f, "#5a6280")

            titulo = f"{'👤 ' + user if user != 'anonimo' else '◎'} Sesion {sid}... · {ts} · {eje_label(score)} ({score}/100)"
            with st.expander(titulo, expanded=False):
                # Score bar
                st.markdown(score_bar(score), unsafe_allow_html=True)

                # Métricas principales
                mc1,mc2,mc3,mc4,mc5 = st.columns(5)
                with mc1:
                    st.markdown(f'<div class="nc" style="text-align:center"><div style="font-size:1.6rem;font-weight:700;color:{"#4ac17a" if score>=61 else "#c17a4a" if score>=41 else "#c14a4a"}">{score}</div><div class="nk">Score /100</div></div>', unsafe_allow_html=True)
                with mc2:
                    st.markdown(f'<div class="nc" style="text-align:center"><div style="font-size:1rem;font-weight:600;color:{arco_c}">{arco.upper()}</div><div class="nk">Arco</div></div>', unsafe_allow_html=True)
                with mc3:
                    st.markdown(f'<div class="nc" style="text-align:center"><div style="font-size:0.9rem;color:{pi_c}">{pos_i}</div><div style="font-size:0.7rem;color:#5a6280">→</div><div style="font-size:0.9rem;color:{pf_c}">{pos_f}</div><div class="nk">Posicion</div></div>', unsafe_allow_html=True)
                with mc4:
                    st.markdown(f'<div class="nc" style="text-align:center"><div style="font-size:1.4rem;font-weight:600;color:#4a7fc1">{turnos}</div><div class="nk">Turnos</div></div>', unsafe_allow_html=True)
                with mc5:
                    decl_color = "#4ac17a" if decl else "#5a6280"
                    decl_txt = "SÍ" if decl else "No"
                    st.markdown(f'<div class="nc" style="text-align:center"><div style="font-size:1.2rem;font-weight:600;color:{decl_color}">{decl_txt}</div><div class="nk">Declaración</div></div>', unsafe_allow_html=True)

                st.markdown("---")

                # Declaración si existe
                decl_texto = conv.get("declaracion_texto", "")
                if decl and decl_texto:
                    st.markdown(f'<div style="background:#1a2a1a;border-left:3px solid #4ac17a;border-radius:0 6px 6px 0;padding:0.8rem 1rem;margin:0.5rem 0;font-family:Cormorant Garamond,serif;font-size:1rem;color:#e8e4dc;font-style:italic;">"{decl_texto}"</div>', unsafe_allow_html=True)

                # Detalles
                # Session ID — link a consultar sesión (izquierda para móvil)
                full_sid = conv.get("session_id","")
                link_cols = st.columns([2, 3])
                with link_cols[0]:
                    if st.button("≡ Ver conversación", key=f"ver_{conv_idx}_{full_sid[:12]}"):
                        st.session_state["consultar_sid"] = full_sid
                        st.session_state["_nav_pending"] = "Consultar sesion"
                        st.rerun()
                with link_cols[1]:
                    st.markdown(f'<div style="font-size:0.6rem;color:#3a4060;padding-top:0.6rem;word-break:break-all">{full_sid}</div>', unsafe_allow_html=True)

                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f'<span class="nk">Llave maestra:</span> <span class="nv">{llave}</span>', unsafe_allow_html=True)
                    st.markdown(f'<span class="nk">Riesgo max:</span> <span class="nv">{riesgo}</span>', unsafe_allow_html=True)
                with col_b:
                    semilla = conv.get("semilla_plantada", "")
                    posib  = "✓" if conv.get("posibilidad_nueva") else "—"
                    creenc = conv.get("creencia_en_movimiento","no")
                    if semilla and semilla != "no":
                        st.markdown(f'<span class="nk">Semilla plantada:</span> <span class="nv">{semilla}</span>', unsafe_allow_html=True)

                # Semilla plantada
                if dictamen and dictamen not in ("no",""):
                    st.markdown("**Semilla plantada para la próxima sesión**")
                    st.markdown(f'<div class="re-box">{dictamen}</div>', unsafe_allow_html=True)

                # Recomendación
                if recom:
                    st.markdown(f'<div style="background:#1a1a2a;border-left:3px solid #4a7fc1;border-radius:0 6px 6px 0;padding:0.7rem 1rem;margin:0.4rem 0;font-size:0.8rem;color:#9a9eb0;font-style:italic;">Proxima sesion: {recom}</div>', unsafe_allow_html=True)

elif vista == "Log de Nodos":
    st.markdown("### Log de Nodos — Registro de aprendizaje")
    st.markdown('<div style="font-size:0.7rem;color:#5a6280;margin-bottom:1rem;line-height:1.6;">Cada fila es un turno completo. Muestra los reportes de todos los nodos, el dictamen del Incisor y la respuesta generada.<br>Herramienta principal para calibrar y mejorar el sistema.</div>',unsafe_allow_html=True)
    cf1,cf2=st.columns([2,1])
    with cf1: sfilt=st.text_input("Filtrar por Session ID (vacio = todas)",placeholder="xxxxxxxx...")
    with cf2: pfilt=st.selectbox("Protocolo",["todos","normal","silencio","incoherencia","vigil"])
    params="order=timestamp.desc"
    if sfilt: params+=f"&session_id=like.{sfilt}%25"
    if pfilt!="todos": params+=f"&protocolo=eq.{pfilt}"
    logs=sb("log_nodos",params,limit=50)
    if not logs:
        st.info("No hay logs. Asegurate de que el backend tiene las variables SUPABASE_URL y SUPABASE_KEY configuradas.")
    else:
        st.markdown(f"**{len(logs)} turno(s)**")
        for log in logs:
            sid=log.get("session_id","?")[:8]; turno=log.get("turno","?")
            ts=log.get("timestamp","")[:16]; proto=log.get("protocolo","normal")
            delta=log.get("delta_observador","estable"); riesgo=log.get("nivel_riesgo","ninguno")
            titulo=f"Sesion {sid}... · Turno {turno} · {ts} · {proto}"
            with st.expander(titulo, expanded=False):
                st.markdown(f'<div class="ui-box">{log.get("user_input","")}</div>',unsafe_allow_html=True)
                b=badge(proto,PC.get(proto,"#5a6280"))+" "+badge(delta,DC.get(delta,"#5a6280"))
                if riesgo not in ("ninguno",""): b+=" "+badge(f"riesgo:{riesgo}","#c14a4a")
                st.markdown(b,unsafe_allow_html=True)
                st.markdown("---")
                st.markdown("**Nodos detectores**")
                c1,c2=st.columns(2)
                with c1:
                    actos=pj(log.get("reporte_actos"))
                    st.markdown('<div class="nc"><div class="nt">ACTOS LINGUISTICOS</div>',unsafe_allow_html=True)
                    if actos:
                        conf=actos.get("confianza",0)
                        st.markdown(f'<span class="nk">Acto:</span> <span class="nv">{actos.get("acto_dominante","—")}</span><br>'
                                   f'<span class="nk">Alerta:</span> <span class="nv">{"SI" if actos.get("alerta") else "No"} — {actos.get("tipo_alerta","—")}</span><br>'
                                   f'<span class="nk">Confianza:</span> <span style="color:{cc(conf)}">{conf}</span><br>'
                                   f'<span class="nk">Obs:</span> <span class="nv" style="font-style:italic;font-size:0.75rem">{actos.get("observacion","—")}</span>',unsafe_allow_html=True)
                    st.markdown('</div>',unsafe_allow_html=True)
                with c2:
                    juicios=pj(log.get("reporte_juicios"))
                    st.markdown('<div class="nc"><div class="nt">JUICIOS Y AFIRMACIONES</div>',unsafe_allow_html=True)
                    if juicios:
                        conf=juicios.get("confianza",0)
                        st.markdown(f'<span class="nk">Tipo:</span> <span class="nv">{juicios.get("tipo_enunciado","—")}</span><br>'
                                   f'<span class="nk">Juicio maestro:</span> <span class="nv">{"SI" if juicios.get("juicio_maestro_detectado") else "No"}</span><br>'
                                   f'<span class="nk">Fragmento:</span> <span class="nv" style="font-style:italic">{juicios.get("fragmento_juicio","—")}</span><br>'
                                   f'<span class="nk">Confianza:</span> <span style="color:{cc(conf)}">{conf}</span>',unsafe_allow_html=True)
                    st.markdown('</div>',unsafe_allow_html=True)
                c3,c4=st.columns(2)
                with c3:
                    q=pj(log.get("reporte_quiebre"))
                    st.markdown('<div class="nc"><div class="nt">QUIEBRE ONTOLOGICO</div>',unsafe_allow_html=True)
                    if q:
                        conf=q.get("confianza",0)
                        st.markdown(f'<span class="nk">Tipo:</span> <span class="nv">{q.get("tipo_quiebre","—")}</span><br>'
                                   f'<span class="nk">Intensidad:</span> <span class="nv">{q.get("intensidad","—")}</span><br>'
                                   f'<span class="nk">Dominio:</span> <span class="nv">{q.get("dominio_afectado","—")}</span><br>'
                                   f'<span class="nk">OSAR:</span> <span class="nv">{q.get("osar_afectado","—")}</span><br>'
                                   f'<span class="nk">Confianza:</span> <span style="color:{cc(conf)}">{conf}</span>',unsafe_allow_html=True)
                    st.markdown('</div>',unsafe_allow_html=True)
                with c4:
                    v=pj(log.get("reporte_victima"))
                    st.markdown('<div class="nc"><div class="nt">PROTAGONISMO / VICTIMA</div>',unsafe_allow_html=True)
                    if v:
                        conf=v.get("confianza",0); pos=v.get("posicion","—")
                        tv=", ".join(v.get("tokens_victima",[]) or [])
                        st.markdown(f'<span class="nk">Posicion:</span> <span style="color:{POSC.get(pos,"#5a6280")};font-weight:500">{pos}</span><br>'
                                   f'<span class="nk">Autoridad ont.:</span> <span class="nv">{v.get("autoridad_ontologica","—")}</span><br>'
                                   f'<span class="nk">Tokens victima:</span> <span class="nv">{tv}</span><br>'
                                   f'<span class="nk">Confianza:</span> <span style="color:{cc(conf)}">{conf}</span>',unsafe_allow_html=True)
                    st.markdown('</div>',unsafe_allow_html=True)
                st.markdown("**Dictamen [DISTINCIONES]**")
                d=pj(log.get("dictamen"))
                if d:
                    lm=d.get("llave_maestra","—")
                    st.markdown(f'<div class="nc"><div class="nt" style="color:#c8a97e;">LLAVE MAESTRA: {lm}</div>'
                               f'<span class="nk">Inquietud real:</span><br><span class="nv">{d.get("inquietud_real","—")}</span><br><br>'
                               f'<span class="nk">Contradiccion central:</span><br><span class="nv">{d.get("contradiccion_central","—")}</span><br><br>'
                               f'<span class="nk">Punto ciego:</span><br><span class="nv">{d.get("punto_ciego","—")}</span><br><br>'
                               f'<span class="nk">Zarpazo:</span><br><span class="nv" style="font-style:italic">{d.get("zarpazo","—")}</span><br><br>'
                               f'<span class="nk">Pregunta 2 orden:</span><br><span class="nv" style="color:#c8a97e;font-size:1rem">{d.get("pregunta_segundo_orden","—")}</span>'
                               f'</div>',unsafe_allow_html=True)
                st.markdown("**Respuesta generada**")
                st.markdown(f'<div class="re-box">{log.get("respuesta","")}</div>',unsafe_allow_html=True)

                # Evaluador de Condiciones de Transformación
                ev = pj(log.get("evaluacion"))
                if ev:
                    score = ev.get("score_total", 0)
                    score_color = "#4ac17a" if score >= 55 else "#c17a4a" if score >= 35 else "#c14a4a"
                    st.markdown("**Evaluación — Condiciones de Transformación**")
                    # Fila 1: 4 dimensiones principales
                    ec1,ec2,ec3,ec4 = st.columns(4)
                    row1 = [
                        (ec1, "Apertura Posib.", ev.get("apertura_posibilidad",0), 15),
                        (ec2, "Escucha Activa",  ev.get("escucha_activa",0),       15),
                        (ec3, "Emoción Indic.",  ev.get("emocion_indicador",0),    10),
                        (ec4, "Incomodidad",     ev.get("incomodidad_calibrada",0),10),
                    ]
                    for col, label, val, max_v in row1:
                        pct = val/max_v if max_v > 0 else 0
                        col_c = "#4ac17a" if pct>=0.7 else "#c17a4a" if pct>=0.4 else "#c14a4a"
                        with col:
                            st.markdown(f'<div class="nc" style="text-align:center"><div style="font-size:1.3rem;font-weight:600;color:{col_c}">{val}<span style="font-size:0.55rem;color:#5a6280">/{max_v}</span></div><div class="nk" style="font-size:0.52rem">{label}</div></div>', unsafe_allow_html=True)
                    # Fila 2: 3 dimensiones + score total
                    ec5,ec6,ec7,ec8 = st.columns(4)
                    row2 = [
                        (ec5, "Lenguaje Devuelto", ev.get("lenguaje_devuelto",0),    10),
                        (ec6, "Acompañamiento",    ev.get("acompañamiento",0),        10),
                        (ec7, "Compromiso Emerg.", ev.get("compromiso_emergente",0),  5),
                        (ec8, "SCORE /75",         score,                            75),
                    ]
                    for col, label, val, max_v in row2:
                        pct = val/max_v if max_v > 0 else 0
                        col_c = "#4ac17a" if pct>=0.7 else "#c17a4a" if pct>=0.4 else "#c14a4a"
                        with col:
                            st.markdown(f'<div class="nc" style="text-align:center"><div style="font-size:1.3rem;font-weight:600;color:{col_c}">{val}<span style="font-size:0.55rem;color:#5a6280">/{max_v}</span></div><div class="nk" style="font-size:0.52rem">{label}</div></div>', unsafe_allow_html=True)
                    # Penalizaciones activas
                    badges_extra = []
                    if ev.get("lenguaje_manual"):       badges_extra.append('<span style="color:#c14a4a;font-size:0.6rem;padding:2px 6px;border:1px solid #c14a4a;border-radius:10px;">-20 Advisory</span>')
                    if ev.get("arrogancia_intelectual"):badges_extra.append('<span style="color:#c14a4a;font-size:0.6rem;padding:2px 6px;border:1px solid #c14a4a;border-radius:10px;">-20 Arrogancia</span>')
                    if ev.get("emocion_juzgada"):       badges_extra.append('<span style="color:#c17a4a;font-size:0.6rem;padding:2px 6px;border:1px solid #c17a4a;border-radius:10px;">-10 Emoción Juzgada</span>')
                    if ev.get("cierre_prematuro"):      badges_extra.append('<span style="color:#c17a4a;font-size:0.6rem;padding:2px 6px;border:1px solid #c17a4a;border-radius:10px;">-15 Cierre Prematuro</span>')
                    if badges_extra:
                        st.markdown(" ".join(badges_extra), unsafe_allow_html=True)
                    nota = ev.get("nota_evaluador","")
                    if nota:
                        st.markdown(f'<div style="font-size:0.75rem;color:#7a7a84;font-style:italic;margin-top:0.3rem;">{nota}</div>', unsafe_allow_html=True)


elif vista == "Etiquetado DPO":
    st.markdown("### Etiquetado DPO — Dataset de Preferencia")
    st.markdown('<div style="font-size:0.7rem;color:#5a6280;margin-bottom:1rem;line-height:1.6;">Captura pares de preferencia para fine-tuning. Selecciona un turno del Log de Nodos, revisa la respuesta generada y escribe la corrección ideal.</div>', unsafe_allow_html=True)

    # Métricas del dataset
    pares = sb("pares_dpo", "order=created_at.desc", limit=500)
    total   = len(pares)
    validados = sum(1 for p in pares if p.get("validado"))
    por_cat = {}
    for p in pares:
        cat = p.get("categoria","general")
        por_cat[cat] = por_cat.get(cat,0) + 1

    dm1,dm2,dm3,dm4 = st.columns(4)
    with dm1: st.markdown(f'<div class="nc" style="text-align:center"><div style="font-size:1.6rem;font-weight:600;color:#4a7fc1">{total}</div><div class="nk">Pares totales</div></div>', unsafe_allow_html=True)
    with dm2: st.markdown(f'<div class="nc" style="text-align:center"><div style="font-size:1.6rem;font-weight:600;color:#4ac17a">{validados}</div><div class="nk">Validados</div></div>', unsafe_allow_html=True)
    with dm3: st.markdown(f'<div class="nc" style="text-align:center"><div style="font-size:1.6rem;font-weight:600;color:#c17a4a">{total-validados}</div><div class="nk">Pendientes</div></div>', unsafe_allow_html=True)
    with dm4:
        objetivo = 200
        pct = min(100, round(validados/objetivo*100))
        color = "#4ac17a" if pct >= 80 else "#c17a4a" if pct >= 40 else "#c14a4a"
        st.markdown(f'<div class="nc" style="text-align:center"><div style="font-size:1.6rem;font-weight:600;color:{color}">{pct}%</div><div class="nk">Objetivo 200</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # Formulario de etiquetado
    st.markdown("#### Nuevo par DPO")
    with st.form("form_dpo", clear_on_submit=True):
        # Session ID con auto-carga
        dpo_session = st.text_input("Session ID completo", placeholder="Pega el session_id y pulsa Enter para cargar datos automaticamente...")

        auto_ui, auto_rej, auto_llave, auto_turno, auto_score = "", "", "", 1, 0
        if dpo_session and len(dpo_session) > 10:
            logs_s = sb("log_nodos", f"session_id=eq.{dpo_session}&order=turno.desc", limit=20)
            if logs_s:
                st.success(f"Sesion encontrada — {len(logs_s)} turno(s)")
                turno_opts = [l.get("turno",1) for l in logs_s]
                turno_sel = st.selectbox("Seleccionar turno", options=turno_opts, format_func=lambda t: f"Turno {t}")
                log_s = next((l for l in logs_s if l.get("turno")==turno_sel), logs_s[0])
                auto_ui    = log_s.get("user_input","")
                auto_rej   = log_s.get("respuesta","")
                auto_llave = pj(log_s.get("dictamen",{})).get("llave_maestra","")
                auto_turno = turno_sel
                auto_score = pj(log_s.get("evaluacion",{})).get("score_total",0)
                st.markdown(f"**Llave:** {auto_llave} · **Score rechazada:** {auto_score}/75")
            elif dpo_session:
                st.warning("Sesion no encontrada. Verifica el ID completo.")

        fc1, fc2 = st.columns(2)
        with fc1:
            dpo_turno  = st.number_input("Turno", min_value=1, value=auto_turno)
            dpo_perfil = st.selectbox("Perfil detectado", ["dolor_agudo","juez_control","victima_estancada","orgullo_herida","reflexivo","general"])
        with fc2:
            dpo_llave     = st.text_input("Llave maestra", value=auto_llave, placeholder="ej: Generalizacion")
            dpo_categoria = st.selectbox("Categoria", ["dolor_agudo","juez","victima","orgullo","general"])
            dpo_supervisor = st.text_input("Supervisor", value="admin")

        dpo_user_input = st.text_area("Mensaje del usuario", value=auto_ui, height=80)
        dpo_rejected   = st.text_area("Respuesta RECHAZADA (generada por ONTOMIND)", value=auto_rej, height=120)
        dpo_chosen     = st.text_area("Respuesta ELEGIDA (correccion ideal)", height=120, placeholder="Escribe la respuesta correcta...")
        dpo_notas      = st.text_area("Notas del supervisor", height=60, placeholder="Por qué se rechazó y qué aporta la corrección...")
        dpo_score      = st.slider("Score de la respuesta rechazada", 0, 75, auto_score)

        submitted = st.form_submit_button("Guardar par DPO", type="primary")
        if submitted:
            if not dpo_user_input or not dpo_rejected or not dpo_chosen:
                st.error("Los campos User Input, Respuesta Rechazada y Respuesta Elegida son obligatorios.")
            else:
                payload = {
                    "session_id": dpo_session, "turno": dpo_turno,
                    "user_input": dpo_user_input, "perfil_detectado": dpo_perfil,
                    "llave_maestra": dpo_llave, "categoria": dpo_categoria,
                    "respuesta_rejected": dpo_rejected, "respuesta_chosen": dpo_chosen,
                    "supervisor": dpo_supervisor, "score_rejected": dpo_score,
                    "notas": dpo_notas
                }
                try:
                    r = httpx.post(f"{API_URL}/admin/dpo/guardar", json=payload, timeout=15)
                    if r.status_code == 200 and r.json().get("ok"):
                        st.success(f"✓ Par DPO guardado correctamente.")
                    else:
                        st.error(f"Error: {r.text[:100]}")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")

    st.markdown("---")

    # Lista de pares existentes
    if pares:
        st.markdown(f"#### Pares guardados ({total})")
        filtro_cat = st.selectbox("Filtrar por categoría", ["todos"] + list(por_cat.keys()), key="dpo_cat_filter")
        filtro_val = st.selectbox("Filtrar por estado", ["todos","validados","pendientes"], key="dpo_val_filter")

        pares_filtrados = pares
        if filtro_cat != "todos":
            pares_filtrados = [p for p in pares_filtrados if p.get("categoria") == filtro_cat]
        if filtro_val == "validados":
            pares_filtrados = [p for p in pares_filtrados if p.get("validado")]
        elif filtro_val == "pendientes":
            pares_filtrados = [p for p in pares_filtrados if not p.get("validado")]

        for par in pares_filtrados[:30]:
            pid      = par.get("id","")
            cat      = par.get("categoria","general")
            perfil   = par.get("perfil_detectado","")
            ts       = par.get("created_at","")[:16]
            val      = par.get("validado", False)
            score_r  = par.get("score_rejected", 0)
            sup      = par.get("supervisor","admin")
            val_badge = '<span style="color:#4ac17a;font-size:0.6rem;padding:2px 6px;border:1px solid #4ac17a;border-radius:8px">✓ Validado</span>' if val else '<span style="color:#c17a4a;font-size:0.6rem;padding:2px 6px;border:1px solid #c17a4a;border-radius:8px">⏳ Pendiente</span>'

            with st.expander(f"#{pid} · {cat} · {ts} · score_rejected: {score_r}/75 {'✓' if val else ''}", expanded=False):
                st.markdown(f'<div style="margin-bottom:0.5rem">{val_badge} <span style="font-size:0.65rem;color:#5a6280">Perfil: {perfil} · Supervisor: {sup}</span></div>', unsafe_allow_html=True)

                st.markdown("**Usuario dijo:**")
                st.markdown(f'<div class="re-box" style="font-size:0.8rem">{par.get("user_input","")}</div>', unsafe_allow_html=True)

                rc1, rc2 = st.columns(2)
                with rc1:
                    st.markdown('<div style="color:#c14a4a;font-size:0.7rem;font-weight:600;margin-bottom:0.3rem">✗ RECHAZADA (generada)</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="re-box" style="border-left:3px solid #c14a4a;font-size:0.8rem">{par.get("respuesta_rejected","")}</div>', unsafe_allow_html=True)
                with rc2:
                    st.markdown('<div style="color:#4ac17a;font-size:0.7rem;font-weight:600;margin-bottom:0.3rem">✓ ELEGIDA (corrección)</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="re-box" style="border-left:3px solid #4ac17a;font-size:0.8rem">{par.get("respuesta_chosen","")}</div>', unsafe_allow_html=True)

                if par.get("notas"):
                    st.markdown(f'<div style="font-size:0.7rem;color:#7a7a84;font-style:italic;margin-top:0.5rem">Notas: {par["notas"]}</div>', unsafe_allow_html=True)

        # Botón exportar dataset
        st.markdown("---")
        if st.button("Exportar dataset DPO (JSON)", type="secondary"):
            import json as _json
            dataset = []
            for p in pares:
                if p.get("validado") or True:  # exportar todos por ahora
                    dataset.append({
                        "prompt": p.get("user_input",""),
                        "chosen": p.get("respuesta_chosen",""),
                        "rejected": p.get("respuesta_rejected",""),
                        "categoria": p.get("categoria","general"),
                        "perfil": p.get("perfil_detectado",""),
                    })
            st.download_button(
                "⬇ Descargar dataset_dpo.json",
                data=_json.dumps(dataset, ensure_ascii=False, indent=2),
                file_name="dataset_dpo.json",
                mime="application/json"
            )

elif vista == "Alertas VIGIL":
    st.markdown("### Alertas VIGIL")
    mostrar=st.radio("",["Sin revisar","Todas"],horizontal=True)
    params="revisado=eq.false&order=timestamp.desc" if mostrar=="Sin revisar" else "order=timestamp.desc"
    alertas=sb("alertas_vigil",params,limit=50)
    if not alertas:
        st.success("No hay alertas pendientes.")
    else:
        for a in alertas:
            nc={"critico":"#c14a4a","alto":"#c17a4a","latente":"#c1c14a"}.get(a.get("nivel",""),"#5a6280")
            c1,c2=st.columns([5,1])
            with c1:
                st.markdown(f'<div class="ac"><div style="font-size:0.6rem;color:#5a6280;">{a.get("session_id","?")[:16]}... · {a.get("timestamp","")[:16]}</div>'
                           f'<div style="font-size:0.55rem;padding:2px 8px;border-radius:20px;display:inline-block;margin:0.3rem 0;color:{nc};border:1px solid {nc};background:#1a0f0f;">{a.get("nivel","?").upper()}</div>'
                           f'<div style="font-family:Cormorant Garamond,serif;font-size:1rem;color:#e8e4dc;">{a.get("mensaje","")}</div></div>',unsafe_allow_html=True)
            with c2:
                st.markdown("<div style='height:35px'></div>",unsafe_allow_html=True)
                if not a.get("revisado") and st.button("Revisado",key=f"r_{a.get('id')}"):
                    httpx.patch(f"{SUPABASE_URL.strip()}/rest/v1/alertas_vigil?id=eq.{a.get('id')}",
                        headers={"apikey":SUPABASE_KEY.strip(),"Authorization":f"Bearer {SUPABASE_KEY.strip()}","Content-Type":"application/json"},
                        json={"revisado":True},timeout=10)
                    st.rerun()


elif vista == "Sesiones":
    st.markdown("### Mapa del Observador — Últimas sesiones")
    total_s = sb_count("mapa_observador")
    mapas=sb("mapa_observador","order=updated_at.desc",limit=200)
    if not mapas:
        st.info("No hay sesiones aun.")
    else:
        count_lbl = f"{total_s} sesion(es) totales" if total_s else f"{len(mapas)} sesion(es)"
        st.markdown(f'<div style="font-size:0.7rem;color:#4a7fc1;margin-bottom:0.8rem">{count_lbl} · mostrando las 200 más recientes</div>', unsafe_allow_html=True)
        for ses_idx, m in enumerate(mapas):
            sid_full = m.get("session_id","")
            pos = m.get("ultima_posicion","desconocido")
            pc  = POSC.get(pos,"#8a9ab0")
            ancora = "ANCORA" if m.get("ancora_activado") else ""
            quiebre = m.get("ultimo_quiebre","—") or "—"
            ts = m.get("updated_at","")[:16]
            sr, sl = st.columns([5, 1])
            with sr:
                st.markdown(
                    f'<div style="background:var(--s);border:1px solid var(--b);border-radius:6px;padding:0.55rem 1rem;margin:0.2rem 0;display:flex;gap:1.5rem;align-items:center;font-size:0.7rem;">'
                    f'<span style="color:#6a7aaa;font-family:DM Mono,monospace">{sid_full[:12]}…</span>'
                    f'<span style="color:{pc};font-weight:600">{pos}</span>'
                    f'<span style="color:#7a8090">{quiebre}</span>'
                    f'{"<span style=\"color:#c14a4a\">ANCORA</span>" if ancora else ""}'
                    f'<span style="color:#5a6280;margin-left:auto">{ts}</span>'
                    f'</div>', unsafe_allow_html=True)
            with sl:
                if st.button("≡", key=f"ses_{ses_idx}_{sid_full[:12]}", help="Ver conversación"):
                    st.session_state["consultar_sid"] = sid_full
                    st.session_state["_nav_pending"] = "Consultar sesion"
                    st.rerun()


elif vista == "Consultar sesion":
    # Autorellenar desde botón "Ver conversación"
    st.markdown("### Consultar sesión específica")
    default_sid = st.session_state.get("consultar_sid", "")
    sid = st.text_input("Session ID", value=default_sid,
                        placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
    if sid:
        st.session_state["consultar_sid"] = sid

    if sid and len(sid) > 8:
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("**Mapa del Observador**")
            try:
                r = httpx.get(f"{API_URL}/sesion/{sid}/mapa", timeout=10)
                if r.status_code == 200:
                    st.json(r.json().get("mapa", {}))
            except Exception as e:
                st.error(str(e))
        with c2:
            st.markdown("**Historial de conversación**")
            mensajes = []
            # Primero intentar Redis vía API
            try:
                r = httpx.get(f"{API_URL}/sesion/{sid}/historial", timeout=10)
                if r.status_code == 200:
                    mensajes = r.json().get("mensajes", [])
            except:
                pass

            # Fallback: reconstruir desde log_nodos en Supabase
            if not mensajes:
                try:
                    logs_hist = sb("log_nodos",
                                   f"session_id=eq.{sid}&order=turno.asc", limit=60)
                    for log in logs_hist:
                        ui = log.get("user_input", "")
                        re = log.get("respuesta", "")
                        if ui:
                            mensajes.append({"rol": "user",    "contenido": ui})
                        if re:
                            mensajes.append({"rol": "agent",   "contenido": re})
                except:
                    pass

            if mensajes:
                for msg in mensajes:
                    rol = msg.get("rol", "")
                    contenido = msg.get("contenido", "")
                    if rol == "user":
                        st.markdown(
                            f'<div class="ui-box"><span style="font-size:0.6rem;color:#5a6280;display:block;margin-bottom:0.3rem">TÚ</span>{contenido}</div>',
                            unsafe_allow_html=True)
                    else:
                        st.markdown(
                            f'<div class="re-box"><span style="font-size:0.6rem;color:#4a7fc1;display:block;margin-bottom:0.3rem">ONTOMIND</span>{contenido}</div>',
                            unsafe_allow_html=True)
            else:
                st.info("Historial no disponible — la sesión puede haber expirado de Redis y no tiene turnos en log_nodos.")

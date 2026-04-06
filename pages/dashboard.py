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
    # Usar el backend como proxy — Railway bloquea conexiones directas a Supabase desde el frontend
    try:
        url = f"{API_URL}/admin/tabla/{tabla}?limit={limit}"
        if params:
            import urllib.parse
            url += "&params=" + urllib.parse.quote(params)
        r = httpx.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            # Asegurar que siempre devolvemos lista de dicts
            if isinstance(data, list):
                return [item if isinstance(item, dict) else {} for item in data]
            return []
        return []
    except Exception as e:
        st.error(f"Error cargando {tabla}: {e}")
        return []

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
    vista = st.radio("Vista", ["Resumen","Log de Nodos","Alertas VIGIL","Sesiones","Consultar sesion"],
                     label_visibility="collapsed")
    st.markdown("---")
    if st.button("Actualizar"): st.rerun()
    ok=api_ok()
    st.markdown(f'<div style="margin-top:1.5rem;font-size:0.55rem;color:#3a4060;">API: {"● ACTIVA" if ok else "● INACTIVA"}</div>',unsafe_allow_html=True)

st.markdown('<div style="font-size:0.7rem;letter-spacing:0.3em;text-transform:uppercase;color:#4a7fc1;margin-bottom:0.2rem;">Panel de Supervision</div>',unsafe_allow_html=True)
st.markdown('<div style="font-family:Cormorant Garamond,serif;font-size:1.6rem;color:#cdd3e0;margin-bottom:1.5rem;">ONTOMIND · Monitor Ontologico</div>',unsafe_allow_html=True)


if vista == "Resumen":
    mapas=sb("mapa_observador","order=updated_at.desc")
    alertas=sb("alertas_vigil","revisado=eq.false")
    logs=sb("log_nodos","order=timestamp.desc",limit=500)
    protags=[m for m in mapas if m.get("ultima_posicion")=="protagonista"]
    ancoras=[m for m in mapas if m.get("ancora_activado")]
    c1,c2,c3,c4=st.columns(4)
    for col,val,lbl,color in [(c1,len(mapas),"Sesiones","#4a7fc1"),(c2,len(alertas),"Alertas VIGIL","#c14a4a"),
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
        with cb:
            for lm,n in sorted(llaves.items(),key=lambda x:-x[1])[:6]: st.markdown(f'`{lm}` — {n}x')
    else:
        st.info("Aun no hay sesiones. Los datos apareceran cuando los usuarios interactuen con ONTOMIND.")


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
    st.markdown("### Mapa del Observador")
    mapas=sb("mapa_observador","order=updated_at.desc",limit=100)
    if not mapas:
        st.info("No hay sesiones aun.")
    else:
        st.markdown(f"**{len(mapas)} sesion(es)**")
        for m in mapas:
            pos=m.get("ultima_posicion","desconocido"); pc=POSC.get(pos,"#5a6280")
            ancora="ANCORA" if m.get("ancora_activado") else ""
            st.markdown(f'<div style="background:var(--s);border:1px solid var(--b);border-radius:6px;padding:0.6rem 1rem;margin:0.3rem 0;display:flex;gap:2rem;font-size:0.7rem;">'
                       f'<span style="color:#3a5080">{m.get("session_id","")[:12]}...</span>'
                       f'<span style="color:{pc};font-weight:500">{pos}</span>'
                       f'<span style="color:#5a6280">{m.get("ultimo_quiebre","—")}</span>'
                       f'<span style="color:#c14a4a">{ancora}</span>'
                       f'<span style="color:#3a4060;margin-left:auto">{m.get("updated_at","")[:16]}</span></div>',unsafe_allow_html=True)


elif vista == "Consultar sesion":
    st.markdown("### Consultar sesion especifica")
    sid=st.text_input("Session ID",placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
    if sid and len(sid)>8:
        c1,c2=st.columns(2)
        with c1:
            st.markdown("**Mapa del Observador**")
            try:
                r=httpx.get(f"{API_URL}/sesion/{sid}/mapa",timeout=10)
                if r.status_code==200: st.json(r.json().get("mapa",{}))
            except Exception as e: st.error(str(e))
        with c2:
            st.markdown("**Historial**")
            try:
                r=httpx.get(f"{API_URL}/sesion/{sid}/historial",timeout=10)
                if r.status_code==200:
                    for msg in r.json().get("mensajes",[]):
                        st.markdown(f"**{'Tu' if msg['rol']=='user' else 'ONTOMIND'}:** {msg['contenido']}")
                        st.markdown("---")
            except Exception as e: st.error(str(e))

"""
app.py - ONTOMIND v3 - botones corregidos, tooltip, contraste mejorado
"""
import streamlit as st
import httpx
import uuid
import os

API_URL = os.getenv("ONTOMIND_API_URL", "https://ontomind-production.up.railway.app")

st.set_page_config(page_title="ONTOMIND", page_icon="\u25c8",
    layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500&family=DM+Mono:wght@300;400&display=swap');
:root{--bg:#0e0e10;--surface:#16161a;--border:#2a2a32;--accent:#c8a97e;--accent2:#7e9cc8;--text:#f0ece4;--dim:#8a8580;}
html,body,[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:var(--text)!important;}
[data-testid="stHeader"]{display:none;}
.oh{text-align:center;padding:2rem 0 1rem;border-bottom:1px solid var(--border);margin-bottom:1.5rem;}
.ot{font-family:'Cormorant Garamond',serif;font-size:2.8rem;font-weight:400;letter-spacing:.35em;color:var(--accent);margin:0;}
.os{font-family:'DM Mono',monospace;font-size:.65rem;letter-spacing:.2em;color:var(--dim);margin-top:.4rem;text-transform:uppercase;}
.si{font-family:'DM Mono',monospace;font-size:.55rem;color:var(--dim);text-align:center;letter-spacing:.1em;margin-bottom:1rem;}
.mc{margin:.9rem 0;animation:fi .35s ease;}
@keyframes fi{from{opacity:0;transform:translateY(5px)}to{opacity:1}}
.ml{font-family:'DM Mono',monospace;font-size:.6rem;letter-spacing:.15em;text-transform:uppercase;color:var(--dim);margin-bottom:.4rem;}
.mla{color:var(--accent);}
.mu{background:#1c1c24;border-left:2px solid var(--accent2);padding:.9rem 1.3rem;border-radius:0 6px 6px 0;font-family:'Cormorant Garamond',serif;font-size:1.2rem;line-height:1.65;color:#f0ece4;}
.ma{background:#141418;border-left:2px solid var(--accent);padding:1.1rem 1.5rem;border-radius:0 6px 6px 0;font-family:'Cormorant Garamond',serif;font-size:1.25rem;line-height:1.9;color:#f5f1ea;}
.pb{display:inline-block;font-family:'DM Mono',monospace;font-size:.5rem;padding:2px 6px;border-radius:20px;margin-left:.4rem;text-transform:uppercase;}
.pn{background:#1a2a1a;color:#6a9a6a;border:1px solid #2a4a2a;}
.ps{background:#1a1a2a;color:#6a6a9a;border:1px solid #2a2a4a;}
.pi{background:#2a1a0a;color:#9a7a4a;border:1px solid #4a2a1a;}
.pv{background:#2a0f0f;color:#c85a5a;border:1px solid #5a1a1a;}
.stTextArea textarea{background:var(--surface)!important;border:1px solid var(--border)!important;border-radius:8px!important;color:#f0ece4!important;font-family:'Cormorant Garamond',serif!important;font-size:1.05rem!important;resize:none!important;}
.stTextArea textarea:focus{border-color:var(--accent)!important;box-shadow:0 0 0 1px var(--accent)!important;}
.stTextArea textarea::placeholder{color:#4a4a54!important;}
div[data-testid="stButton"] button{background:transparent!important;border:1px solid var(--accent)!important;color:var(--accent)!important;font-family:'DM Mono',monospace!important;font-size:.68rem!important;letter-spacing:.08em!important;text-transform:uppercase!important;padding:.5rem .4rem!important;border-radius:4px!important;white-space:nowrap!important;width:100%!important;}
div[data-testid="stButton"] button:hover{background:var(--accent)!important;color:#0e0e10!important;}
.ns-wrap{position:relative;width:100%;margin-top:6px;}
.ns-btn{width:100%;padding:.5rem .4rem;background:transparent;border:1px solid #363640;color:#7a7a84;font-family:'DM Mono',monospace;font-size:.68rem;letter-spacing:.08em;text-transform:uppercase;border-radius:4px;cursor:default;white-space:nowrap;}
.ns-tip{display:none;position:absolute;bottom:calc(100% + 8px);right:0;width:230px;background:#1e1e28;border:1px solid var(--border);border-radius:8px;padding:1rem 1.1rem;z-index:999;font-family:'DM Mono',monospace;font-size:.62rem;line-height:1.75;color:#9a9690;box-shadow:0 8px 28px rgba(0,0,0,.6);}
.ns-tip b{color:#c8a97e;}
.ns-tip::after{content:'';position:absolute;bottom:-6px;right:18px;width:10px;height:10px;background:#1e1e28;border-right:1px solid var(--border);border-bottom:1px solid var(--border);transform:rotate(45deg);}
.ns-wrap:hover .ns-tip{display:block;}
div[data-testid="stButton"]:last-child button{border-color:#363640!important;color:#7a7a84!important;font-size:.68rem!important;}
div[data-testid="stButton"]:last-child button:hover{background:#363640!important;color:#f0ece4!important;}
</style>""", unsafe_allow_html=True)

for k,v in [("session_id",None),("mensajes",[]),("turno",0),("input_key",0),("user_code","")]:
    if k not in st.session_state: st.session_state[k]=v

def nueva_sesion():
    try:
        r=httpx.post(f"{API_URL}/sesion/nueva",timeout=10)
        return r.json().get("session_id")
    except: return str(uuid.uuid4())

def chat(session_id,msg,user_code="anonimo"):
    try:
        r=httpx.post(f"{API_URL}/chat",json={"session_id":session_id,"mensaje":msg,"user_code":user_code or "anonimo"},timeout=120)
        return r.json() if r.status_code==200 else {"respuesta":"Error de conexion.","protocolo":"error"}
    except Exception as e: return {"respuesta":f"Error: {e}","protocolo":"error"}

def badge(p):
    m={"normal":"pn","silencio":"ps","incoherencia":"pi","vigil":"pv"}
    return f'<span class="pb {m.get(p,"pn")}">{p}</span>'

# User code input in sidebar
with st.sidebar:
    st.markdown('<div style="font-family:DM Mono,monospace;font-size:0.6rem;letter-spacing:0.15em;text-transform:uppercase;color:#c8a97e;margin-bottom:0.5rem;">Codigo de usuario</div>', unsafe_allow_html=True)
    user_code_input = st.text_input("codigo", label_visibility="collapsed",
        placeholder="ej: JAVIER-01",
        value=st.session_state.user_code,
        key="user_code_input")
    if user_code_input != st.session_state.user_code:
        st.session_state.user_code = user_code_input.strip().upper()
    if st.session_state.user_code:
        st.markdown(f'<div style="font-size:0.6rem;color:#4ac17a;margin-top:0.3rem;">● {st.session_state.user_code}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size:0.6rem;color:#7a7570;margin-top:0.3rem;">Sin identificar</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div style="font-size:0.55rem;color:#5a5550;line-height:1.5;">El codigo te permite que ONTOMIND recuerde tu historial entre sesiones.</div>', unsafe_allow_html=True)

if not st.session_state.session_id:
    st.session_state.session_id=nueva_sesion()

st.markdown('<div class="oh"><h1 class="ot">ONTOMIND</h1><p class="os">Coaching Ontologico</p></div>',unsafe_allow_html=True)
st.markdown(f'<div class="si">sesion {st.session_state.session_id[:8]}... · turno {st.session_state.turno}</div>',unsafe_allow_html=True)

if not st.session_state.mensajes:
    st.markdown('<div style="text-align:center;padding:3rem 2rem;"><div style="font-size:2rem;color:#3a3a42;margin-bottom:1rem;">\u25c8</div><div style="font-family:Cormorant Garamond,serif;font-size:1.25rem;color:#6a6560;">\u00bfQue esta ocurriendo en tu vida que te trae aqui hoy?</div></div>',unsafe_allow_html=True)
else:
    for msg in st.session_state.mensajes:
        if msg["rol"]=="user":
            st.markdown(f'<div class="mc"><div class="ml">Tu</div><div class="mu">{msg["contenido"]}</div></div>',unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="mc"><div class="ml mla">ONTOMIND {badge(msg.get("protocolo","normal"))}</div><div class="ma">{msg["contenido"]}</div></div>',unsafe_allow_html=True)

st.markdown("<div style='height:175px'></div>",unsafe_allow_html=True)

c1,c2=st.columns([5,1])
with c1:
    mensaje=st.text_area("m",label_visibility="collapsed",placeholder="Escribe lo que quieras compartir...",height=90,key=f"i_{st.session_state.input_key}")
with c2:
    st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
    enviar=st.button("Enviar",use_container_width=True)
    st.markdown("""
    <div class="ns-wrap">
      <div class="ns-btn">Nueva sesion</div>
      <div class="ns-tip">
        <b>Nueva Sesion</b><br><br>
        Borra el historial visible y abre una conversacion desde cero.<br><br>
        Usalo para cambiar de tema o empezar sin contexto previo.<br><br>
        <span style="color:#6a6560;">La sesion anterior no se pierde en el sistema.</span>
      </div>
    </div>""",unsafe_allow_html=True)
    if st.button("↺ Nueva",use_container_width=True,key="nb"):
        st.session_state.session_id=nueva_sesion()
        st.session_state.mensajes=[]
        st.session_state.turno=0
        st.session_state.input_key+=1
        st.rerun()

if enviar and mensaje and mensaje.strip():
    t=mensaje.strip()
    st.session_state.mensajes.append({"rol":"user","contenido":t})
    with st.spinner(""): res=chat(st.session_state.session_id,t,st.session_state.user_code)
    st.session_state.mensajes.append({"rol":"agent","contenido":res.get("respuesta",""),"protocolo":res.get("protocolo","normal")})
    st.session_state.turno=res.get("turno",st.session_state.turno+1)
    st.session_state.input_key+=1
    st.rerun()

# python -m streamlit run app2.py

import io
import time
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import zxingcpp

# Módulo de base de datos PostgreSQL en AWS RDS
from db import buscar_codigo, init_db, obtener_progreso_master_box

# Aseguramos que la base de datos esté inicializada y tenga todas las columnas requeridas
init_db()

# ---------------------------------------------------------
# Configuración de Página para Móviles
# ---------------------------------------------------------
st.set_page_config(
    page_title="Completar Master Box",
    page_icon="📦",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilos CSS Personalizados para Alta Eficiencia y Estética Premium (Optimizados para Móvil)
st.markdown("""
    <style>
        /* Prevención de desbordamiento horizontal en móviles */
        .stApp {
            background-color: #0F172A;
            color: #F8FAFC;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            overflow-x: hidden;
        }
        .main-header {
            text-align: center;
            padding: 12px 0 6px 0;
        }
        .main-header h2 {
            color: #38BDF8;
            font-weight: 800;
            font-size: 1.6rem;
            margin-bottom: 2px;
        }
        .main-header p {
            color: #94A3B8;
            font-size: 0.85rem;
        }
        .progress-box {
            background-color: #1E293B;
            border: 2px solid #38BDF8;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            margin-bottom: 20px;
        }
        .progress-box h3 {
            margin: 0;
            color: #94A3B8;
            font-size: 1rem;
        }
        .progress-box .counter {
            font-size: 3rem;
            font-weight: 900;
            color: #38BDF8;
            margin: 10px 0;
        }
        .result-card-found {
            background: linear-gradient(135deg, #059669 0%, #10B981 100%);
            color: #FFFFFF;
            padding: 22px;
            border-radius: 18px;
            box-shadow: 0 10px 25px -5px rgba(16, 185, 129, 0.4);
            margin: 15px 0;
            animation: popIn 0.3s ease-out;
        }
        .result-card-notfound {
            background: linear-gradient(135deg, #DC2626 0%, #EF4444 100%);
            color: #FFFFFF;
            padding: 22px;
            border-radius: 18px;
            box-shadow: 0 10px 25px -5px rgba(239, 68, 68, 0.4);
            margin: 15px 0;
            animation: popIn 0.3s ease-out;
        }
        @keyframes popIn {
            0% { transform: scale(0.95); opacity: 0; }
            100% { transform: scale(1); opacity: 1; }
        }
        .detail-row {
            display: flex;
            justify-content: space-between;
            border-bottom: 1px solid rgba(255,255,255,0.2);
            padding: 6px 0;
            font-size: 0.95rem;
        }
        .detail-row strong {
            text-align: right;
            word-break: break-word;
            max-width: 65%;
        }
        .detail-row:last-child {
            border-bottom: none;
        }
        .badge-source {
            background: rgba(0,0,0,0.3);
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        @media (max-width: 600px) {
            .main-header h2 { font-size: 1.35rem; }
            .result-card-found, .result-card-notfound { padding: 16px; border-radius: 12px; }
            .detail-row { flex-direction: column; align-items: flex-start; }
            .detail-row strong { text-align: left; max-width: 100%; margin-top: 3px; font-size: 1.05rem; }
            div.row-widget.stRadio > div[role="radiogroup"] { flex-direction: column !important; gap: 8px !important; }
            .block-container { padding-top: 1.5rem !important; padding-bottom: 1.5rem !important; padding-left: 1rem !important; padding-right: 1rem !important; }
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sintetizador de Audio HTML5 (Web Audio API)
# ---------------------------------------------------------
def emitir_sonido(tipo: str):
    import time
    ts = time.time()
    if tipo == "success":
        js_code = f"""
        <script>
            // ts: {ts}
            try {{
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                const osc1 = audioCtx.createOscillator();
                const gain1 = audioCtx.createGain();
                osc1.type = 'sine';
                osc1.frequency.setValueAtTime(880, audioCtx.currentTime);
                gain1.gain.setValueAtTime(0.3, audioCtx.currentTime);
                osc1.connect(gain1);
                gain1.connect(audioCtx.destination);
                osc1.start();
                osc1.stop(audioCtx.currentTime + 0.12);

                setTimeout(() => {{
                    const osc2 = audioCtx.createOscillator();
                    const gain2 = audioCtx.createGain();
                    osc2.type = 'sine';
                    osc2.frequency.setValueAtTime(1046, audioCtx.currentTime);
                    gain2.gain.setValueAtTime(0.3, audioCtx.currentTime);
                    osc2.connect(gain2);
                    gain2.connect(audioCtx.destination);
                    osc2.start();
                    osc2.stop(audioCtx.currentTime + 0.2);
                }}, 130);
            }} catch(e) {{ console.log(e); }}
        </script>
        """
        components.html(js_code, height=0, width=0)
    elif tipo == "error":
        js_code = f"""
        <script>
            // ts: {ts}
            try {{
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(220, audioCtx.currentTime);
                gain.gain.setValueAtTime(0.4, audioCtx.currentTime);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.4);
            }} catch(e) {{ console.log(e); }}
        </script>
        """
        components.html(js_code, height=0, width=0)

# ---------------------------------------------------------
# Inicialización de Estado de Sesión
# ---------------------------------------------------------
if "historial" not in st.session_state:
    st.session_state.historial = []
if "ultimo_codigo_procesado" not in st.session_state:
    st.session_state.ultimo_codigo_procesado = None
if "resultado_actual" not in st.session_state:
    st.session_state.resultado_actual = None
if "current_master_box" not in st.session_state:
    st.session_state.current_master_box = None
if "master_box_progreso" not in st.session_state:
    st.session_state.master_box_progreso = None
if "codigo_a_procesar" not in st.session_state:
    st.session_state.codigo_a_procesar = None

def procesar_y_limpiar_manual():
    if st.session_state.get("manual_input"):
        st.session_state.codigo_a_procesar = st.session_state.manual_input
        st.session_state.manual_input = ""
        st.session_state.ultimo_codigo_procesado = None

def procesar_y_limpiar_live():
    if st.session_state.get("live_input"):
        st.session_state.codigo_a_procesar = st.session_state.live_input
        st.session_state.live_input = ""
        st.session_state.ultimo_codigo_procesado = None

# ---------------------------------------------------------
# Lógica de Búsqueda (Procesamiento temprano)
# ---------------------------------------------------------
if st.session_state.codigo_a_procesar:
    codigo_limpio = st.session_state.codigo_a_procesar.strip()
    st.session_state.codigo_a_procesar = None
    
    if st.session_state.ultimo_codigo_procesado != codigo_limpio:
        st.session_state.ultimo_codigo_procesado = codigo_limpio
        
        # Buscar el código
        res, origen = buscar_codigo(codigo_limpio)
        
        tipo_resultado = "not_found"
        if res:
            if res['master_box'] != st.session_state.current_master_box:
                tipo_resultado = "wrong_box"
            else:
                tipo_resultado = "success"
                # Actualizar el progreso desde la BD
                st.session_state.master_box_progreso = obtener_progreso_master_box(st.session_state.current_master_box)

        st.session_state.resultado_actual = [res, origen, codigo_limpio, tipo_resultado, True]

        # Registrar en el historial de la sesión
        st.session_state.historial.insert(0, {
            "hora": datetime.now().strftime("%H:%M:%S"),
            "codigo_buscado": codigo_limpio,
            "codigo_barras": res.get("codigo_barras", codigo_limpio) if res else codigo_limpio,
            "codigo_pedido": res.get("codigo_pedido", "") if res else "",
            "encontrado": tipo_resultado == "success",
            "tipo": tipo_resultado,
            "nombre": res.get("desc_master_box", "Caja") if res else "No registrado",
            "origen": origen
        })

# ---------------------------------------------------------
# Encabezado
# ---------------------------------------------------------
st.markdown("""
    <div class="main-header">
        <h2>📦 Completar Master Box</h2>
        <p>Verifica paso a paso el contenido de una caja maestra</p>
    </div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# PANTALLA 1: SELECCIÓN DE MASTER BOX
# ---------------------------------------------------------
if st.session_state.current_master_box is None:
    st.info("Primero, introduce o escanea la Master Box que vas a trabajar.")
    mb_input = st.text_input("Código de la Master Box:", key="mb_input_field")
    if st.button("Buscar Caja", use_container_width=True):
        if mb_input:
            progreso = obtener_progreso_master_box(mb_input)
            if progreso:
                st.session_state.current_master_box = progreso["master_box"]
                st.session_state.master_box_progreso = progreso
                st.rerun()
            else:
                st.error("No se encontraron registros para esa Master Box.")
    st.stop()


# ---------------------------------------------------------
# PANTALLA 2: ESCANEO Y PROGRESO
# ---------------------------------------------------------
prog = st.session_state.master_box_progreso
if prog:
    if prog['encontrados'] >= prog['total']:
        color_contador = "#10B981" # Verde
    else:
        color_contador = "#38BDF8" # Azul

    st.markdown(f"""
        <div class="progress-box" style="display: flex; align-items: center; justify-content: center; gap: 15px; padding: 15px; flex-wrap: wrap;">
            <h3 style="font-size: 1.4rem; margin: 0; color: #F8FAFC;">{prog['master_box']}</h3>
            <span style="font-size: 1.2rem; color: #94A3B8;">{prog.get('desc_master_box', '')}</span>
            <div class="counter" style="color: {color_contador}; font-size: 1.8rem; margin: 0; padding-left: 10px; border-left: 2px solid #334155;">{prog['encontrados']} / {prog['total']}</div>
        </div>
    """, unsafe_allow_html=True)

if st.button("🔄 Cambiar a otra Master Box", use_container_width=True):
    st.session_state.current_master_box = None
    st.session_state.master_box_progreso = None
    st.session_state.resultado_actual = None
    st.session_state.historial = []
    st.rerun()

st.markdown("---")

modo = None
codigo_detectado = None

if prog and prog['encontrados'] < prog['total']:
    modo = st.radio(
        "Selecciona el modo de lectura:",
        ["⚡ Escáner Continuo en Vivo", "📷 Tomar Foto", "⌨️ Entrada Manual / Escáner USB"],
        horizontal=True,
        label_visibility="collapsed"
    )

    if modo == "⚡ Escáner Continuo en Vivo":
        st.caption("📷 Apunta la cámara del móvil al código de barras")
        html_scanner = """
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js"></script>
            <style>
                #reader { width: 100%; max-width: 450px; margin: 0 auto; border-radius: 12px; overflow: hidden; border: 2px solid #38BDF8; }
                #reader video { object-fit: cover; width: 100% !important; }
            </style>
        </head>
        <body>
            <div id="reader"></div>
            <script>
                function onScanSuccess(decodedText, decodedResult) {
                    window.parent.postMessage({ type: 'streamlit:setComponentValue', value: decodedText }, '*');
                }
                let html5QrcodeScanner = new Html5QrcodeScanner("reader", { fps: 15, qrbox: {width: 280, height: 160}, experimentalFeatures: {useBarCodeDetectorIfSupported: true} }, false);
                html5QrcodeScanner.render(onScanSuccess);
            </script>
        </body>
        </html>
        """
        scanned_value = components.html(html_scanner, height=330)
        st.text_input("Código capturado en vivo:", key="live_input", placeholder="Escaneando cámara...", on_change=procesar_y_limpiar_live)
    elif modo == "📷 Tomar Foto":
        foto = st.camera_input("Capturar etiqueta")
        if foto:
            try:
                img = Image.open(io.BytesIO(foto.getvalue()))
                resultados = zxingcpp.read_barcodes(img)
                if resultados:
                    codigo_detectado = resultados[0].text
                    st.success(f"Código detectado en foto: `{codigo_detectado}`")
                    st.session_state.codigo_a_procesar = codigo_detectado
                    st.rerun()
                else:
                    st.warning("No se identificó ningún código.")
            except Exception as e:
                st.error(f"Error procesando imagen: {e}")
    elif modo == "⌨️ Entrada Manual / Escáner USB":
        st.text_input("Ingresa o escanea el código aquí:", key="manual_input", on_change=procesar_y_limpiar_manual)
else:
    st.success("🎉 ¡ESTA MASTER BOX ESTÁ COMPLETADA!")
    emitir_sonido("success")


# ---------------------------------------------------------
# Presentación de Resultados
# ---------------------------------------------------------
# Renderizar resultado actual si existe
if st.session_state.resultado_actual:
    ra = st.session_state.resultado_actual
    res, origen, codigo_buscado, tipo_resultado, sonido_pendiente = ra[0], ra[1], ra[2], ra[3], ra[4]

    if tipo_resultado == "success":
        if sonido_pendiente:
            emitir_sonido("success")
            ra[4] = False
        ya_encontrado_html = ""
        if res.get('ya_encontrado'):
            ya_encontrado_html = "<div style='background-color: #F59E0B; color: white; padding: 5px 10px; border-radius: 5px; margin-bottom: 15px; font-weight: bold; text-align: center; font-size: 1.1rem;'>⚠️ CÓDIGO YA HABÍA SIDO ENCONTRADO</div>"

        st.markdown(f"""
            <div class="result-card-found">{ya_encontrado_html}
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 12px;">
                    <span style="font-size: 1.4rem; font-weight:bold;">✅ ENCONTRADO EN BD</span>
                    <span class="badge-source">{origen}</span>
                </div>
                <div class="detail-row">
                    <span>Código de Barras:</span>
                    <strong>{res.get('codigo_barras', codigo_buscado)}</strong>
                </div>
                <div class="detail-row">
                    <span>Master Box:</span>
                    <strong>{res.get('master_box', 'N/A')}</strong>
                </div>
                <div class="detail-row">
                    <span>Código Pedido:</span>
                    <strong>{res.get('codigo_pedido', 'N/A')}</strong>
                </div>
                <div class="detail-row">
                    <span>Letra Apellido:</span>
                    <strong>{res.get('letra_apellido', 'N/A')}</strong>
                </div>
                <div class="detail-row">
                    <span>Fecha encontrado:</span>
                    <strong>{str(res.get('fecha_encontrado', 'N/A'))[:19]}</strong>
                </div>
            </div>
        """, unsafe_allow_html=True)
    elif tipo_resultado == "wrong_box":
        if sonido_pendiente:
            emitir_sonido("error")
            ra[4] = False
        st.markdown(f"""
            <div class="result-card-notfound">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 10px;">
                    <span style="font-size: 1.4rem; font-weight:bold;">⚠️ CAJA EQUIVOCADA</span>
                </div>
                <p style="font-size: 1.1rem; margin-bottom: 12px;">Este producto pertenece a otra Master Box.</p>
                <div class="detail-row">
                    <span>Código:</span>
                    <strong>{res.get('codigo_barras', codigo_buscado)}</strong>
                </div>
                <div class="detail-row">
                    <span>Pertenece a:</span>
                    <strong>{res.get('master_box', 'N/A')}</strong>
                </div>
                <div class="detail-row">
                    <span>Caja Actual:</span>
                    <strong>{st.session_state.current_master_box}</strong>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        if sonido_pendiente:
            emitir_sonido("error")
            ra[4] = False
        st.markdown(f"""
            <div class="result-card-notfound">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 10px;">
                    <span style="font-size: 1.4rem; font-weight:bold;">❌ NO ENCONTRADO</span>
                    <span class="badge-source">AWS RDS</span>
                </div>
                <p style="font-size: 1.1rem; margin-bottom: 12px;">El código no está registrado en la base de datos.</p>
                <div class="detail-row">
                    <span>Código Escaneado:</span>
                    <strong>{codigo_buscado}</strong>
                </div>
            </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Historial de Escaneos Recientes
# ---------------------------------------------------------
if st.session_state.historial:
    st.markdown("---")
    st.subheader("📋 Historial de esta Master Box")
    
    for item in st.session_state.historial[:8]:
        if item["tipo"] == "success":
            color_indicador = "🟢"
        elif item["tipo"] == "wrong_box":
            color_indicador = "🟠"
        else:
            color_indicador = "🔴"
            
        codigo_b = item.get("codigo_barras", item.get("codigo", ""))
        codigo_p = item.get("codigo_pedido", "")
        
        if item["encontrado"]:
            st.text(f"{item['hora']} | {color_indicador} {codigo_b} -> {codigo_p} -> {item['nombre']} ({item['origen']})")
        else:
            st.text(f"{item['hora']} | {color_indicador} {codigo_b} -> {item['nombre']} ({item['origen']})")

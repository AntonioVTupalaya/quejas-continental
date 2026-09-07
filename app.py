import streamlit as st
import pandas as pd
import database as db
import carga_datos as cd
from datetime import date

st.set_page_config(page_title="Quejas y Reclamos | Dirección de Asuntos Académicos", page_icon="🎓", layout="wide")

# Credenciales Supabase desde secrets (Cloud) o entorno (local)
import os
_sb_secret = st.secrets.get("supabase", {}) if st.secrets else {}
SUPABASE_URL = _sb_secret.get("url") or os.environ.get("SUPABASE_URL")
SUPABASE_KEY = _sb_secret.get("key") or os.environ.get("SUPABASE_KEY")
if not (SUPABASE_URL and SUPABASE_KEY):
    st.error("Faltan las credenciales de Supabase. Configúralas en los Secrets de Streamlit Cloud o en .streamlit/secrets.toml")
    st.stop()
os.environ["SUPABASE_URL"] = SUPABASE_URL
os.environ["SUPABASE_KEY"] = SUPABASE_KEY

# Paleta institucional PROYECTO PRISM - Universidad Continental (UCColores.tex)
UC_PRINCIPAL = "#6802C1"          # violeta institucional
UC_FRANJA = "#9632FA"             # violeta luminoso
UC_PROFUNDO = "#28075A"           # violeta profundo
UC_MORADO_OSCURO = "#330066"      # morado oscuro
UC_TITULO_OSCURO = "#00143D"      # azul marino (títulos jerarquía)
UC_LILA_DECORATIVO = "#CAA0F5"    # lila decorativo
UC_LAVANDA = "#E0AAFF"            # lavanda
UC_FONDO_TITULO = "#FCFBFF"       # blanco violeta
UC_FONDO_SUAVE = "#F7F4FF"        # lila muy claro (paneles)
UC_BLANCO = "#FFFFFF"
UC_NEGRO = "#000000"
UC_GRIS_TEXTO = "#4A4A4A"         # gris de lectura
UC_GRIS_LOGO = "#8A8A8A"          # gris institucional
UC_EXITO = "#059669"              # verde de logro
UC_ADVERTENCIA = "#C66A00"        # ámbar
UC_ERROR = "#B42318"              # rojo

db.init_db()

EAPS = [
    "ADMINISTRACIÓN",
    "ADMINISTRACIÓN Y FINANZAS",
    "ADMINISTRACIÓN Y GESTIÓN DEL TALENTO HUMANO",
    "ADMINISTRACIÓN Y GESTIÓN PÚBLICA",
    "ADMINISTRACIÓN Y MARKETING",
    "ADMINISTRACIÓN Y NEGOCIOS DIGITALES",
    "ADMINISTRACIÓN Y NEGOCIOS INTERNACIONALES",
    "ADMINISTRACIÓN Y RECURSOS HUMANOS",
    "ARQUITECTURA",
    "ARQUITECTURA Y DISEÑO DE INTERIORES",
    "CIENCIA DE LA COMPUTACIÓN",
    "CIENCIAS DE LA COMUNICACIÓN",
    "CIENCIAS Y TECNOLOGÍAS DE LA COMUNICACIÓN",
    "CONTABILIDAD",
    "CONTABILIDAD Y FINANZAS",
    "DERECHO",
    "ECONOMÍA",
    "EDUCACIÓN CON ESPECIALIDAD EN INNOVACIÓN Y APRENDIZAJE DIGITAL",
    "ENFERMERÍA",
    "FARMACIA Y BIOQUÍMICA",
    "INGENIERÍA AMBIENTAL",
    "INGENIERÍA CIVIL",
    "INGENIERÍA DE MINAS",
    "INGENIERÍA DE SISTEMAS E INFORMÁTICA",
    "INGENIERÍA ELÉCTRICA",
    "INGENIERÍA EMPRESARIAL",
    "INGENIERÍA INDUSTRIAL",
    "INGENIERÍA MECATRÓNICA",
    "INGENIERÍA MECÁNICA",
    "MEDICINA HUMANA",
    "NUTRICIÓN Y DIETÉTICA",
    "ODONTOLOGÍA",
    "PSICOLOGÍA",
    "TECNOLOGÍA MÉDICA - ESPECIALIDAD EN LABORATORIO CLÍNICO Y ANATOMÍA PATOLÓGICA",
    "TECNOLOGÍA MÉDICA - ESPECIALIDAD EN TERAPIA FÍSICA Y REHABILITACIÓN",
    "TECNOLOGÍA MÉDICA CON ESPECIALIDAD EN RADIOLOGÍA",
]


def estilo():
    st.markdown(
        f"""
        <style>
        .stApp {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .stApp, html, body {{
            background-color: #FBF9FF;
        }}
        /* ---- Cabecera institucional ---- */
        .uc-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-top: 18px;
            background: linear-gradient(135deg, {UC_PROFUNDO} 0%, {UC_PRINCIPAL} 100%);
            color: {UC_BLANCO};
            padding: 20px 32px;
            border-radius: 12px;
            margin-bottom: 8px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.15);
        }}
        .uc-header .logo img {{
            height: 56px;
        }}
        .uc-header .titulos {{
            text-align: right;
        }}
        .uc-header .titulos .universidad {{
            font-size: 15px;
            letter-spacing: 2px;
            font-weight: 300;
        }}
        .uc-header .titulos .direccion {{
            font-size: 24px;
            font-weight: 700;
            margin-top: 2px;
        }}
        .uc-header .titulos .sistema {{
            font-size: 14px;
            color: {UC_LAVANDA};
            margin-top: 4px;
        }}
        .uc-barra {{
            height: 5px;
            background: linear-gradient(90deg, {UC_FRANJA}, {UC_LAVANDA}, {UC_FRANJA});
            border-radius: 0 0 8px 8px;
            margin-bottom: 24px;
        }}
        /* ---- Folio ---- */
        .folio-badge {{
            background-color: {UC_LAVANDA};
            color: {UC_PROFUNDO};
            padding: 8px 16px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 16px;
            border: 1px solid {UC_LILA_DECORATIVO};
            text-align: center;
        }}
        /* ---- Tarjetas de registros (colores semánticos didácticos) ---- */
        .registro-card {{
            border-left: 6px solid;
            padding: 12px;
            margin-bottom: 16px;
            border-radius: 8px;
        }}
        .pendiente {{ border-color: {UC_ADVERTENCIA}; background: #FFF6EA; }}
        .en-proceso {{ border-color: {UC_PRINCIPAL}; background: {UC_FONDO_SUAVE}; }}
        .resuelta {{ border-color: {UC_EXITO}; background: #EAF7F1; }}
        .cancellada {{ border-color: {UC_GRIS_LOGO}; background: #F5F5F5; }}

        /* ---- Encabezados de sección (oscuros para contraste) ---- */
        h1, h2, h3, h4, h5, h6 {{
            color: {UC_TITULO_OSCURO} !important;
        }}
        div[data-testid="stHeading"] h1,
        div[data-testid="stHeading"] h2,
        div[data-testid="stHeading"] h3,
        div[data-testid="stHeading"] h4,
        div[data-testid="stHeading"] h5,
        div[data-testid="stHeading"] h6 {{
            color: {UC_TITULO_OSCURO} !important;
        }}
        div[data-testid="stHeading"], div[data-testid="stHeader"] h1,
        div[data-testid="stHeader"] h2, div[data-testid="stHeader"] h3 {{
            color: {UC_TITULO_OSCURO} !important;
        }}

        /* ---- Contrastes de interactivos: fondo CLARO y texto OSCURO ---- */
        /* Núcleo del campo de BasinUI (input / select) */
        div[data-baseweb="input"], div[data-baseweb="base-input"],
        div[data-baseweb="select"] > div, div[data-baseweb="select"] div[data-baseweb="base-input"],
        .stDateInput, .stTimeInput, .stNumberInput, textarea {{
            background-color: {UC_BLANCO} !important;
            color: {UC_NEGRO} !important;
        }}
        /* El input HTML real donde se escribe */
        div[data-baseweb="input"] input, .stDateInput input,
        .stTimeInput input, .stNumberInput input, textarea, input {{
            background-color: {UC_BLANCO} !important;
            color: {UC_NEGRO} !important;
        }}
        /* Selectbox: texto mostrado */
        div[data-baseweb="select"] span,
        div[data-baseweb="select"] [data-baseweb="tag"],
        div[data-baseweb="select"] * {{
            background-color: transparent !important;
        }}
        div[data-baseweb="select"] > div > div > div, 
        div[data-baseweb="select"] [data-baseweb="base-input"] {{
            color: {UC_NEGRO} !important;
        }}
        /* Menú desplegable (lista) y opciones */
        ul[data-baseweb="menu"], div[data-baseweb="popover"] > div,
        li[role="option"], div[data-baseweb="menu-list"],
        div[data-baseweb="menu"] {{
            background-color: {UC_BLANCO} !important;
        }}
        li[role="option"] {{
            color: {UC_TITULO_OSCURO} !important;
        }}
        li[role="option"]:hover, li[aria-selected="true"] {{
            background-color: {UC_FONDO_SUAVE} !important;
        }}
        /* Labels de los campos */
        .stTextInput label, .stNumberInput label, .stDateInput label,
        .stSelectbox label, .stTimeInput label, .stMultiSelect label,
        .stTextArea label, .stRadio label, .stCheckbox label,
        label[data-testid="stWidgetLabel"] p {{
            color: {UC_TITULO_OSCURO} !important;
            font-weight: 600;
        }}
        /* Placeholder legible */
        div[data-baseweb="input"] input::placeholder,
        textarea::placeholder {{
            color: {UC_GRIS_LOGO} !important;
        }}
        /* Ayudas */
        div[data-testid="stTextInputHelp"], .stCaption, [data-testid="stWidgetHelp"] {{
            color: {UC_GRIS_TEXTO} !important;
        }}
        /* ---- Pie de página con paleta ---- */
        .uc-pie {{
            margin-top: 30px;
            padding: 10px 0;
            text-align: center;
            font-size: 15px;
            color: {UC_PROFUNDO};
        }}
        .uc-pie .uc-pie-uni {{
            color: {UC_PRINCIPAL};
            font-weight: 700;
        }}
        .uc-pie .uc-pie-daa {{
            color: {UC_TITULO_OSCURO};
            font-weight: 600;
        }}
        .uc-pie .uc-pie-at {{
            color: {UC_PROFUNDO};
            font-weight: 800;
        }}
        .uc-pie > span {{
            margin: 0 6px;
        }}
        /* ============ ALINEACIÓN: todos los cuadros con la misma altura ============ */
        [data-testid="stTextInputRootElement"],
        [data-testid="stNumberInputRootElement"],
        [data-testid="stTimeInputRootElement"],
        [data-testid="stSelectbox"],
        [data-testid="stDateInput"],
        [data-testid="stTimeInput"] {{
            height: 42px !important;
            min-height: 42px !important;
            max-height: 42px !important;
        }}
        [data-testid="stTextInputRootElement"] input {{
            height: 40px !important;
        }}
        [data-testid="stSelectbox"] > div > div,
        [data-testid="stDateInput"] > div > div {{
            height: 40px !important;
        }}
        /* ---- Formato uniforme de todos los campos: borde TENUE igual que textarea ---- */
        [data-testid="stTextInputRootElement"],
        [data-testid="stNumberInputRootElement"],
        [data-testid="stTimeInputRootElement"],
        [data-testid="stTextAreaRootElement"],
        [data-testid="stSelectbox"],
        [data-testid="stMultiSelect"],
        [data-testid="stDateInput"],
        [data-testid="stTimeInput"] {{
            border: 1px solid #D8CFEA !important;
            border-radius: 8px !important;
            box-shadow: none !important;
            outline: none !important;
            background-color: {UC_BLANCO} !important;
        }}
        /* Al hacer click/focus el borde se atenúa sin resaltar */
        [data-testid="stTextInputRootElement"]:hover,
        [data-testid="stTextInputRootElement"]:focus-within,
        [data-testid="stNumberInputRootElement"]:hover,
        [data-testid="stNumberInputRootElement"]:focus-within,
        [data-testid="stTimeInputRootElement"]:hover,
        [data-testid="stTimeInputRootElement"]:focus-within,
        [data-testid="stTextAreaRootElement"]:hover,
        [data-testid="stTextAreaRootElement"]:focus-within,
        [data-testid="stSelectbox"]:hover, [data-testid="stSelectbox"]:focus-within,
        [data-testid="stMultiSelect"]:hover, [data-testid="stMultiSelect"]:focus-within,
        [data-testid="stDateInput"]:hover, [data-testid="stDateInput"]:focus-within,
        [data-testid="stTimeInput"]:hover, [data-testid="stTimeInput"]:focus-within {{
            border: 1px solid #C0B4DA !important;
            box-shadow: none !important;
            outline: none !important;
        }}
        /* Descartar el anillo de la estructura interna que dibuja líneas gruesas */
        [data-testid="stTextInputRootElement"] *,
        [data-testid="stNumberInputRootElement"] *,
        [data-testid="stTimeInputRootElement"] *,
        [data-testid="stTextAreaRootElement"] *,
        [data-testid="stSelectbox"] *,
        [data-testid="stDateInput"] *,
        [data-testid="stTimeInput"] * {{
            box-shadow: none !important;
            outline: none !important;
        }}
        /* El input/texto interno sin borde ni fondo adquiridos */
        [data-testid="stTextInputField"],
        [data-testid="stTextAreaRootElement"] textarea,
        [data-testid="stSelectbox"] input,
        input, textarea {{
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
            background-color: transparent !important;
        }}
        .stButton > button {{
            background-color: {UC_PRINCIPAL};
            color: {UC_BLANCO};
            border: none;
            border-radius: 8px;
        }}
        .stButton > button:hover {{
            background-color: {UC_PROFUNDO};
            color: {UC_BLANCO};
        }}
        /* ---- Eliminar cualquier focus ring / fondo oscuro residual ---- */
        *:focus, *:focus-visible, *:focus-within {{
            outline: none !important;
        }}
        /* Label de campo uniforme (texto independiente, altura fija para alinear columnas) */
        .campo-label {{
            color: {UC_TITULO_OSCURO} !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            margin-bottom: 4px !important;
            min-height: 20px !important;
            line-height: 20px !important;
            background: transparent !important;
        }}
        div[data-testid="stWidgetLabel"]:focus,
        div[data-testid="stWidgetLabel"]:hover {{
            background-color: transparent !important;
            outline: none !important;
            box-shadow: none !important;
        }}
        /* Cualquier anillo de focus de loss componentes Basil/Streamlit */
        [data-testid="stTextInput"]:has(> div):focus-within,
        [data-testid="stSelectbox"]:has(> div):focus-within,
        div[data-baseweb="popover"] {{
            background-color: {UC_BLANCO} !important;
        }}
        section[data-testid="stKeyFocused"] *,
        [data-testid="stForm"] *:focus {{
            box-shadow: none !important;
            outline: none !important;
        }}
        /* ============================================================
           LABEL INDEPENDIENTE: siempre transparente, fijo y sin
           resaltado en ningún estado (normal, hover, focus, focus-within).
           Sin transiciones para evitar el efecto de "resaltar".
           ============================================================ */
        label[data-testid="stWidgetLabel"],
        label[data-testid="stWidgetLabel"] p,
        label[data-testid="stWidgetLabel"] span,
        [data-testid="stWidgetLabel"] * {{
            transition: none !important;
            color: {UC_TITULO_OSCURO} !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            background-color: transparent !important;
            box-shadow: none !important;
            outline: none !important;
            border: none !important;
            text-shadow: none !important;
        }}
        label[data-testid="stWidgetLabel"]:hover,
        label[data-testid="stWidgetLabel"] p:hover,
        label[data-testid="stWidgetLabel"]:focus,
        label[data-testid="stWidgetLabel"] p:focus,
        label[data-testid="stWidgetLabel"]:active,
        *:hover label[data-testid="stWidgetLabel"] *,
        *:focus label[data-testid="stWidgetLabel"] *,
        *:focus-within label[data-testid="stWidgetLabel"] *,
        *:focus-within label,
        label:focus-within {{
            transition: none !important;
            color: {UC_TITULO_OSCURO} !important;
            font-weight: 600 !important;
            background-color: transparent !important;
            box-shadow: none !important;
            outline: none !important;
            border: none !important;
            text-shadow: none !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def cabecera():
    logo_html = (
        '<img src="https://raw.githubusercontent.com/JMDeveloper-Dev/public/main/logo_uc.png">'
    )
    # El logo local se muestra como imagen a través de base64
    import base64
    import os
    ruta_logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_uc.png")
    if os.path.exists(ruta_logo):
        with open(ruta_logo, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        logo_html = f'<img src="data:image/png;base64,{b64}" style="height:56px">'

    st.markdown(
        f"""
        <div class="uc-header">
            <div class="logo">
                {logo_html}
            </div>
            <div class="titulos">
                <div class="direccion">Dirección de Asuntos Académicos</div>
                <div class="sistema">Sistema de Quejas y Reclamos de Estudiantes</div>
            </div>
        </div>
        <div class="uc-barra"></div>
        """,
        unsafe_allow_html=True,
    )


def etiqueta(texto):
    st.markdown(
        f'<div class="campo-label">{texto}</div>',
        unsafe_allow_html=True,
    )


def pie():
    st.markdown(
        f"""
        <div class="uc-pie">
            <span class="uc-pie-uni">UNIVERSIDAD CONTINENTAL</span>
            <span class="uc-pie">·</span>
            <span class="uc-pie-daa">Dirección de Asuntos Académicos – Ciencias</span>
            <span class="uc-pie">·</span>
            <span class="uc-pie-at">@mquispe</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def mostrar_formulario():
    st.header("📝 Registrar Nueva Queja o Reclamo")

    with st.form("formulario_queja", clear_on_submit=True):
        st.subheader("👤 Datos del Alumno")
        c1, c2 = st.columns(2)
        with c1:
            etiqueta("Apellidos *")
            apellidos = st.text_input("Apellidos", label_visibility="collapsed")
            etiqueta("Nombres *")
            nombres = st.text_input("Nombres", label_visibility="collapsed")
            etiqueta("Código de Matrícula *")
            matricula = st.text_input("Código de Matrícula", label_visibility="collapsed")
            etiqueta("Celular *")
            celular = st.text_input("Celular", label_visibility="collapsed")
        with c2:
            etiqueta("DNI *")
            dni = st.text_input("DNI", label_visibility="collapsed")
            etiqueta("Fecha de registro")
            fecha_registro = st.date_input("F. registro", value=date.today(), label_visibility="collapsed")
            etiqueta("EAP - Escuela Académica Profesional *")
            eap = st.selectbox("EAP", EAPS, label_visibility="collapsed")
            etiqueta("NRC *")
            nrc = st.text_input("NRC", help="Ingrese el NRC del curso. Asignatura y docente se autocompletan.", label_visibility="collapsed")

        st.divider()
        st.subheader("📚 Datos del Curso")

        info_nrc = None
        if nrc.strip():
            info_nrc = cd.obtener_info_nrc(nrc.strip())
            if info_nrc:
                st.success(f"✅ Curso encontrado: {info_nrc['curso']} - {info_nrc['docente']}")
            else:
                st.warning("⚠️ NRC no encontrado. Puede completar los datos manualmente.")

        c3, c4 = st.columns(2)
        with c3:
            etiqueta("Asignatura *")
            asignatura = st.text_input("Asig", value=info_nrc["curso"] if info_nrc else "", label_visibility="collapsed")
            etiqueta("Docente *")
            docente = st.text_input("Doc", value=info_nrc["docente"] if info_nrc else "", label_visibility="collapsed")
        with c4:
            etiqueta("Fecha del hecho")
            fecha_hecho = st.date_input("F. hecho", value=date.today(), label_visibility="collapsed")
            etiqueta("Tipo de reporte *")
            tipo = st.selectbox(
                "Tipo",
                ["Queja", "Reclamo", "Sugerencia", "Observación"],
                label_visibility="collapsed",
            )

        horarios = []
        horarios_detectados = (info_nrc["horarios"] if info_nrc else []) or []

        st.markdown("**Horario del curso** (el curso puede dictarse hasta en 3 días):")
        st.caption("Horarios en bloques de 2 horas pedagógicas consecutivas")
        h_enc = st.columns(3)
        h_enc[0].markdown('<div class="campo-label">Día</div>', unsafe_allow_html=True)
        h_enc[1].markdown('<div class="campo-label">Inicio</div>', unsafe_allow_html=True)
        h_enc[2].markdown('<div class="campo-label">Fin</div>', unsafe_allow_html=True)

        un_dia = "-- Seleccionar --"
        for i in range(3):
            h_pre = horarios_detectados[i] if i < len(horarios_detectados) else None
            c_dia, c_ini, c_fin = st.columns(3)
            with c_dia:
                dia = st.selectbox(
                    "Día",
                    [un_dia] + cd.DIAS_SEMANA,
                    index=(cd.DIAS_SEMANA.index(h_pre["dia"]) + 1) if h_pre and h_pre["dia"] in cd.DIAS_SEMANA else 0,
                    key=f"dia_{i}",
                    label_visibility="collapsed",
                )

            opciones_inicio = cd.INICIOS_POR_DIA.get(dia, cd.HORAS_INICIO)
            opciones_fin = cd.FINES_POR_DIA.get(dia, cd.HORAS_FIN)

            with c_ini:
                inicio_idx = opciones_inicio.index(h_pre["inicio"]) if h_pre and h_pre["inicio"] in opciones_inicio else 0
                inicio = st.selectbox(
                    "Inicio",
                    opciones_inicio,
                    index=inicio_idx,
                    key=f"inicio_{i}",
                    label_visibility="collapsed",
                )
            with c_fin:
                fin_idx = opciones_fin.index(h_pre["fin"]) if h_pre and h_pre["fin"] in opciones_fin else (len(opciones_fin) - 1)
                fin = st.selectbox(
                    "Fin",
                    opciones_fin,
                    index=fin_idx,
                    key=f"fin_{i}",
                    label_visibility="collapsed",
                )
            if dia != un_dia:
                horarios.append({"dia": dia, "inicio": inicio, "fin": fin})

        st.divider()
        st.subheader("📝 Detalle de la Queja / Reclamo")
        detalle = st.text_area("Describa la queja o reclamo *", height=140)
        solicita = st.text_area("Solicita *", height=100, help="Escriba lo que desea el estudiante.")

        submitted = st.form_submit_button("💾 Guardar registro")

        if submitted:
            if not apellidos or not nombres or not matricula or not celular or not dni or not nrc or not detalle or not asignatura or not docente or not solicita:
                st.error("Por favor complete los campos obligatorios marcados con *")
            else:
                datos = {
                    "fecha": fecha_registro.strftime("%Y-%m-%d"),
                    "apellidos": apellidos.strip().upper(),
                    "nombres": nombres.strip().upper(),
                    "matricula": matricula.strip().upper(),
                    "celular": celular.strip(),
                    "dni": dni.strip(),
                    "eap": eap,
                    "asignatura": asignatura.strip(),
                    "nrc": nrc.strip(),
                    "docente": docente.strip(),
                    "tipo": tipo,
                    "detalle": detalle.strip(),
                    "solicita": solicita.strip(),
                    "fecha_hecho": fecha_hecho.strftime("%Y-%m-%d"),
                    "estado": "Pendiente",
                }
                folio = db.insertar_queja(datos, horarios)
                st.success(f"✅ Registro guardado correctamente")
                st.markdown(f'<div class="folio-badge">Folio asignado: {folio}</div>', unsafe_allow_html=True)


def mostrar_registros():
    st.header("📋 Registro de Quejas y Reclamos")

    quejas = db.obtener_quejas()
    if not quejas:
        st.info("No hay registros todavía. Use la pestaña 'Registrar' para capturar uno.")
        return

    tab_detalle, tab_tabla, tab_stats = st.tabs(["📑 Detalle", "🗂️ Tabla", "📊 Estadísticas"])

    with tab_tabla:
        df = pd.DataFrame(quejas)
        columnas = ["id", "folio", "fecha", "apellidos", "nombres", "matricula",
                    "celular", "dni", "eap", "asignatura", "nrc", "docente",
                    "tipo", "estado"]
        display = df[columnas].copy()
        display.columns = ["ID", "Folio", "Fecha", "Apellidos", "Nombres", "Matrícula",
                           "Celular", "DNI", "EAP", "Asignatura", "NRC", "Docente",
                           "Tipo", "Estado"]
        st.dataframe(display, use_container_width=True, hide_index=True)

        st.download_button(
            "⬇️ Descargar CSV",
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name="quejas_reclamos.csv",
            mime="text/csv",
        )

    with tab_detalle:
        for q in quejas:
            estado = q["estado"]
            clase = estado.lower().replace(" ", "-")
            cols = st.columns([3, 1])
            with cols[0]:
                horario_txt = " · ".join(
                    f"{h['dia']} {h['inicio']}-{h['fin']}" for h in q.get("horarios", [])
                ) if q.get("horarios") else "No registrado"
                st.markdown(
                    f'<div class="registro-card {clase}">'
                    f'<strong>{q["folio"]}</strong> - {q["apellidos"]}, {q["nombres"]} '
                    f'({q["matricula"]})<br>'
                    f'<strong>EAP:</strong> {q["eap"]} · <strong>DNI:</strong> {q["dni"]} · '
                    f'<strong>Celular:</strong> {q["celular"]}<br>'
                    f'<strong>Asignatura:</strong> {q["asignatura"]} · <strong>NRC:</strong> {q["nrc"]}<br>'
                    f'<strong>Docente:</strong> {q["docente"]} · <strong>Horario:</strong> {horario_txt}<br>'
                    f'<strong>Tipo:</strong> {q["tipo"]}<br>'
                    f'<strong>Hecho:</strong> {q["fecha_hecho"]} · <strong>Registro:</strong> {q["fecha"]}<br>'
                    f'<strong>Queja/Reclamo:</strong> {q["detalle"]}<br>'
                    f'<strong>Solicita:</strong> {q.get("solicita", "")}',
                    unsafe_allow_html=True,
                )
            with cols[1]:
                nuevo_estado = st.selectbox(
                    "Estado",
                    ["Pendiente", "En proceso", "Resuelta", "Cancelada"],
                    index=["Pendiente", "En proceso", "Resuelta", "Cancelada"].index(estado)
                    if estado in ["Pendiente", "En proceso", "Resuelta", "Cancelada"] else 0,
                    key=f"estado_{q['id']}",
                    label_visibility="collapsed",
                )
                if nuevo_estado != estado:
                    db.actualizar_estado(q["id"], nuevo_estado)
                    st.rerun()
                if st.button("🗑️ Eliminar", key=f"del_{q['id']}"):
                    db.eliminar_queja(q["id"])
                    st.rerun()
            st.divider()

    with tab_stats:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total registros", len(quejas))
        pendientes = sum(1 for q in quejas if q["estado"] == "Pendiente")
        resueltas = sum(1 for q in quejas if q["estado"] == "Resuelta")
        c2.metric("Pendientes", pendientes)
        c3.metric("Resueltas", resueltas)
        c4.metric("Procesadas", sum(1 for q in quejas if q["estado"] == "En proceso"))

        st.subheader("Distribución por tipo")
        tipo_counts = pd.Series([q["tipo"] for q in quejas]).value_counts()
        st.bar_chart(tipo_counts)


def main():
    estilo()
    cabecera()

    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] { display: none; }
        .stMainBlockContainer { padding-top: 2rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    mostrar_formulario()
    pie()


if __name__ == "__main__":
    main()

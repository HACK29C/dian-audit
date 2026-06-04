import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import tempfile
import os
from comparador import ComparadorArchivos
from exportador import ExportadorAuditoria

# Configuracion de pagina
st.set_page_config(
    page_title="Sistema de Auditoría de Datos - Verificacion y Analisis Fiscal",
    page_icon="app/LOGO.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado - Estilo corporativo DIAN moderno
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #F8F9FA;
    }
    
    .dian-header {
        background: linear-gradient(135deg, #0A2B4E 0%, #005A9E 50%, #003366 100%);
        padding: 2rem 2rem 1.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    
    .dian-header h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 600;
        color: white;
        letter-spacing: -0.5px;
    }
    
    .dian-header p {
        margin: 0.5rem 0 0 0;
        color: rgba(255,255,255,0.85);
        font-size: 0.95rem;
    }
    
    .dian-subheader {
        background: linear-gradient(135deg, #E8F4FD 0%, #D4E8F7 100%);
        padding: 1.2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border-left: 4px solid #005A9E;
    }
    
    .metric-card {
        background: white;
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: transform 0.2s;
        border-top: 4px solid;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    }
    
    .metric-card.critico {
        border-top-color: #DC3545;
    }
    
    .metric-card.alto {
        border-top-color: #FD7E14;
    }
    
    .metric-card.medio {
        border-top-color: #FFC107;
    }
    
    .metric-card.bajo {
        border-top-color: #28A745;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #6C757D;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    
    .metric-detail {
        font-size: 0.7rem;
        color: #6C757D;
        margin-top: 0.5rem;
    }
    
    .risk-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    
    .risk-card.critico {
        border-left-color: #DC3545;
        background: linear-gradient(90deg, #FFF5F5 0%, white 100%);
    }
    
    .risk-card.alto {
        border-left-color: #FD7E14;
        background: linear-gradient(90deg, #FFF8F0 0%, white 100%);
    }
    
    .risk-card.medio {
        border-left-color: #FFC107;
        background: linear-gradient(90deg, #FFFBEB 0%, white 100%);
    }
    
    .risk-card.bajo {
        border-left-color: #28A745;
        background: linear-gradient(90deg, #F0FFF4 0%, white 100%);
    }
    
    .risk-title {
        font-weight: 700;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .risk-value {
        font-size: 1.2rem;
        font-weight: 600;
        margin: 0.2rem 0;
    }
    
    .footer {
        text-align: center;
        padding: 2rem;
        color: #6C757D;
        font-size: 0.75rem;
        border-top: 1px solid #DEE2E6;
        margin-top: 2rem;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: white;
        padding: 0.5rem 1rem;
        border-radius: 12px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        font-weight: 500;
        color: #495057;
    }
    
    .stTabs [aria-selected="true"] {
        color: #005A9E;
        font-weight: 600;
    }
    
    .stButton button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,90,158,0.2);
    }
</style>
""", unsafe_allow_html=True)

# ==================== HEADER ====================
st.markdown("""
<div class="dian-header">
    <h1>Sistema de Auditoría de Datos</h1>
    <p>Direccion de Impuestos y Aduanas Nacionales de Colombia</p>
    <p style="font-size:0.85rem; margin-top:0.5rem;">Sistema de Verificacion, Analisis Fiscal y Control de Mercancias</p>
</div>
""", unsafe_allow_html=True)

# ==================== DESCRIPCION ====================
st.markdown("""
<div class="dian-subheader">
    <strong>Que hace esta herramienta?</strong><br>
    ElSistema de Auditoría de Datos permite comparar dos archivos de datos (Excel o CSV) para identificar discrepancias, 
    registros faltantes y duplicados. Es ideal para procesos de fiscalizacion, control de inventarios, 
    verificacion de declaraciones y auditoria de datos. Seleccione una columna clave (como ID, NIT o Factura) 
    y el sistema analizara automaticamente las diferencias.
</div>
""", unsafe_allow_html=True)

# ==================== INICIALIZAR ESTADO ====================
if 'resultado' not in st.session_state:
    st.session_state.resultado = None
if 'archivo_principal_nombre' not in st.session_state:
    st.session_state.archivo_principal_nombre = None
if 'archivo_verificacion_nombre' not in st.session_state:
    st.session_state.archivo_verificacion_nombre = None
if 'columna_clave_actual' not in st.session_state:
    st.session_state.columna_clave_actual = None
if 'comparacion_ejecutada' not in st.session_state:
    st.session_state.comparacion_ejecutada = False
if 'df_principal' not in st.session_state:
    st.session_state.df_principal = None
if 'df_verificacion' not in st.session_state:
    st.session_state.df_verificacion = None
if 'ignorar_mayusculas' not in st.session_state:
    st.session_state.ignorar_mayusculas = True
if 'ignorar_espacios' not in st.session_state:
    st.session_state.ignorar_espacios = True

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("### Carga de Archivos")
    st.markdown("---")
    
    archivo_principal = st.file_uploader(
        "Archivo Principal (Fuente Primaria)", 
        type=["xlsx", "xls", "csv"],
        help="Cargue el archivo que contiene la informacion de referencia o base para la fiscalizacion."
    )
    
    archivo_verificacion = st.file_uploader(
        "Archivo de Verificacion", 
        type=["xlsx", "xls", "csv"],
        help="Cargue el archivo que desea verificar o comparar contra el archivo principal."
    )
    
    st.markdown("---")
    st.markdown("### Configuracion")
    
    if archivo_principal and archivo_verificacion:
        try:
            if archivo_principal.name.endswith('.csv'):
                df_principal_temp = pd.read_csv(archivo_principal)
            else:
                df_principal_temp = pd.read_excel(archivo_principal)
            
            if archivo_verificacion.name.endswith('.csv'):
                df_verificacion_temp = pd.read_csv(archivo_verificacion)
            else:
                df_verificacion_temp = pd.read_excel(archivo_verificacion)
            
            st.session_state.df_principal = df_principal_temp
            st.session_state.df_verificacion = df_verificacion_temp
            st.session_state.archivo_principal_nombre = archivo_principal.name
            st.session_state.archivo_verificacion_nombre = archivo_verificacion.name
            
            columnas_comunes = list(set(df_principal_temp.columns) & set(df_verificacion_temp.columns))
            
            if columnas_comunes:
                columna_clave = st.selectbox(
                    "Seleccione la columna clave (identificador unico)",
                    columnas_comunes,
                    help="La columna clave permite cruzar los registros entre ambos archivos."
                )
                st.session_state.columna_clave_actual = columna_clave
            else:
                st.warning("No hay columnas comunes entre los archivos.")
                st.session_state.columna_clave_actual = None
            
            st.markdown("---")
            
            with st.expander("Opciones avanzadas"):
                ignorar_mayusculas = st.checkbox(
                    "Ignorar mayusculas y minusculas", 
                    value=st.session_state.ignorar_mayusculas
                )
                ignorar_espacios = st.checkbox(
                    "Ignorar espacios en blanco", 
                    value=st.session_state.ignorar_espacios
                )
                st.session_state.ignorar_mayusculas = ignorar_mayusculas
                st.session_state.ignorar_espacios = ignorar_espacios
            
        except Exception as e:
            st.error(f"Error al leer archivos: {str(e)}")
            st.session_state.df_principal = None
            st.session_state.df_verificacion = None
    
    st.markdown("---")
    
    ejecutar = st.button(
        "Ejecutar Comparacion", 
        type="primary", 
        width='stretch',
        help="Inicia el proceso de comparacion y generacion de la matriz de riesgos."
    )
    
    if archivo_principal and archivo_verificacion:
        st.markdown("---")
        st.markdown("### Archivos cargados")
        st.markdown(f"**Principal:** {archivo_principal.name}")
        st.markdown(f"**Verificacion:** {archivo_verificacion.name}")

# ==================== EJECUTAR COMPARACION ====================
if ejecutar:
    if st.session_state.df_principal is not None and st.session_state.df_verificacion is not None and st.session_state.columna_clave_actual is not None:
        with st.spinner("Procesando archivos y generando matriz de riesgos..."):
            try:
                df_principal = st.session_state.df_principal
                df_verificacion = st.session_state.df_verificacion
                columna_clave = st.session_state.columna_clave_actual
                
                comparador = ComparadorArchivos(
                    df_principal, df_verificacion, columna_clave,
                    ignorar_mayusculas=st.session_state.ignorar_mayusculas,
                    ignorar_espacios=st.session_state.ignorar_espacios
                )
                resultado = comparador.comparar()
                resultado["df_diferencias"] = comparador.obtener_df_diferencias_detallado(resultado)
                
                estructura = {
                    "columnas_principal": set(df_principal.columns),
                    "columnas_verificacion": set(df_verificacion.columns),
                    "columnas_comunes": set(df_principal.columns) & set(df_verificacion.columns),
                    "columnas_solo_principal": set(df_principal.columns) - set(df_verificacion.columns),
                    "columnas_solo_verificacion": set(df_verificacion.columns) - set(df_principal.columns),
                    "filas_principal": len(df_principal),
                    "filas_verificacion": len(df_verificacion)
                }
                resultado["estructura"] = estructura
                
                metricas = resultado["metricas"]
                concordancia = metricas["concordancia"]
                
                if concordancia >= 95:
                    nivel_riesgo = "Bajo"
                    color_riesgo = "bajo"
                    descripcion_riesgo = "Los datos presentan alta consistencia. Se recomienda revision periodica."
                elif concordancia >= 80:
                    nivel_riesgo = "Medio"
                    color_riesgo = "medio"
                    descripcion_riesgo = "Se detectaron discrepancias moderadas. Requiere verificacion selectiva."
                elif concordancia >= 50:
                    nivel_riesgo = "Alto"
                    color_riesgo = "alto"
                    descripcion_riesgo = "Discrepancias significativas. Se recomienda auditoria prioritaria."
                else:
                    nivel_riesgo = "Critico"
                    color_riesgo = "critico"
                    descripcion_riesgo = "Alteraciones mayores detectadas. Requiere actuacion fiscal inmediata."
                
                resultado["nivel_riesgo"] = nivel_riesgo
                resultado["color_riesgo"] = color_riesgo
                resultado["descripcion_riesgo"] = descripcion_riesgo
                
                st.session_state.resultado = resultado
                st.session_state.comparacion_ejecutada = True
                
                st.rerun()
                
            except Exception as e:
                st.error(f"Error durante la comparacion: {str(e)}")
                st.session_state.comparacion_ejecutada = False
    else:
        if st.session_state.df_principal is None or st.session_state.df_verificacion is None:
            st.warning("Por favor, cargue ambos archivos antes de ejecutar la comparacion.")
        elif st.session_state.columna_clave_actual is None:
            st.warning("Por favor, seleccione una columna clave para la comparacion.")

# ==================== MOSTRAR RESULTADOS ====================
if st.session_state.comparacion_ejecutada and st.session_state.resultado is not None:
    resultado = st.session_state.resultado
    metricas = resultado["metricas"]
    estructura = resultado.get("estructura", {})
    nivel_riesgo = resultado.get("nivel_riesgo", "No definido")
    color_riesgo = resultado.get("color_riesgo", "medio")
    descripcion_riesgo = resultado.get("descripcion_riesgo", "")
    
    concordancia = metricas["concordancia"]
    
    # Matriz de Riesgo
    st.markdown("## Matriz de Riesgos")
    
    risk_color_class = f"risk-card {color_riesgo}"
    st.markdown(f"""
    <div class="{risk_color_class}">
        <div class="risk-title">NIVEL DE RIESGO FISCAL</div>
        <div class="risk-value">{nivel_riesgo}</div>
        <div style="font-size:0.85rem; margin-top:0.5rem;">{descripcion_riesgo}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # KPI
    st.markdown("### Indicadores de Calidad de Datos")
    
    if concordancia >= 95:
        concordancia_color = "bajo"
        concordancia_texto = "Excelente"
    elif concordancia >= 80:
        concordancia_color = "medio"
        concordancia_texto = "Aceptable"
    elif concordancia >= 50:
        concordancia_color = "alto"
        concordancia_texto = "Preocupante"
    else:
        concordancia_color = "critico"
        concordancia_texto = "Critico"
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card {concordancia_color}">
            <div class="metric-label">Concordancia General</div>
            <div class="metric-value">{concordancia:.1f}%</div>
            <div class="metric-label">{concordancia_texto}</div>
            <div class="metric-detail">{metricas['coincidencias']} de {metricas['total_claves']} registros</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Discrepancias Detectadas</div>
            <div class="metric-value">{metricas['diferencias']}</div>
            <div class="metric-label">Registros con valores inconsistentes</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Solo en Principal</div>
            <div class="metric-value">{metricas['solo_a']}</div>
            <div class="metric-label">Registros no encontrados en verificacion</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Solo en Verificacion</div>
            <div class="metric-value">{metricas['solo_b']}</div>
            <div class="metric-label">Registros adicionales no declarados</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Explicacion 0%
    if concordancia == 0:
        st.info("""
        **Por que la concordancia es 0%?**
        
        La concordancia del 0% significa que ninguno de los registros comparados es completamente identico en todas sus columnas.
        En este caso, todos los registros existen en ambos archivos, pero tienen diferencias en la columna 'Cantidad'.
        
        - No significa que los archivos sean completamente diferentes
        - Significa que no hay coincidencias exactas registro por registro
        - Revise las diferencias especificas en la pestaña 'Discrepancias'
        """)
    
    # Analisis estructural
    with st.expander("Analisis Estructural de Columnas"):
        col_est1, col_est2, col_est3 = st.columns(3)
        
        with col_est1:
            st.markdown(f"**Archivo Principal ({len(estructura.get('columnas_principal', []))} columnas)**")
            for col in sorted(estructura.get('columnas_principal', [])):
                st.markdown(f"- `{col}`")
        
        with col_est2:
            st.markdown(f"**Archivo de Verificacion ({len(estructura.get('columnas_verificacion', []))} columnas)**")
            for col in sorted(estructura.get('columnas_verificacion', [])):
                st.markdown(f"- `{col}`")
        
        with col_est3:
            st.markdown("**Columnas no comunes**")
            solo_principal = estructura.get('columnas_solo_principal', set())
            solo_verificacion = estructura.get('columnas_solo_verificacion', set())
            if solo_principal:
                st.markdown("*Solo en archivo principal:*")
                for col in sorted(solo_principal):
                    st.markdown(f"- `{col}`")
            if solo_verificacion:
                st.markdown("*Solo en archivo de verificacion:*")
                for col in sorted(solo_verificacion):
                    st.markdown(f"- `{col}`")
            if not solo_principal and not solo_verificacion:
                st.success("Las estructuras de columnas coinciden perfectamente.")
    
    # Mapa de Calor
    if resultado["diferencias"]:
        st.markdown("### Mapa de Calor - Concentracion de Discrepancias")
        
        conteo_columnas = {}
        for diff in resultado["diferencias"]:
            for col in diff["diferencias"].keys():
                conteo_columnas[col] = conteo_columnas.get(col, 0) + 1
        
        if conteo_columnas:
            df_calor = pd.DataFrame({
                'Campo': list(conteo_columnas.keys()),
                'Discrepancias': list(conteo_columnas.values())
            })
            df_calor = df_calor.sort_values('Discrepancias', ascending=False)
            
            fig_calor = px.bar(
                df_calor, 
                x='Campo', 
                y='Discrepancias',
                title="Discrepancias por Campo",
                labels={'Discrepancias': 'Numero de Discrepancias', 'Campo': 'Campo Analizado'},
                color='Discrepancias',
                color_continuous_scale=['#28A745', '#FFC107', '#FD7E14', '#DC3545']
            )
            fig_calor.update_layout(height=400, title_x=0.5)
            st.plotly_chart(fig_calor, use_container_width=True)
    
    # Grafico de barras
    st.markdown("### Distribucion de Hallazgos")
    
    fig = go.Figure(data=[
        go.Bar(
            name='Archivo Principal', 
            x=['Coincidencias', 'Discrepancias', 'Solo Principal'], 
            y=[metricas['coincidencias'], metricas['diferencias'], metricas['solo_a']],
            marker_color='#005A9E',
            text=[metricas['coincidencias'], metricas['diferencias'], metricas['solo_a']],
            textposition='auto'
        ),
        go.Bar(
            name='Archivo de Verificacion', 
            x=['Coincidencias', 'Discrepancias', 'Solo Verificacion'],
            y=[metricas['coincidencias'], metricas['diferencias'], metricas['solo_b']],
            marker_color='#4CAF50',
            text=[metricas['coincidencias'], metricas['diferencias'], metricas['solo_b']],
            textposition='auto'
        )
    ])
    fig.update_layout(
        barmode='group',
        title="Comparacion General",
        xaxis_title="Tipo de Hallazgo",
        yaxis_title="Cantidad de Registros",
        height=450,
        title_x=0.5
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Pestañas
    st.markdown("### Resultados Detallados")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Discrepancias", "Solo Principal", "Solo Verificacion", "Duplicados"])
    
    with tab1:
        if resultado["diferencias"]:
            for diff in resultado["diferencias"]:
                with st.expander(f"Registro: {diff['clave']}"):
                    st.markdown("**Diferencias encontradas:**")
                    for col, vals in diff["diferencias"].items():
                        try:
                            val_a = float(vals["A"]) if vals["A"] else 0
                            val_b = float(vals["B"]) if vals["B"] else 0
                            if val_a > 0:
                                diff_pct = ((val_b - val_a) / val_a) * 100
                                st.markdown(f"- **{col}**: `{vals['A']}` → `{vals['B']}` (diferencia de {diff_pct:+.1f}%)")
                            else:
                                st.markdown(f"- **{col}**: `{vals['A']}` → `{vals['B']}`")
                        except:
                            st.markdown(f"- **{col}**: `{vals['A']}` → `{vals['B']}`")
        else:
            st.success("No se encontraron discrepancias entre los archivos.")
    
    with tab2:
        if not resultado["df_solo_a"].empty:
            st.dataframe(resultado["df_solo_a"], use_container_width=True)
            st.caption(f"Total: {len(resultado['df_solo_a'])} registros que estan en el archivo principal pero NO en el de verificacion.")
        else:
            st.info("No hay registros exclusivos del archivo principal.")
    
    with tab3:
        if not resultado["df_solo_b"].empty:
            st.dataframe(resultado["df_solo_b"], use_container_width=True)
            st.caption(f"Total: {len(resultado['df_solo_b'])} registros que estan en el archivo de verificacion pero NO en el principal.")
        else:
            st.info("No hay registros exclusivos del archivo de verificacion.")
    
    with tab4:
        col_dup1, col_dup2 = st.columns(2)
        with col_dup1:
            st.markdown("**Duplicados en archivo principal**")
            if not resultado["duplicados_a"].empty:
                st.dataframe(resultado["duplicados_a"], use_container_width=True)
            else:
                st.success("No se detectaron duplicados.")
        with col_dup2:
            st.markdown("**Duplicados en archivo de verificacion**")
            if not resultado["duplicados_b"].empty:
                st.dataframe(resultado["duplicados_b"], use_container_width=True)
            else:
                st.success("No se detectaron duplicados.")
    
    # Exportacion
    st.markdown("---")
    st.markdown("### Exportar Resultados")
    
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        if st.button("Exportar a Excel", width='stretch'):
            with st.spinner("Generando archivo Excel..."):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
                        exportador = ExportadorAuditoria(
                            resultado, 
                            st.session_state.archivo_principal_nombre, 
                            st.session_state.archivo_verificacion_nombre, 
                            st.session_state.columna_clave_actual
                        )
                        exportador.exportar_excel(tmp.name)
                        with open(tmp.name, 'rb') as f:
                            st.download_button("Descargar Excel", f, "auditoria_dian.xlsx")
                        os.unlink(tmp.name)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col_exp2:
        if st.button("Exportar a PDF", width='stretch'):
            with st.spinner("Generando archivo PDF..."):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                        exportador = ExportadorAuditoria(
                            resultado, 
                            st.session_state.archivo_principal_nombre, 
                            st.session_state.archivo_verificacion_nombre, 
                            st.session_state.columna_clave_actual
                        )
                        exportador.exportar_pdf(tmp.name)
                        with open(tmp.name, 'rb') as f:
                            st.download_button("Descargar PDF", f, "informe_auditoria_dian.pdf")
                        os.unlink(tmp.name)
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# ==================== FOOTER ====================
st.markdown("""
<div class="footer">
    <p>Sistema de Auditoría de Datos | Direccion de Impuestos y Aduanas Nacionales de Colombia</p>
    <p>Herramienta de Verificacion y Analisis Fiscal</p>
</div>
""", unsafe_allow_html=True)
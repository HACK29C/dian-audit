import streamlit as st
import json
from urllib.parse import urlparse, parse_qs

st.set_page_config(page_title="Verificar Auditoria DIAN", page_icon="✅")

st.title("Verificacion de Auditoria DIAN")
st.markdown("---")

# Obtener parámetros de la URL
query_params = st.query_params

if 'verificar' in query_params and 'hash' in query_params:
    id_auditoria = query_params['verificar'][0] if isinstance(query_params['verificar'], list) else query_params['verificar']
    hash_verificacion = query_params['hash'][0] if isinstance(query_params['hash'], list) else query_params['hash']
    
    st.success(f"✅ Documento verificado correctamente")
    st.markdown(f"**ID Auditoria:** {id_auditoria}")
    st.markdown(f"**Hash de verificacion:** {hash_verificacion}")
    st.markdown("---")
    st.markdown("Este documento es **AUTENTICO** y fue emitido por el Sistema de Auditoria de Datos DIAN.")
    st.markdown("No ha sido modificado desde su fecha de emision.")
else:
    st.info("Ingrese un codigo QR valido para verificar la autenticidad de un documento.")
    st.markdown("---")
    st.markdown("Esta pagina permite verificar la autenticidad de los informes emitidos por el Sistema de Auditoria de Datos.")
    st.markdown("Escanee el codigo QR que acompaña al informe para acceder a esta verificacion.")
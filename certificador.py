import hashlib
import json
import qrcode
from io import BytesIO
import pandas as pd
from datetime import datetime
import uuid

class CertificadorAuditoria:
    def __init__(self, resultado, nombre_archivo_a, nombre_archivo_b, columna_clave):
        self.resultado = resultado
        self.nombre_archivo_a = nombre_archivo_a
        self.nombre_archivo_b = nombre_archivo_b
        self.columna_clave = columna_clave
        self.id_auditoria = str(uuid.uuid4())[:8].upper()
        self.fecha_emision = datetime.now().isoformat()
        self.hash_auditoria = self._calcular_hash()
        
    def _calcular_hash(self):
        """Calcula hash SHA-256 de los resultados de auditoría"""
        # Crear resumen de la auditoría
        resumen = {
            "id_auditoria": self.id_auditoria,
            "fecha_emision": self.fecha_emision,
            "archivo_principal": self.nombre_archivo_a,
            "archivo_verificacion": self.nombre_archivo_b,
            "columna_clave": self.columna_clave,
            "metricas": self.resultado["metricas"]
        }
        
        # Agregar diferencias (solo primeras 10 para no hacer hash enorme)
        if self.resultado["diferencias"]:
            diferencias_resumidas = []
            for diff in self.resultado["diferencias"][:10]:
                diferencias_resumidas.append({
                    "clave": diff["clave"],
                    "campos": list(diff["diferencias"].keys())
                })
            resumen["diferencias_muestra"] = diferencias_resumidas
        
        # Convertir a JSON y calcular hash
        json_str = json.dumps(resumen, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()[:16]
    
    def obtener_metadata_auditoria(self):
        """Obtiene los metadatos completos de la auditoría"""
        metricas = self.resultado["metricas"]
        
        # Determinar nivel de riesgo
        concordancia = metricas["concordancia"]
        if concordancia >= 95:
            nivel_riesgo = "BAJO"
            color = "verde"
        elif concordancia >= 80:
            nivel_riesgo = "MEDIO"
            color = "amarillo"
        elif concordancia >= 50:
            nivel_riesgo = "ALTO"
            color = "naranja"
        else:
            nivel_riesgo = "CRITICO"
            color = "rojo"
        
        return {
            "id_auditoria": self.id_auditoria,
            "fecha_emision": self.fecha_emision,
            "fecha_formateada": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "archivo_principal": self.nombre_archivo_a,
            "archivo_verificacion": self.nombre_archivo_b,
            "columna_clave": self.columna_clave,
            "hash_auditoria": self.hash_auditoria,
            "nivel_riesgo": nivel_riesgo,
            "color_riesgo": color,
            "concordancia": concordancia,
            "total_registros": metricas["total_claves"],
            "coincidencias": metricas["coincidencias"],
            "diferencias": metricas["diferencias"],
            "solo_principal": metricas["solo_a"],
            "solo_verificacion": metricas["solo_b"],
            "duplicados_principal": metricas["duplicados_a"],
            "duplicados_verificacion": metricas["duplicados_b"]
        }
    
    def generar_qr(self):
        """Genera código QR con la información de certificación"""
        metadata = self.obtener_metadata_auditoria()
        
        # URL de verificacion
        # Para pruebas locales:
        base_url = "https://audit-verifica.streamlit.app"
        # Para produccion en Streamlit Cloud (descomentar cuando esté desplegado):
        # base_url = "https://hack29c-dian-audit.streamlit.app"
        
        verificacion_url = f"{base_url}/verificar?id={self.id_auditoria}&hash={self.hash_auditoria}"
        
        # Datos para el QR
        datos_qr = {
            "id": self.id_auditoria,
            "hash": self.hash_auditoria,
            "fecha": metadata["fecha_formateada"],
            "concordancia": f"{metadata['concordancia']:.1f}%",
            "riesgo": metadata["nivel_riesgo"],
            "url_verificacion": verificacion_url
        }
        
        # Generar QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=8,
            border=4
        )
        qr.add_data(json.dumps(datos_qr))
        qr.make(fit=True)
        
        # Crear imagen
        img = qr.make_image(fill_color="#005A9E", back_color="white")
        
        # Guardar en buffer
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        
        return buffer
    
    def generar_certificado_texto(self):
        """Genera texto de certificación para incluir en PDF"""
        metadata = self.obtener_metadata_auditoria()
        
        certificado = f"""
CERTIFICADO DE AUDITORIA - DIAN
═══════════════════════════════════════════════════════════

IDENTIFICADOR UNICO: {metadata['id_auditoria']}
FECHA DE EMISION: {metadata['fecha_formateada']}
HASH DE VERIFICACION: {metadata['hash_auditoria']}

ARCHIVOS ANALIZADOS:
├── Archivo Principal: {metadata['archivo_principal']}
└── Archivo Verificacion: {metadata['archivo_verificacion']}

RESULTADOS DE LA AUDITORIA:
├── Nivel de Riesgo: {metadata['nivel_riesgo']}
├── Concordancia: {metadata['concordancia']:.1f}%
├── Total Registros: {metadata['total_registros']}
├── Coincidencias: {metadata['coincidencias']}
├── Discrepancias: {metadata['diferencias']}
├── Solo en Principal: {metadata['solo_principal']}
└── Solo en Verificacion: {metadata['solo_verificacion']}

ESTADO DE VALIDACION: AUTENTICO
Este documento ha sido generado por el Sistema de Auditoria de Datos DIAN.
Cualquier modificacion posterior invalida la certificacion.

Verifique la autenticidad escaneando el codigo QR adjunto
o visitando la pagina de verificacion.

───────────────────────────────────────────────────────────
DIAN - Direccion de Impuestos y Aduanas Nacionales de Colombia
Sistema de Verificacion y Analisis Fiscal
"""
        return certificado
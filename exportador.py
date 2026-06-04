import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from io import BytesIO
import os

class ExportadorAuditoria:
    def __init__(self, resultado, nombre_a, nombre_b, columna_clave):
        self.resultado = resultado
        self.nombre_a = nombre_a
        self.nombre_b = nombre_b
        self.columna_clave = columna_clave
        self.metricas = resultado["metricas"]
    
    def exportar_excel(self, ruta_archivo):
        """Exporta todos los resultados a un archivo Excel con múltiples hojas"""
        with pd.ExcelWriter(ruta_archivo, engine='openpyxl') as writer:
            # Hoja de resumen
            resumen = pd.DataFrame([
                ["Métrica", "Valor"],
                ["Concordancia", f"{self.metricas['concordancia']:.2f}%"],
                ["Coincidencias", self.metricas["coincidencias"]],
                ["Diferencias", self.metricas["diferencias"]],
                ["Solo en Archivo Principal", self.metricas["solo_a"]],
                ["Solo en Archivo Verificacion", self.metricas["solo_b"]],
                ["Duplicados en Principal", self.metricas["duplicados_a"]],
                ["Duplicados en Verificacion", self.metricas["duplicados_b"]],
                ["Total claves unicas", self.metricas["total_claves"]]
            ])
            resumen.to_excel(writer, sheet_name="Resumen", index=False)
            
            # Solo Archivo Principal
            if not self.resultado["df_solo_a"].empty:
                self.resultado["df_solo_a"].to_excel(writer, sheet_name="Solo Archivo Principal", index=False)
            
            # Solo Archivo Verificacion
            if not self.resultado["df_solo_b"].empty:
                self.resultado["df_solo_b"].to_excel(writer, sheet_name="Solo Archivo Verificacion", index=False)
            
            # Diferencias detalladas
            if "df_diferencias" in self.resultado and not self.resultado["df_diferencias"].empty:
                self.resultado["df_diferencias"].to_excel(writer, sheet_name="Diferencias Detalladas", index=False)
            
            # Duplicados
            if not self.resultado["duplicados_a"].empty:
                self.resultado["duplicados_a"].to_excel(writer, sheet_name="Duplicados Archivo Principal", index=False)
            if not self.resultado["duplicados_b"].empty:
                self.resultado["duplicados_b"].to_excel(writer, sheet_name="Duplicados Archivo Verificacion", index=False)
    
    def exportar_pdf(self, ruta_archivo):
        """Genera informe PDF profesional (versión estándar)"""
        doc = SimpleDocTemplate(ruta_archivo, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Título
        titulo_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, spaceAfter=30, textColor=colors.HexColor('#005A9E'))
        story.append(Paragraph("Informe de Auditoria de Datos - DIAN", titulo_style))
        story.append(Spacer(1, 0.3*cm))
        
        # Metadatos
        story.append(Paragraph(f"<b>Archivo Principal:</b> {self.nombre_a}", styles['Normal']))
        story.append(Paragraph(f"<b>Archivo de Verificacion:</b> {self.nombre_b}", styles['Normal']))
        story.append(Paragraph(f"<b>Columna clave:</b> {self.columna_clave}", styles['Normal']))
        story.append(Spacer(1, 0.5*cm))
        
        # Tabla de métricas
        data = [["Metrica", "Valor", "Indicador"]]
        
        concordancia = self.metricas["concordancia"]
        if concordancia >= 95:
            indicador = "Excelente"
            color_fondo = colors.HexColor('#28A745')
        elif concordancia >= 80:
            indicador = "Media"
            color_fondo = colors.HexColor('#FFC107')
        elif concordancia >= 50:
            indicador = "Alta"
            color_fondo = colors.HexColor('#FD7E14')
        else:
            indicador = "Critica"
            color_fondo = colors.HexColor('#DC3545')
        
        data.append(["Concordancia", f"{concordancia:.2f}%", indicador])
        data.append(["Coincidencias", str(self.metricas["coincidencias"]), ""])
        data.append(["Diferencias", str(self.metricas["diferencias"]), ""])
        data.append(["Solo en Principal", str(self.metricas["solo_a"]), ""])
        data.append(["Solo en Verificacion", str(self.metricas["solo_b"]), ""])
        
        tabla = Table(data, colWidths=[5*cm, 3*cm, 5*cm])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#005A9E')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        story.append(tabla)
        
        doc.build(story)
    
    def exportar_pdf_con_certificado(self, ruta_archivo, qr_buffer, certificado_texto):
        """Genera informe PDF profesional con certificado digital y QR"""
        doc = SimpleDocTemplate(ruta_archivo, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Estilo personalizado para el título
        titulo_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=20, textColor=colors.HexColor('#005A9E'))
        story.append(Paragraph("INFORME DE AUDITORIA - DIAN", titulo_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Extraer ID de auditoría del texto del certificado
        try:
            id_auditoria = certificado_texto.split('IDENTIFICADOR UNICO:')[1].split('FECHA')[0].strip()
            story.append(Paragraph(f"<b>ID Auditoria:</b> {id_auditoria}", styles['Normal']))
        except:
            story.append(Paragraph(f"<b>ID Auditoria:</b> No disponible", styles['Normal']))
        
        story.append(Spacer(1, 0.3*cm))
        
        # Tabla de métricas con colores según riesgo
        metricas = self.metricas
        concordancia = metricas["concordancia"]
        
        if concordancia >= 95:
            nivel_riesgo = "BAJO"
            color_riesgo = colors.HexColor('#28A745')
        elif concordancia >= 80:
            nivel_riesgo = "MEDIO"
            color_riesgo = colors.HexColor('#FFC107')
        elif concordancia >= 50:
            nivel_riesgo = "ALTO"
            color_riesgo = colors.HexColor('#FD7E14')
        else:
            nivel_riesgo = "CRITICO"
            color_riesgo = colors.HexColor('#DC3545')
        
        data = [
            ["Metrica", "Valor", "Estado"],
            ["Concordancia", f"{concordancia:.1f}%", nivel_riesgo],
            ["Coincidencias", str(metricas["coincidencias"]), ""],
            ["Discrepancias", str(metricas["diferencias"]), ""],
            ["Solo en Principal", str(metricas["solo_a"]), ""],
            ["Solo en Verificacion", str(metricas["solo_b"]), ""],
            ["Duplicados en Principal", str(metricas["duplicados_a"]), ""],
            ["Duplicados en Verificacion", str(metricas["duplicados_b"]), ""],
            ["Total claves", str(metricas["total_claves"]), ""]
        ]
        
        tabla = Table(data, colWidths=[5*cm, 3*cm, 5*cm])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#005A9E')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (2,1), (2,1), color_riesgo),
            ('TEXTCOLOR', (2,1), (2,1), colors.white),
        ]))
        story.append(tabla)
        story.append(Spacer(1, 0.5*cm))
        
        # Código QR
        if qr_buffer:
            qr_img = Image(BytesIO(qr_buffer.getvalue()), width=3.5*cm, height=3.5*cm)
            story.append(qr_img)
            story.append(Spacer(1, 0.3*cm))
            story.append(Paragraph("<i>Escanee este codigo QR para verificar la autenticidad del informe</i>", styles['Italic']))
        
        story.append(Spacer(1, 0.5*cm))
        
        # Agregar el texto del certificado
        story.append(Paragraph("CERTIFICADO DE AUTENTICIDAD", ParagraphStyle('CertTitle', parent=styles['Heading2'], fontSize=12, spaceAfter=10, textColor=colors.HexColor('#005A9E'))))
        
        # Formatear el texto del certificado para ReportLab
        lineas_certificado = certificado_texto.split('\n')
        for linea in lineas_certificado[:25]:  # Limitar a 25 líneas
            if linea.strip():
                if '═' in linea:
                    continue
                story.append(Paragraph(linea, styles['Normal']))
                story.append(Spacer(1, 0.1*cm))
        
        doc.build(story)
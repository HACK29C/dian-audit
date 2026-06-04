import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
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
                ["Solo en Archivo A", self.metricas["solo_a"]],
                ["Solo en Archivo B", self.metricas["solo_b"]],
                ["Duplicados en A", self.metricas["duplicados_a"]],
                ["Duplicados en B", self.metricas["duplicados_b"]],
                ["Total claves únicas", self.metricas["total_claves"]]
            ])
            resumen.to_excel(writer, sheet_name="Resumen", index=False)
            
            # Solo Archivo A
            if not self.resultado["df_solo_a"].empty:
                self.resultado["df_solo_a"].to_excel(writer, sheet_name="Solo Archivo A", index=False)
            
            # Solo Archivo B
            if not self.resultado["df_solo_b"].empty:
                self.resultado["df_solo_b"].to_excel(writer, sheet_name="Solo Archivo B", index=False)
            
            # Diferencias detalladas
            if "df_diferencias" in self.resultado and not self.resultado["df_diferencias"].empty:
                self.resultado["df_diferencias"].to_excel(writer, sheet_name="Diferencias Detalladas", index=False)
            
            # Duplicados
            if not self.resultado["duplicados_a"].empty:
                self.resultado["duplicados_a"].to_excel(writer, sheet_name="Duplicados Archivo A", index=False)
            if not self.resultado["duplicados_b"].empty:
                self.resultado["duplicados_b"].to_excel(writer, sheet_name="Duplicados Archivo B", index=False)
    
    def exportar_pdf(self, ruta_archivo):
        """Genera informe PDF profesional"""
        doc = SimpleDocTemplate(ruta_archivo, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Título
        titulo_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, spaceAfter=30)
        story.append(Paragraph("Informe de Auditoría de Datos", titulo_style))
        
        # Metadatos
        story.append(Paragraph(f"<b>Archivo A:</b> {self.nombre_a}", styles['Normal']))
        story.append(Paragraph(f"<b>Archivo B:</b> {self.nombre_b}", styles['Normal']))
        story.append(Paragraph(f"<b>Columna clave:</b> {self.columna_clave}", styles['Normal']))
        story.append(Spacer(1, 0.5*cm))
        
        # Tabla de métricas
        data = [["Métrica", "Valor", "Indicador"]]
        
        concordancia = self.metricas["concordancia"]
        indicador = "Excelente" if concordancia >= 95 else "Media" if concordancia >= 80 else "Baja"
        data.append(["Concordancia", f"{concordancia:.2f}%", indicador])
        data.append(["Coincidencias", str(self.metricas["coincidencias"]), ""])
        data.append(["Diferencias", str(self.metricas["diferencias"]), ""])
        data.append(["Solo en Archivo A", str(self.metricas["solo_a"]), ""])
        data.append(["Solo en Archivo B", str(self.metricas["solo_b"]), ""])
        
        tabla = Table(data, colWidths=[5*cm, 3*cm, 5*cm])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        story.append(tabla)
        
        doc.build(story)
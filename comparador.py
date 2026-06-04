import pandas as pd
import numpy as np

class ComparadorArchivos:
    def __init__(self, df_a, df_b, columna_clave, ignorar_mayusculas=True, ignorar_espacios=True):
        self.df_a = df_a.copy()
        self.df_b = df_b.copy()
        self.columna_clave = columna_clave
        self.ignorar_mayusculas = ignorar_mayusculas
        self.ignorar_espacios = ignorar_espacios
        
        # Normalizar columna clave
        self._normalizar_columna_clave()
        
    def _normalizar_columna_clave(self):
        """Normaliza la columna clave para comparación"""
        for df in [self.df_a, self.df_b]:
            df[self.columna_clave] = df[self.columna_clave].astype(str)
            if self.ignorar_espacios:
                df[self.columna_clave] = df[self.columna_clave].str.strip()
            if self.ignorar_mayusculas:
                df[self.columna_clave] = df[self.columna_clave].str.upper()
    
    def _detectar_duplicados(self, df, nombre):
        """Detecta registros duplicados por columna clave"""
        duplicados = df[df.duplicated(subset=[self.columna_clave], keep=False)]
        if len(duplicados) > 0:
            conteo = duplicados.groupby(self.columna_clave).size().reset_index(name='veces_repetido')
            return conteo
        return pd.DataFrame(columns=[self.columna_clave, 'veces_repetido'])
    
    def comparar(self):
        """Ejecuta comparación completa"""
        # Conjuntos de claves
        claves_a = set(self.df_a[self.columna_clave])
        claves_b = set(self.df_b[self.columna_clave])
        
        # Identificación de registros
        solo_a = list(claves_a - claves_b)
        solo_b = list(claves_b - claves_a)
        comunes = list(claves_a & claves_b)
        
        # DataFrames de faltantes
        df_solo_a = self.df_a[self.df_a[self.columna_clave].isin(solo_a)]
        df_solo_b = self.df_b[self.df_b[self.columna_clave].isin(solo_b)]
        
        # Comparación de registros comunes
        df_comunes_a = self.df_a[self.df_a[self.columna_clave].isin(comunes)].set_index(self.columna_clave).sort_index()
        df_comunes_b = self.df_b[self.df_b[self.columna_clave].isin(comunes)].set_index(self.columna_clave).sort_index()
        
        # Detectar diferencias
        diferencias = []
        coincidencias = []
        
        for clave in comunes:
            row_a = df_comunes_a.loc[clave]
            row_b = df_comunes_b.loc[clave]
            
            # Comparar todas las columnas excepto la clave
            columnas_a = [c for c in df_comunes_a.columns if c != self.columna_clave]
            
            diferencias_encontradas = {}
            es_igual = True
            
            for col in columnas_a:
                if col in df_comunes_b.columns:
                    val_a = str(row_a[col]) if pd.notna(row_a[col]) else ""
                    val_b = str(row_b[col]) if pd.notna(row_b[col]) else ""
                    
                    if val_a != val_b:
                        es_igual = False
                        diferencias_encontradas[col] = {"A": val_a, "B": val_b}
            
            if es_igual:
                coincidencias.append(clave)
            else:
                diferencias.append({
                    "clave": clave,
                    "diferencias": diferencias_encontradas,
                    "fila_a": row_a.to_dict(),
                    "fila_b": row_b.to_dict()
                })
        
        # Detectar duplicados
        duplicados_a = self._detectar_duplicados(self.df_a, "Archivo A")
        duplicados_b = self._detectar_duplicados(self.df_b, "Archivo B")
        
        # Métricas
        total_claves = len(claves_a | claves_b)
        metricas = {
            "total_claves": total_claves,
            "coincidencias": len(coincidencias),
            "diferencias": len(diferencias),
            "solo_a": len(solo_a),
            "solo_b": len(solo_b),
            "duplicados_a": len(duplicados_a),
            "duplicados_b": len(duplicados_b),
            "concordancia": (len(coincidencias) / total_claves * 100) if total_claves > 0 else 0
        }
        
        return {
            "metricas": metricas,
            "coincidencias": coincidencias,
            "diferencias": diferencias,
            "df_solo_a": df_solo_a,
            "df_solo_b": df_solo_b,
            "duplicados_a": duplicados_a,
            "duplicados_b": duplicados_b,
            "df_comunes": df_comunes_a
        }
    
    def obtener_df_diferencias_detallado(self, resultado):
        """Genera DataFrame detallado de diferencias para exportar"""
        if not resultado["diferencias"]:
            return pd.DataFrame()
        
        registros = []
        for diff in resultado["diferencias"]:
            for col, vals in diff["diferencias"].items():
                registros.append({
                    "Clave": diff["clave"],
                    "Columna": col,
                    "Valor Archivo A": vals["A"],
                    "Valor Archivo B": vals["B"],
                    "Estado": "Diferente"
                })
        return pd.DataFrame(registros)
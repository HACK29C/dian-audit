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
    
    def _normalizar_valor(self, valor):
        """Normaliza un valor para comparación (maneja nulos y formatos numéricos)"""
        if pd.isna(valor):
            return ""
        
        # Si es número, convertir a float y luego a string sin decimales innecesarios
        if isinstance(valor, (int, float)):
            if isinstance(valor, float) and valor.is_integer():
                return str(int(valor))
            return str(valor)
        
        valor_str = str(valor)
        if self.ignorar_espacios:
            valor_str = valor_str.strip()
        if self.ignorar_mayusculas:
            valor_str = valor_str.upper()
        return valor_str
    
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
        
        # Para registros comunes, tomar el PRIMER registro de cada clave (en caso de duplicados)
        df_comunes_a = self.df_a[self.df_a[self.columna_clave].isin(comunes)].drop_duplicates(subset=[self.columna_clave], keep='first')
        df_comunes_b = self.df_b[self.df_b[self.columna_clave].isin(comunes)].drop_duplicates(subset=[self.columna_clave], keep='first')
        
        # Crear diccionarios (ahora con índices únicos)
        dict_a = df_comunes_a.set_index(self.columna_clave).to_dict('index')
        dict_b = df_comunes_b.set_index(self.columna_clave).to_dict('index')
        
        # Detectar diferencias
        diferencias = []
        coincidencias = []
        
        # Obtener todas las columnas excepto la clave
        columnas_a = [c for c in self.df_a.columns if c != self.columna_clave]
        columnas_b = [c for c in self.df_b.columns if c != self.columna_clave]
        columnas_comunes = list(set(columnas_a) & set(columnas_b))
        
        for clave in comunes:
            row_a = dict_a.get(clave, {})
            row_b = dict_b.get(clave, {})
            
            diferencias_encontradas = {}
            es_igual = True
            
            for col in columnas_comunes:
                # Obtener valores normalizados
                val_a = self._normalizar_valor(row_a.get(col))
                val_b = self._normalizar_valor(row_b.get(col))
                
                if val_a != val_b:
                    es_igual = False
                    diferencias_encontradas[col] = {
                        "A": val_a if val_a else "(vacio)", 
                        "B": val_b if val_b else "(vacio)"
                    }
            
            if es_igual:
                coincidencias.append(clave)
            else:
                # Obtener filas completas originales
                fila_a_original = self.df_a[self.df_a[self.columna_clave] == clave].iloc[0].to_dict() if len(self.df_a[self.df_a[self.columna_clave] == clave]) > 0 else {}
                fila_b_original = self.df_b[self.df_b[self.columna_clave] == clave].iloc[0].to_dict() if len(self.df_b[self.df_b[self.columna_clave] == clave]) > 0 else {}
                
                diferencias.append({
                    "clave": clave,
                    "diferencias": diferencias_encontradas,
                    "fila_a": fila_a_original,
                    "fila_b": fila_b_original
                })
        
        # Detectar duplicados
        duplicados_a = self._detectar_duplicados(self.df_a, "Archivo A")
        duplicados_b = self._detectar_duplicados(self.df_b, "Archivo B")
        
        # Métricas
        total_claves = len(claves_a | claves_b)
        coincidencias_count = len(coincidencias)
        diferencias_count = len(diferencias)
        
        concordancia = (coincidencias_count / total_claves * 100) if total_claves > 0 else 0
        
        metricas = {
            "total_claves": total_claves,
            "coincidencias": coincidencias_count,
            "diferencias": diferencias_count,
            "solo_a": len(solo_a),
            "solo_b": len(solo_b),
            "duplicados_a": len(duplicados_a),
            "duplicados_b": len(duplicados_b),
            "concordancia": concordancia
        }
        
        return {
            "metricas": metricas,
            "coincidencias": coincidencias,
            "diferencias": diferencias,
            "df_solo_a": df_solo_a,
            "df_solo_b": df_solo_b,
            "duplicados_a": duplicados_a,
            "duplicados_b": duplicados_b,
            "df_comunes": None
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
                    "Valor Archivo Principal": vals["A"],
                    "Valor Archivo Verificacion": vals["B"],
                    "Estado": "Diferente"
                })
        return pd.DataFrame(registros)
"""
Script para crear e insertar datos iniciales en la base de datos PostgreSQL de AWS RDS desde tu entorno local.
Ejecución:
    python carga_datos.py
"""

import sys
import psycopg2
import streamlit as st
import os
from pathlib import Path
import pandas as pd

BASE_DIR = Path().resolve()
print (BASE_DIR)


# Carpetas de salida
OUTPUT_CSV_DIR = BASE_DIR / 'sheets' / 'csv'
OUTPUT_CSV_DIR.mkdir(parents=True, exist_ok=True)
print (OUTPUT_CSV_DIR)

# Configura las credenciales de tu instancia AWS RDS aquí o pásalas por argumento
if "postgres" in st.secrets:
    RDS_HOST = st.secrets["postgres"]["host"]
    RDS_PORT = st.secrets["postgres"].get("port", 5432)
    RDS_DB = st.secrets["postgres"]["database"]
    RDS_USER = st.secrets["postgres"]["user"]
    RDS_PASSWORD = st.secrets["postgres"]["password"]

    print(f"RDS_HOST {RDS_HOST}")
    print(f"RDS_PORT {RDS_PORT}")
    print(f"RDS_DB {RDS_DB}")
    print(f"RDS_USER {RDS_USER}")
    print(f"RDS_PASSWORD {RDS_PASSWORD}")

def cargar_csv_en_rds(nombre_archivo):
    ruta_csv = OUTPUT_CSV_DIR / nombre_archivo
    
    if not ruta_csv.exists():
        print(f"Error: No se encuentra el archivo CSV en la ruta: {ruta_csv}")
        print(f"Por favor, coloca tu archivo '{nombre_archivo}' dentro de la carpeta '{OUTPUT_CSV_DIR}'.")
        return
        
    print(f"Leyendo archivo CSV: {ruta_csv}")
    try:
        # Leemos el CSV indicando que no tiene encabezado (header=None) y asignando los nombres de las columnas
        columnas = ['master_box', 'codigo_barras', 'codigo_pedido', 'letra_apellido', 'desc_master_box', 'fecha_encontrado']
        # Usamos dtype=str para no perder los ceros a la izquierda (000...) de los códigos de barras
        # Usamos index_col=False y usecols=range(7) para que Pandas no confunda la primera columna con un índice si sobran comas al final
        df = pd.read_csv(ruta_csv, header=None, names=columnas, dtype=str, index_col=False, usecols=range(6))
        
        # Eliminamos las filas que estén completamente vacías o que no tengan 'master_box' (ya que es PRIMARY KEY y no puede ser nulo)
        df = df.dropna(subset=['master_box'])
        
        # Reemplazamos los valores nulos/vacíos por None (NULL en base de datos)
        df = df.where(pd.notnull(df), None)
        
        print("Conectando a AWS RDS PostgreSQL...")
        conn = psycopg2.connect(
            host=RDS_HOST,
            port=RDS_PORT,
            dbname=RDS_DB,
            user=RDS_USER,
            password=RDS_PASSWORD,
            connect_timeout=10
        )
        print("¡Conexión a AWS RDS exitosa!")

        with conn.cursor() as cur:
            # Crear tabla si no existe
            print("Verificando tabla 'barcode_cazafantasmas' e índices...")
            cur.execute("""
                DROP TABLE IF EXISTS barcode_cazafantasmas;
                
                CREATE TABLE barcode_cazafantasmas (
                    master_box        VARCHAR(20),
                    codigo_barras     VARCHAR(50) PRIMARY KEY,
                    codigo_pedido     VARCHAR(50),
                    letra_apellido    VARCHAR(50),
                    desc_master_box   VARCHAR(500),
                    fecha_encontrado  TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_codigo_barras ON barcode_cazafantasmas (codigo_barras);
                CREATE INDEX IF NOT EXISTS idx_codigo_secundario ON barcode_cazafantasmas (codigo_pedido);
            """)

            print(f"Insertando {len(df)} productos en la base de datos...")
            
            for index, row in df.iterrows():
                
                def get_val(col_name):
                    val = row.get(col_name)
                    if pd.isna(val) or val == "":
                        return None
                    # Limpiamos espacios en blanco o caracteres invisibles por seguridad
                    return str(val).strip()
                    
                print(f"---> Fila {index}: master_box es '{get_val('master_box')}' y codigo_barras es '{get_val('codigo_barras')}'")

                cur.execute("""
                    INSERT INTO barcode_cazafantasmas (master_box, codigo_barras, codigo_pedido, letra_apellido, desc_master_box, fecha_encontrado)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """, (
                    str(get_val("master_box")),
                    get_val("codigo_barras"),
                    get_val("codigo_pedido"),
                    get_val("letra_apellido"),
                    get_val("desc_master_box"),
                    get_val("fecha_encontrado")
                ))
            
            conn.commit()
            print("¡Carga masiva desde CSV completada con éxito!")

        conn.close()
    except Exception as e:
        print(f"Error durante la carga en AWS RDS: {e}")

if __name__ == "__main__":
    # Nombre de tu archivo CSV (Cámbialo si es diferente)
    nombre_del_csv = "carga_27072026.csv"
    cargar_csv_en_rds(nombre_del_csv)

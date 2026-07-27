import os
import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st
from datetime import datetime

def get_db_config():
    """Obtiene los parámetros de conexión desde st.secrets o variables de entorno."""
    if "postgres" in st.secrets:
        return {
            "host": st.secrets["postgres"]["host"],
            "port": st.secrets["postgres"].get("port", 5432),
            "database": st.secrets["postgres"]["database"],
            "user": st.secrets["postgres"]["user"],
            "password": st.secrets["postgres"]["password"],
            "connect_timeout": 5
        }
    return None

def get_connection():
    """Establece conexión con la base de datos PostgreSQL de AWS RDS."""
    config = get_db_config()
    if not config:
        return None
    try:
        conn = psycopg2.connect(**config)
        return conn
    except Exception as e:
        print(f"Error conectando a AWS RDS PostgreSQL: {e}")
        return None

def init_db():
    """Crea la tabla 'barcode_cazafantasmas' en AWS RDS si no existe."""
    conn = get_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS barcode_cazafantasmas (
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
            conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")
        if conn:
            conn.close()
        return False

def buscar_codigo(codigo: str):
    """
    Busca un código de barras en la base de datos de AWS RDS PostgreSQL.
    Si no hay conexión con RDS, busca en la base de datos demo local.
    """
    if not codigo:
        return None, "VACIO"

    codigo_limpio = codigo.strip()

    # Intentar buscar en AWS RDS PostgreSQL
    conn = get_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT master_box, codigo_barras, codigo_pedido, letra_apellido, desc_master_box, fecha_encontrado
                    FROM barcode_cazafantasmas
                    WHERE codigo_barras = %s OR codigo_pedido = %s
                    LIMIT 1;
                """, (codigo_limpio, codigo_limpio))
                resultado = cur.fetchone()

                if resultado:
                    if resultado.get('fecha_encontrado'):
                        resultado['ya_encontrado'] = True
                    else:
                        resultado['ya_encontrado'] = False
                        cur.execute("""
                            UPDATE barcode_cazafantasmas 
                            SET fecha_encontrado = CURRENT_TIMESTAMP 
                            WHERE codigo_barras = %s OR codigo_pedido = %s
                        """, (codigo_limpio, codigo_limpio))
                        conn.commit()
                        resultado['fecha_encontrado'] = datetime.now()

            conn.close()
            if resultado:
                return dict(resultado), "RDS"
            else:
                return None, "RDS"
        except Exception as e:
            print(f"Error en consulta SQL RDS: {e}")
            if conn:
                conn.close()

    return None, "NO_ENCONTRADO"

def obtener_progreso_master_box(master_box: str):
    """
    Devuelve el estado de progreso de una Master Box: total de códigos y cuántos han sido encontrados.
    """
    if not master_box:
        return None
        
    master_box_limpio = master_box.strip()
    conn = get_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Contar total
                cur.execute("SELECT COUNT(*) as total FROM barcode_cazafantasmas WHERE master_box = %s;", (master_box_limpio,))
                total = cur.fetchone()['total']
                
                if total == 0:
                    conn.close()
                    return None
                    
                # Obtener descripción
                cur.execute("SELECT desc_master_box FROM barcode_cazafantasmas WHERE master_box = %s LIMIT 1;", (master_box_limpio,))
                desc_row = cur.fetchone()
                desc_master_box = desc_row['desc_master_box'] if desc_row else ""
                    
                # Contar encontrados
                cur.execute("SELECT COUNT(*) as encontrados FROM barcode_cazafantasmas WHERE master_box = %s AND fecha_encontrado IS NOT NULL;", (master_box_limpio,))
                encontrados = cur.fetchone()['encontrados']
                
            conn.close()
            return {
                "master_box": master_box_limpio,
                "desc_master_box": desc_master_box,
                "total": total,
                "encontrados": encontrados,
                "restantes": total - encontrados
            }
        except Exception as e:
            print(f"Error consultando progreso Master Box en RDS: {e}")
            if conn:
                conn.close()
                
    return None

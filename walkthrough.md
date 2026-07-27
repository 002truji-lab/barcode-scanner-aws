# Walkthrough: Aplicación Streamlit de Escaneo con AWS RDS y Respuesta Sonora/Visual

La aplicación se encuentra lista y configurada en el directorio:
`C:\Users\03010496\.gemini\antigravity\scratch\streamlit_barcode_aws`

---

## 🌟 Archivos del Proyecto Creados

1. **[app.py](file:///C:/Users/03010496/.gemini/antigravity/scratch/streamlit_barcode_aws/app.py)**
   * **Escáner Continuo en Vivo:** Componente HTML5/JS (`html5-qrcode`) que decodifica códigos en milisegundos usando la cámara trasera del smartphone.
   * **Respuesta Sonora:** Sintetización de tono agudo doble en caso de Éxito y tono grave en caso de Error usando HTML5 Web Audio API.
   * **Respuesta Visual:** Tarjeta dinámica de color **Verde (#10B981)** al encontrar el producto o **Rojo (#EF4444)** si no está registrado.
   * **Soporte Múltiples Códigos:** Lee códigos de barras de distintos formatos (SKU, EAN, LPN, etc.).
   * **Historial Reciente:** Tabla interactiva de escaneos de la sesión.

2. **[db.py](file:///C:/Users/03010496/.gemini/antigravity/scratch/streamlit_barcode_aws/db.py)**
   * Conexión a **PostgreSQL en AWS RDS** mediante `psycopg2`.
   * Búsqueda en múltiples columnas (`codigo_barras` y `codigo_secundario`).
   * Modo de respaldo en memoria local anonimizado para pruebas iniciales.

3. **[upload_data.py](file:///C:/Users/03010496/.gemini/antigravity/scratch/streamlit_barcode_aws/upload_data.py)**
   * Script local ejecutable para crear la tabla e insertar/actualizar registros en la base de datos de AWS RDS.

4. **[.streamlit/secrets.toml.template](file:///C:/Users/03010496/.gemini/antigravity/scratch/streamlit_barcode_aws/.streamlit/secrets.toml.template)**
   * Estructura de credenciales para el panel de *Secrets* de Streamlit Cloud.

5. **[requirements.txt](file:///C:/Users/03010496/.gemini/antigravity/scratch/streamlit_barcode_aws/requirements.txt)**
   * Lista de librerías requeridas (`streamlit`, `psycopg2-binary`, `zxing-cpp`, `pillow`, `pandas`).

6. **[README.md](file:///C:/Users/03010496/.gemini/antigravity/scratch/streamlit_barcode_aws/README.md)**
   * Guía completa de configuración de AWS RDS (Security Group en puerto 5432) y despliegue gratuito en Streamlit Cloud.

---

## 🚀 Pasos para Desplegar en Producción

1. **Subir a GitHub:** Publica el código en un repositorio público o privado de tu cuenta.
2. **Crear tu AWS RDS PostgreSQL (Free Tier):** Asegúrate de habilitar **Publicly Accessible = YES** y abrir el puerto `5432` en el **Security Group**.
3. **Conectar Streamlit Cloud:** Ingresa a [share.streamlit.io](https://share.streamlit.io/), selecciona tu repositorio y configura los *Secrets* con las credenciales de tu RDS.

---

## 🔄 Actualización (Migración de Esquema)

Se ha migrado la base de datos de la tabla genérica a la tabla estructurada `barcode_cazafantasmas`, alimentada por un archivo CSV de inventario real.

### 🛠️ Cambios Realizados
1. **Conexión de Base de Datos (`db.py`)**
   - **Nueva Tabla:** Migración a `barcode_cazafantasmas`.
   - **Nuevas Columnas SQL:** Adaptación de las consultas para extraer `master_box, codigo_barras, codigo_pedido, letra_apellido, desc_master_box, creado_en, modificado_en`.
   - **Datos Locales Simulados:** Se actualizaron los Mock Data en `DEMO_DATABASE` para usar formatos reales (ej. `00384279077087884051` y `F6YMRZ00`) garantizando que la aplicación funciona localmente incluso si falla la conexión a RDS.

2. **Interfaz Gráfica (`app.py`)**
   - **Adaptación Visual:** Las tarjetas de resultado ya no muestran campos irrelevantes (tienda, ruta). Ahora exponen fielmente los campos del CSV: el Master Box, Código de Barras Principal, Código Pedido (LPN) y Letra Apellido.
   - **Título de Producto:** Se ha reemplazado para que muestre de forma predeterminada la descripción (`desc_master_box`).
   
3. **Cargador de Datos (`carga_datos.py`)**
   - Este script fue modificado para leer un CSV (sin cabecera) manejando conversiones seguras con Pandas (manteniendo los ceros a la izquierda mediante `dtype=str`).
   - Ajustada la `PRIMARY KEY` a `codigo_barras` para permitir la repetición lógica de cajas maestras (`master_box`).

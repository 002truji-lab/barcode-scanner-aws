# 📱 Aplicación Streamlit: Escáner de Código de Barras con AWS RDS PostgreSQL

Aplicación web optimizada para smartphones para la lectura ágil de códigos de barras, consulta en AWS RDS PostgreSQL, y respuesta inmediata visual (Verde/Rojo) y sonora (Beep Éxito / Beep Error).

---

## 🚀 Características

* **Visor en Vivo Real-Time:** Lectura continua con la cámara del smartphone mediante HTML5.
* **Captura de Foto Alternativa:** Decodificación de códigos 1D (EAN, Code-128, etc.) y 2D (QR, PDF417) mediante `zxing-cpp`.
* **Respuesta Sonora Instantánea:** Beeps sintetizados con Web Audio API (agudo para éxito, grave para error).
* **Integración con AWS RDS PostgreSQL:** Consulta rápida de productos mediante `psycopg2`.
* **Modo Demo de Respaldo:** Funciona sin configuración previa para pruebas locales.
* **Despliegue Internacional Gratuito:** Listo para ser publicado en Streamlit Cloud.

---

## 🛠️ Estructura del Proyecto

```text
streamlit_barcode_aws/
├── app.py                      # Aplicación principal de Streamlit
├── db.py                       # Conexión y consultas SQL a PostgreSQL AWS RDS
├── upload_data.py              # Script local para poblar la base de datos en AWS RDS
├── requirements.txt            # Dependencias del proyecto
├── README.md                   # Documentación y guía de despliegue
└── .streamlit/
    └── secrets.toml.template   # Plantilla de configuración de secretos de AWS RDS
```

---

## 📦 Configuración Local y Pruebas

1. Instala las dependencias de Python:
   ```bash
   pip install -r requirements.txt
   ```

2. Ejecuta la aplicación localmente:
   ```bash
   streamlit run app.py
   ```

---

## ☁️ Configuración de AWS RDS PostgreSQL (Capa Gratuita)

1. **Crear Instancia RDS:**
   * Entra a la consola de AWS -> **Amazon RDS** -> **Create database**.
   * Elige **PostgreSQL** y selecciona la plantilla **Free tier** (Capa gratuita).
   * Asigna un identificador de BD, usuario (ej. `postgres`) y contraseña.
   * En la sección **Connectivity**:
     * Marca **Publicly Accessible: YES** (Accesible públicamente).

2. **Configurar el Security Group (Grupo de Seguridad):**
   * Ve a la sección **EC2 Security Group** asociado a tu base de datos RDS.
   * En **Inbound rules** (Reglas de entrada), añade una regla:
     * **Type:** PostgreSQL (Port 5432)
     * **Source:** `0.0.0.0/0` (o el rango de IPs requeridas).

3. **Cargar Datos Iniciales a RDS:**
   * Abre `upload_data.py`, coloca las credenciales de tu instancia RDS y ejecuta:
     ```bash
     python upload_data.py
     ```

---

## 🌐 Despliegue Gratuito en Streamlit Cloud

1. Sube este repositorio a **GitHub**.
2. Entra a [share.streamlit.io](https://share.streamlit.io/) e inicia sesión con tu cuenta de GitHub.
3. Haz clic en **New app**, selecciona el repositorio y establece `app.py` como el archivo principal.
4. En **Advanced Settings -> Secrets**, pega la configuración de tu PostgreSQL:
   ```toml
   [postgres]
   host = "tu-instancia-rds.xxxxxx.us-east-1.rds.amazonaws.com"
   port = 5432
   database = "postgres"
   user = "postgres"
   password = "TuPasswordSeguro123"
   ```
5. Haz clic en **Deploy**. ¡Tu aplicación estará publicada en una URL HTTPS pública accesible desde cualquier smartphone del mundo!

# 🚀 Guía paso a paso para subir tu aplicación a Streamlit Cloud

Subir tu aplicación a la nube con **Streamlit Community Cloud** es el método más rápido, fácil y **totalmente gratuito**. Sigue estos pasos cuidadosamente:

## Paso 1: Sube tu proyecto a GitHub
Streamlit Cloud lee el código directamente desde tu repositorio de GitHub.

1. Entra a [GitHub](https://github.com/) e inicia sesión (o créate una cuenta si no tienes).
2. Haz clic en el botón verde **"New"** (Nuevo repositorio).
3. Ponle un nombre a tu repositorio (ej. `barcode-scanner-aws`).
4. Déjalo como **Public** o **Private** (ambos funcionan) y haz clic en **"Create repository"**.
5. Abre la consola/terminal en tu ordenador, dentro de tu carpeta `c:\Proyectos\Proyecto barcode AWS\` y ejecuta estos comandos para subir tus archivos:
   ```bash
   git init
   git add .
   git commit -m "Mi primera versión de la app"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
   git push -u origin main
   ```
   *(Asegúrate de cambiar `TU_USUARIO` y `TU_REPOSITORIO` por los tuyos).*

## Paso 2: Crear la App en Streamlit Cloud

1. Entra a [Streamlit Community Cloud](https://share.streamlit.io/) e inicia sesión vinculando tu cuenta de GitHub.
2. Haz clic en el botón azul **"New app"** arriba a la derecha.
3. Te pedirá que selecciones un repositorio. Selecciona el que acabas de crear (`barcode-scanner-aws`).
4. En **Branch**, déjalo en `main`.
5. En **Main file path**, asegúrate de escribir **`app2.py`** (ya que ese es el archivo con el que has estado trabajando).
6. **IMPORTANTE: ¡No le des a Deploy todavía!**

## Paso 3: Configurar los Secretos de la Base de Datos (AWS RDS)
Tu aplicación necesita la contraseña de tu base de datos AWS RDS para poder buscar los códigos. Nunca debes subir las contraseñas a GitHub por seguridad, por eso usamos los *Secrets* de Streamlit.

1. En la misma ventana donde estás creando la app, abajo a la derecha hay un botón que dice **"Advanced settings..."**. Haz clic en él.
2. Verás un cuadro de texto grande llamado **"Secrets"**.
3. Pega la configuración de tu conexión a PostgreSQL allí dentro. Asegúrate de rellenarlo con los datos reales de tu base de datos AWS RDS:

```toml
[postgres]
host = "EL_PUNTO_DE_ENLACE_DE_TU_AWS_RDS.rds.amazonaws.com"
port = 5432
database = "TU_BASE_DE_DATOS"
user = "TU_USUARIO"
password = "TU_CONTRASEÑA"
```

4. Haz clic en **Save** en la ventana de configuración avanzada.

## Paso 4: ¡Desplegar!

1. Ahora sí, haz clic en el botón rojo **"Deploy"**.
2. Streamlit empezará a "cocinar" tu aplicación. Verás una pantalla cargando con globos (puede tardar un par de minutos porque está instalando todo lo que pusiste en el archivo `requirements.txt`).
3. Cuando termine... **¡Felicidades! 🎉** 

Tu aplicación ya estará subida a la nube. Streamlit te dará un enlace único (algo como `https://tu-app.streamlit.app`) que puedes abrir desde el navegador de tu móvil o compartir con quien quieras en cualquier lugar del mundo.

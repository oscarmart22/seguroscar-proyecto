# Seguroscar - Plataforma Global de Seguros

Seguroscar es una aplicación web moderna diseñada para la gestión y comunicación en el sector de seguros, integrando un foro interactivo, un mapa global de nodos y un sistema robusto de autenticación.

## 🚀 Descripción de Funcionalidades

1.  **Sistema de Autenticación Completo:**
    *   Registro de usuarios con hashing de contraseñas.
    *   Inicio de sesión persistente mediante `Flask-Login`.
    *   Gestión de sesiones y perfiles de usuario.
2.  **Foro Interactivo (Comunidad):**
    *   Creación de hilos de discusión principales.
    *   Sistema de respuestas anidadas para debates fluidos.
    *   Edición y eliminación de publicaciones (restringido a autores y administradores).
3.  **Red Global (Mapa):**
    *   Visualización interactiva de nodos internacionales.
    *   Interfaz dinámica basada en datos geoespaciales.
4.  **Panel de Administración:**
    *   Capacidades de moderación para usuarios con rol de administrador.
5.  **Arquitectura Serverless:**
    *   Despliegue optimizado para Vercel mediante funciones serverless en Python.

## 🛠️ Tecnologías Utilizadas

*   **Backend:** Python 3.x con el framework **Flask**.
*   **Base de Datos:** PostgreSQL (alojado en **Supabase**) con **SQLAlchemy** como ORM.
*   **Frontend:** HTML5 semántico, CSS3 moderno (Vanilla CSS con diseño premium) y JavaScript nativo.
*   **Despliegue:** Vercel (Serverless Architecture).
*   **Gestión de Dependencias:** pip (`requirements.txt`).
*   **Seguridad:** Werkzeug para hashing de contraseñas y variables de entorno para datos sensibles.

## 📡 Endpoints Principales de la API

| Método | Ruta | Descripción |
| :--- | :--- | :--- |
| `POST` | `/register` | Registra un nuevo usuario en el sistema. |
| `POST` | `/login` | Autentica a un usuario y crea una sesión. |
| `POST` | `/logout` | Cierra la sesión activa del usuario. |
| `GET` | `/api/me` | Retorna los datos del usuario actualmente autenticado. |
| `GET` | `/api/posts` | Obtiene todos los hilos principales del foro. |
| `POST` | `/api/posts` | Crea una nueva publicación o respuesta. |
| `PUT` | `/api/posts/edit/<id>` | Edita el contenido de una publicación existente. |
| `DELETE` | `/api/posts/delete/<id>` | Elimina una publicación y sus respuestas. |

## 💻 Instrucciones de Instalación y Ejecución

### Requisitos Previos
*   Python 3.9 o superior instalado.
*   Cuenta en Supabase (para la base de datos PostgreSQL).

### Pasos para Ejecución Local

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/oscarmart22/seguroscar-proyecto.git
    cd seguroscar-proyecto
    ```

2.  **Crear y activar un entorno virtual:**
    ```bash
    python -m venv venv
    # En Windows:
    .\venv\Scripts\activate
    # En Unix/macOS:
    source venv/bin/activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar variables de entorno:**
    Crea un archivo `.env` en la raíz con el siguiente formato:
    ```env
    DATABASE_URL=tu_url_de_postgresql
    SECRET_KEY=tu_clave_secreta
    ```

5.  **Ejecutar la aplicación:**
    ```bash
    python server.py
    ```
    La aplicación estará disponible en `http://localhost:8080`.

### Despliegue en Vercel
Para desplegar en Vercel, simplemente vincula el repositorio en el panel de control de Vercel. El archivo `vercel.json` ya está configurado para manejar la ejecución serverless automáticamente.

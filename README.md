# Sistema de Quejas y Reclamos de Alumnos

Aplicación web construida con **Streamlit** y **SQLite** para capturar y gestionar quejas, reclamos, sugerencias y observaciones de alumnos.

## Requisitos

- Python 3.9+
- Instalar dependencias:

```bash
pip install streamlit pandas
```

## Cómo ejecutar

Desde la carpeta `SistemaQuejas`:

```bash
streamlit run app.py
```

Se abrirá el navegador en `http://localhost:8501`.

## Funcionalidades

- **Registrar queja/reclamo**: formulario con datos del alumno, tipo, área, prioridad y descripción.
- **Mis Registros**: vista detallada con cambio de estado, vista en tabla, estadísticas y descarga en CSV.
- **Folio automático**: cada registro recibe un folio único (Q-AÑO-####).
- **Base de datos SQLite**: los datos se guardan en `quejas.db`.

## Estructura

```
SistemaQuejas/
├── app.py        # Aplicación principal
├── database.py   # Capa de acceso a datos (SQLite)
└── quejas.db     # Base de datos (se crea automáticamente)
```

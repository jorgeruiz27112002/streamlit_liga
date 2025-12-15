# ⚽ Dashboard Profesional La Liga 23/24

Este proyecto es una herramienta interactiva de análisis de datos para jugadores de La Liga temporada 2023/2024. Construido con **Streamlit** y **Python**, permite explorar métricas financieras, tácticas y demográficas de los equipos y jugadores.

## 🚀 Características Principales

La aplicación se divide en 4 módulos principales:

### 1. 💰 Economía
Análisis financiero detallado de la liga:
- **Distribución Salarial**: Gráficos de cajas y bigotes para comparar rangos salariales por equipo.
- **Análisis ROI**: Relación entre salario y rendimiento (goles, asistencias, recuperación, etc.).
- **Gasto por Equipo**: Visualización del presupuesto salarial (Barras o Treemap).
- **Correlaciones**: Mapa de calor para ver cómo influyen métricas clave en el salario.
- **Densidad Salarial**: Comparativa de curvas de densidad (KDE) entre equipos.

### 2. 🧪 Comparador de Jugadores
Herramienta de scouting para comparar dos jugadores cara a cara:
- Gráfico de **Radar** interactivo.
- Selección de perfiles: Atacante, Defensivo o Creador.
- Normalización automática de métricas para una comparación justa.

### 3. 🧠 Análisis Táctico
Exploración profunda de estilos de juego:
- **Comparativa de Equipos**: Scatter plots personalizables (Ejes X/Y a elección).
- **Análisis de Jugadores**: Dispersión de métricas individuales filtradas por posición.
- **Porteros**: Sección específica para métricas de guardametas (paradas, goles encajados, etc.).

### 4. 🧬 Demografía
Visión general de la composición de la liga:
- **Edad**: Histograma de distribución de edad por posición.
- **Nacionalidades**: Gráfico de diversidad internacional (excluyendo locales para destacar el talento extranjero).

## 🛠️ Requisitos e Instalación

### Prerrequisitos
Asegúrate de tener Python instalado (recomendado 3.9+). Las principales librerías utilizadas son:
- `streamlit`
- `pandas`
- `plotly`
- `seaborn`
- `matplotlib`
- `scikit-learn`
- `openpyxl` (para procesar el Excel original)

### Instalación
1. Clona el repositorio o descarga los archivos.
2. Instala las dependencias:
   ```bash
   pip install streamlit pandas plotly seaborn matplotlib scikit-learn openpyxl
   ```

## ▶️ Uso

1. **Datos**: El proyecto incluye un script de limpieza (`clean_data.ipynb`) que procesa el archivo original `SS2324_laliga_players.xlsx` y genera `SS2324_laliga_players_cleaned.csv`, el cual es consumido por la app.
   
2. **Ejecutar la App**:
   Navega a la carpeta del proyecto en tu terminal y ejecuta:
   ```bash
   streamlit run app2.py
   ```

3. **Navegación**:
   - Usa la **Barra Lateral** para filtrar globalmente por **Equipos** y **Posiciones**.
   - Navega entre las pestañas superiores para cambiar de módulo de análisis.

## 📂 Estructura del Proyecto

- `app2.py`: Código fuente principal de la aplicación Streamlit.
- `clean_data.ipynb`: Notebook de Jupyter para la limpieza y preparación inicial de datos.
- `SS2324_laliga_players_cleaned.csv`: Dataset procesado (listo para la app).
- `LaLiga.png`: Logo utilizado en la interfaz.

---
*Desarrollado para la asignatura de Almacenamiento - Loyola IA.*

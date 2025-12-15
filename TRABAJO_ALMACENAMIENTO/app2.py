import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Dashboard Profesional La Liga",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS
st.markdown("""
<style>
    .main { background-color: #f5f5f5; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #FFFFFF;
        border-radius: 4px 4px 0px 0px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF;
        border-bottom: 2px solid #ff4b4b;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. CARGA Y PREPARACIÓN DE DATOS ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('SS2324_laliga_players_cleaned.csv')
    except FileNotFoundError:
        # Fallback: Logic from clean_data.ipynb
        df = pd.read_excel('SS2324_laliga_players.xlsx')
        df['Salario'] = pd.to_numeric(df['Salario'], errors='coerce')
        df = df.dropna(subset=['Salario'])
        df = df.fillna(0)
    
    # A. Cálculo de Edad
    df['date_of_birth'] = pd.to_datetime(df['date_of_birth'], errors='coerce')
    now = datetime.now()
    df['age'] = (now - df['date_of_birth']).dt.days / 365.25
    df['age'] = df['age'].fillna(0).astype(int)
    
    # B. Limpieza de Salario
    df['Salario'] = pd.to_numeric(df['Salario'], errors='coerce')
    
    # C. Minutos reales
    df['minutos_reales'] = df['time_played'].apply(lambda x: x if x > 0 else 1)
    
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error crítico al cargar datos: {e}")
    st.stop()

# --- 3. BARRA LATERAL ---
st.sidebar.image("LaLiga.png", width=150)
st.sidebar.header("Filtros Globales")

equipos = sorted(df['team'].dropna().unique())
sel_equipos = st.sidebar.multiselect("Equipos", equipos, default=equipos)

posiciones = sorted(df['position'].dropna().unique())
sel_posiciones = st.sidebar.multiselect("Posiciones", posiciones, default=posiciones)

df_filtered = df[
    (df['team'].isin(sel_equipos)) & 
    (df['position'].isin(sel_posiciones))
]

st.sidebar.markdown("---")
st.sidebar.metric("Jugadores", len(df_filtered))
st.sidebar.metric("Salario Medio", f"€{df_filtered['Salario'].mean():,.0f}")

# Lista de métricas para los selectores tácticos
metricas_tacticas = [
    'goals', 'assists_intentional', 'total_passes', 'successful_long_passes', 
    'tackles_won', 'interceptions', 'total_clearances', 'recoveries', 
    'aerial_duels_won', 'successful_dribbles', 'shots_on_target_inc_goals', 
    'time_played', 'Salario'
]

# --- 4. CUERPO PRINCIPAL ---
st.title("📊 La Liga 23/24: Scouting & Finanzas")

tab1, tab2, tab3, tab4 = st.tabs([
    "💰 Economía", 
    "🧪 Comparador de jugadores", 
    "🧠 Análisis Táctico",
    "🧬 Demografía"
])

# ==============================================================================
# PESTAÑA 1: Economía
# ==============================================================================
with tab1:
    st.header("Análisis Financiero Avanzado")
    
    # 1. Boxplot
    st.subheader("1. Distribución y Dispersión Salarial por Equipo")
    orden_equipos = df_filtered.groupby('team')['Salario'].median().sort_values(ascending=False).index
    fig_box = px.box(
        df_filtered,
        x='team',
        y='Salario',
        color='team',
        category_orders={'team': orden_equipos},
        title="Rango Salarial (Cajas y Bigotes)",
        labels={'Salario': 'Salario Anual (€)', 'team': ''}
    )
    fig_box.update_layout(showlegend=False, xaxis_tickangle=-45, height=500)
    st.plotly_chart(fig_box, use_container_width=True)
    
    st.markdown("---")

    # 2. Scatter Plot
    st.subheader("2. ROI: Relación Coste vs. Rendimiento Total")
    metrica_roi = st.selectbox(
        "Métrica de Rendimiento (Eje X):",
        ['goals', 'assists_intentional', 'recoveries', 'interceptions', 'total_passes', 'tackles_won'],
        index=0
    )
    fig_scatter = px.scatter(
        df_filtered,
        x=metrica_roi,
        y="Salario",
        size="time_played",
        color="position",
        hover_name="name",
        hover_data=["team", "age"],
        title=f"Salario vs {metrica_roi.capitalize()} (Tamaño = Minutos Jugados)",
        labels={"Salario": "Salario (€)", metrica_roi: metrica_roi.capitalize()}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")

    # 3. Reparto del Gasto Salarial por Equipo (MEJORADO)
    st.subheader("3. Reparto del Gasto Salarial por Equipo")

    df_team_salary = (
        df_filtered
        .dropna(subset=["Salario"])
        .groupby("team", as_index=False)["Salario"]
        .sum()
    )

    if df_team_salary.empty or df_team_salary["Salario"].sum() <= 0:
        st.warning("No hay datos de salario para mostrar con los filtros actuales.")
    else:
        total_salary = df_team_salary["Salario"].sum()
        df_team_salary["pct"] = 100 * df_team_salary["Salario"] / total_salary

        vista = st.radio(
            "Tipo de gráfico",
            ["Barras (Top + Otros)", "Treemap"],
            horizontal=True,
            key="salary_share_view"
        )

        if vista == "Barras (Top + Otros)":
            max_top = min(20, df_team_salary.shape[0])
            top_n = st.slider(
                "Top N equipos",
                min_value=5 if max_top >= 5 else 1,
                max_value=max_top,
                value=min(10, max_top),
                key="salary_top_n"
            )
            agrupar_otros = st.checkbox(
                "Agrupar el resto como 'Otros'",
                value=True,
                key="salary_group_others"
            )

            d = df_team_salary.sort_values("Salario", ascending=False).reset_index(drop=True)

            if agrupar_otros and d.shape[0] > top_n:
                top = d.iloc[:top_n].copy()
                resto = d.iloc[top_n:]["Salario"].sum()
                d_plot = pd.concat(
                    [top, pd.DataFrame([{"team": "Otros", "Salario": resto}])],
                    ignore_index=True
                )
            else:
                d_plot = d.iloc[:top_n].copy()

            d_plot["pct"] = 100 * d_plot["Salario"] / d_plot["Salario"].sum()
            d_plot = d_plot.sort_values("pct", ascending=True)

            fig = px.bar(
                d_plot,
                y="team",
                x="pct",
                orientation="h",
                text=d_plot["pct"].map(lambda v: f"{v:.1f}%"),
                hover_data={"Salario": ":,.0f", "pct": ":.2f"},
                title="Proporción de gasto salarial por equipo",
                labels={"team": "", "pct": "% del total"}
            )
            fig.update_traces(textposition="outside", cliponaxis=False)
            fig.update_layout(height=650, xaxis_range=[0, max(d_plot["pct"]) * 1.15])

            st.plotly_chart(fig, use_container_width=True)

        else:
            # Treemap robusto (con raíz + sin color continuo + sin tema Streamlit)
            d = df_team_salary.copy()
            d["team"] = d["team"].astype(str).str.strip()
            d = d[d["Salario"] > 0]

            fig_treemap = px.treemap(
                d,
                path=[px.Constant("LaLiga"), "team"],  # raíz + nivel equipo
                values="Salario",
                title="Distribución de gasto salarial por equipo (Treemap)"
            )

            fig_treemap.update_traces(
                textinfo="label+percent entry",
                textfont=dict(size=12, color="black"),
                marker=dict(line=dict(width=2, color="white")),
                root_color="lightgrey"
            )

            fig_treemap.update_layout(
                height=650,
                margin=dict(t=60, l=0, r=0, b=0)
            )

            st.plotly_chart(fig_treemap, use_container_width=True, theme=None)


    # 4. Matriz de Correlación
    st.subheader("4. Matriz de Correlación: Salario vs Métricas")
    cols_corr = ['Salario', 'age', 'goals', 'assists_intentional', 'total_passes', 'time_played', 'tackles_won', 'aerial_duels_won']
    cols_corr = [c for c in cols_corr if c in df_filtered.columns]
    
    corr_matrix = df_filtered[cols_corr].corr()
    
    fig_heat = px.imshow(
        corr_matrix,
        text_auto='.2f',
        aspect="auto",
        color_continuous_scale='RdBu_r',
        title="Mapa de Calor de Correlaciones (Pearson)"
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("---")

    # 5. Funciones de Densidad
    st.subheader("5. Comparativa de Curvas de Densidad Salarial")
    teams_kde = st.multiselect(
        "Selecciona equipos para comparar sus curvas:",
        options=equipos,
        default=[equipos[0], equipos[1]] if len(equipos) > 1 else equipos,
        key="kde_multiselect"
    )
    
    if teams_kde:
        hist_data = []
        group_labels = []
        for team in teams_kde:
            salaries = df_filtered[df_filtered['team'] == team]['Salario'].dropna()
            if len(salaries) > 1:
                hist_data.append(salaries)
                group_labels.append(team)
        
        if hist_data:
            custom_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
            fig_kde = ff.create_distplot(
                hist_data, 
                group_labels, 
                show_hist=False, 
                show_rug=False,
                colors=custom_colors[:len(hist_data)],
                curve_type='kde'
            )
            fig_kde.update_layout(title="Curvas de Densidad de Salarios (KDE)", xaxis_title="Salario Anual (€)", yaxis_title="Densidad")
            for trace in fig_kde.data:
                if 'x' in trace: trace.line.width = 3
            st.plotly_chart(fig_kde, use_container_width=True)
        else:
            st.warning("Datos insuficientes para generar curvas.")
    else:
        st.warning("Selecciona al menos un equipo.")

# ==============================================================================
# PESTAÑA 2: Comparación jugadores
# ==============================================================================
with tab2:
    st.header("Comparador de Jugadores (Radar)")
    c_sel1, c_sel2, c_sel3 = st.columns(3)
    lista_jugadores = sorted(df['name'].unique())
    p1_name = c_sel1.selectbox("Jugador 1 (Azul)", lista_jugadores, index=0)
    p2_name = c_sel2.selectbox("Jugador 2 (Rojo)", lista_jugadores, index=1)
    perfil = c_sel3.selectbox("Perfil", ["Atacante", "Defensivo", "Creador"])
    
    if perfil == "Atacante":
        cols = ['goals', 'shots_on_target_inc_goals', 'successful_dribbles', 'aerial_duels_won', 'key_passes_attempt_assists']
        names = ['Goles', 'Tiros Puerta', 'Regates', 'Aéreos', 'Pases Clave']
    elif perfil == "Defensivo":
        cols = ['tackles_won', 'interceptions', 'total_clearances', 'recoveries', 'aerial_duels_won']
        names = ['Entradas', 'Intercep.', 'Despejes', 'Recuperac.', 'Aéreos']
    else:
        cols = ['total_passes', 'successful_long_passes', 'assists_intentional', 'key_passes_attempt_assists', 'successful_dribbles']
        names = ['Pases', 'Pases Largos', 'Asistencias', 'Pases Clave', 'Regates']
        
    try:
        df_radar_base = df[cols].fillna(0)
        scaler = MinMaxScaler()
        df_scaled = pd.DataFrame(scaler.fit_transform(df_radar_base), columns=cols, index=df.index)
        
        idx_p1 = df[df['name'] == p1_name].index[0]
        idx_p2 = df[df['name'] == p2_name].index[0]
        val_p1 = df_scaled.loc[idx_p1].values
        val_p2 = df_scaled.loc[idx_p2].values
        
        fig_radar = go.Figure()
        
        # JUGADOR 1: AZUL
        fig_radar.add_trace(go.Scatterpolar(
            r=val_p1, 
            theta=names, 
            fill='toself', 
            name=p1_name,
            line_color='#1f77b4', # Azul
            fillcolor='rgba(31, 119, 180, 0.5)'
        ))
        
        # JUGADOR 2: ROJO
        fig_radar.add_trace(go.Scatterpolar(
            r=val_p2, 
            theta=names, 
            fill='toself', 
            name=p2_name,
            line_color='#d62728', # Rojo
            fillcolor='rgba(214, 39, 40, 0.5)'
        ))
        
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), showlegend=True, title=f"Comparativa: {p1_name} vs {p2_name}")
        st.plotly_chart(fig_radar, use_container_width=True)
    except Exception as e:
        st.error(f"Error al generar radar: {e}")

# ==============================================================================
# PESTAÑA 3: TÁCTICA
# ==============================================================================
with tab3:
    st.header("Análisis Táctico Avanzado")

    st.subheader("1. Comparativa Táctica de Equipos")
    col_t1, col_t2 = st.columns(2)
    with col_t1: x_team = st.selectbox("Eje X (Equipos):", metricas_tacticas, index=2, key="team_x")
    with col_t2: y_team = st.selectbox("Eje Y (Equipos):", metricas_tacticas, index=3, key="team_y")
    
    estilo_equipo = df.groupby('team')[metricas_tacticas].mean().reset_index()
    fig_style = px.scatter(estilo_equipo, x=x_team, y=y_team, text="team", title=f"Equipos: {x_team.capitalize()} vs {y_team.capitalize()}")
    fig_style.update_traces(textposition='top center', marker=dict(size=12, color='#ef553b'))
    st.plotly_chart(fig_style, use_container_width=True)
    
    st.markdown("---")

    st.subheader("2. Comparativa Táctica de Jugadores")
    col_p1, col_p2 = st.columns(2)
    with col_p1: x_player = st.selectbox("Eje X (Jugadores):", metricas_tacticas, index=4, key="play_x")
    with col_p2: y_player = st.selectbox("Eje Y (Jugadores):", metricas_tacticas, index=5, key="play_y")
        
    fig_players = px.scatter(df_filtered, x=x_player, y=y_player, color="position", hover_name="name", hover_data=["team"], title=f"Jugadores: {x_player.capitalize()} vs {y_player.capitalize()}")
    st.plotly_chart(fig_players, use_container_width=True)
    
    st.markdown("---")

    st.subheader("3. Rendimiento de Porteros")
    gk_df = df[df['position'] == 'Goalkeeper']
    if not gk_df.empty:
        col_gk1, col_gk2 = st.columns(2)
        with col_gk1: x_gk = st.selectbox("Eje X (Porteros):", ['saves_made', 'goals_conceded', 'clean_sheets', 'penalties_saved'], index=0)
        with col_gk2: y_gk = st.selectbox("Eje Y (Porteros):", ['saves_made', 'goals_conceded', 'clean_sheets', 'penalties_saved'], index=1)

        fig_gk = px.scatter(gk_df, x=x_gk, y=y_gk, color="team", hover_name="name", title=f"Porteros: {x_gk.capitalize()} vs {y_gk.capitalize()}")
        fig_gk.update_traces(marker=dict(size=10, line=dict(width=1, color='DarkSlateGrey')))
        st.plotly_chart(fig_gk, use_container_width=True)
    else:
        st.info("No hay datos de porteros disponibles.")

# ==============================================================================
# PESTAÑA 4: DEMOGRAFÍA
# ==============================================================================
with tab4:
    st.header("Demografía y Origen")
    
    # 1. Histograma de Edad
    st.subheader("1. Distribución de Edad de la Plantilla")
    fig_hist = px.histogram(
        df_filtered,
        x="age",
        color="position",
        nbins=20,
        title="Histograma de Edad por Posición",
        barmode="overlay",
        opacity=0.7,
        labels={'age': 'Edad', 'count': 'Número de Jugadores'}
    )
    st.plotly_chart(fig_hist, use_container_width=True)
    
    st.markdown("---")
    
    # 2. Nacionalidades (Bar Chart Horizontal - Sin España)
    st.subheader("2. Diversidad Internacional (Excluyendo España)")
    
    # A. Contar y preparar datos
    df_nacionalidad = df_filtered['country'].value_counts().reset_index()
    df_nacionalidad.columns = ['País', 'Cantidad']
    
    # B. KPI: Jugadores Españoles
    esp_data = df_nacionalidad[df_nacionalidad['País'] == 'ES']
    num_esp = esp_data['Cantidad'].values[0] if not esp_data.empty else 0
    st.metric("🇪🇸 Total Jugadores Españoles (Excluidos del gráfico)", num_esp)
    
    # C. Filtrar España y Ordenar
    # Ordenamos descendente para tomar el Top N, luego ascendente para que Plotly pinte el mayor arriba
    df_plot_nac = df_nacionalidad[df_nacionalidad['País'] != 'ES'].sort_values('Cantidad', ascending=False)
    
    # Filtro Top 20 para legibilidad
    top_n = 20
    if len(df_plot_nac) > top_n:
        df_plot_nac = df_plot_nac.head(top_n)
        titulo_nac = f"Top {top_n} Nacionalidades Extranjeras (Menor a Mayor)"
    else:
        titulo_nac = "Distribución de Jugadores Extranjeros"
    
    # Invertimos el orden para que en el gráfico horizontal el mayor salga arriba (Plotly dibuja de abajo a arriba)
    df_plot_nac = df_plot_nac.sort_values('Cantidad', ascending=True)

    fig_nac = px.bar(
        df_plot_nac,
        x='Cantidad',
        y='País',
        orientation='h', # Horizontal
        title=titulo_nac,
        text='Cantidad',
        color='País', # Colores distintos por país
        color_discrete_sequence=px.colors.qualitative.Bold # Paleta de colores vivos
    )
    fig_nac.update_layout(xaxis_title="Número de Jugadores", yaxis_title="País")
    st.plotly_chart(fig_nac, use_container_width=True)

st.markdown("---")
with st.expander("📂 Ver Datos Brutos"):
    st.dataframe(df_filtered)
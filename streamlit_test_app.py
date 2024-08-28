#######################
# Import libraries
import streamlit as st
import pandas as pd
import geopandas as gpd
import altair as alt
import plotly.express as px
import shapely
from shapely import wkt

#######################
# Page configuration
st.set_page_config(
    page_title="Delitos en Montevideo",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")


#######################
# Load data

df_reshaped = pd.read_csv('data/us-population-2010-2019-reshaped.csv')

# Cargar el archivo CSV usando pandas
df_uy = pd.read_csv('data/geo_filtrado.csv')


# Convertir la columna 'geo' de WKT a objetos geométricos
df_uy['geo'] = df_uy['geo'].apply(wkt.loads)

# Luego, crear el GeoDataFrame
df_uy2 = gpd.GeoDataFrame(df_uy, geometry='geo')
df_uy2.set_crs(epsg=4326, inplace=True)

# Data frame para el mapa de calor
df_mapa = pd.read_csv('data/tabla_calor.csv')

#######################
# Sidebar
with st.sidebar:
    st.title('Delitos en Montevideo')
    
    year_list = list(df_reshaped.year.unique())[::-1]
    
    selected_year = st.selectbox('Select a year', year_list)
    df_selected_year = df_reshaped[df_reshaped.year == selected_year]
    df_selected_year_sorted = df_selected_year.sort_values(by="population", ascending=False)

    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)


#######################

# Manipulación de datos

# Asegurar el orden correcto de los días de la semana
orden_dias_semana = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO']



#######################
# Plots

# Heatmap
def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
            y=alt.Y(f'{input_y}:O', sort=orden_dias_semana, axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
            x=alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
            color=alt.Color(f'sum({input_color}):Q',
                             legend=None,
                             scale=alt.Scale(scheme=input_color_theme)),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
        ).properties(width=900
        ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
        )
    return heatmap

# Choropleth map
def make_choropleth(input_df, input_color_theme):
    # Convertir a GeoJSON si es necesario
    geojson_data = input_df.__geo_interface__ if hasattr(input_df, '__geo_interface__') else None
    
    if geojson_data:
        choropleth = px.choropleth_mapbox(
            input_df, 
            geojson=geojson_data,
            locations='BARRIO_MONTEVIDEO',  
            featureidkey="properties.BARRIO_MONTEVIDEO", 
            color='ratio',  
            mapbox_style="carto-darkmatter",
            color_continuous_scale=input_color_theme,
            zoom=10,
            center={"lat": -34.9011, "lon": -56.1645}, 
            opacity=0.8,
            labels={'ratio': 'Delitos por mil habitantes'} 
        )
    else:
        st.error("Error: No se pudo generar el geojson a partir del DataFrame.")

    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return choropleth

# Barras
def make_bars(input_df, input_color_theme):
    bars = px.bar(
        input_df,
        x='BARRIO_MONTEVIDEO',  # Eje X: nombres de los barrios
        y='ratio',  # Eje Y: número total de delitos
        color='ratio',  # Colorear las barras según el número de delitos
        color_continuous_scale=input_color_theme,  # Escala de colores (rojo para representar peligro)
        labels={'ratio': 'Delitos por mil habitantes', 'BARRIO_MONTEVIDEO': 'Barrio'}  # Etiquetas de los ejes
)

# Personalizar el diseño
    bars.update_layout(
        xaxis_title='Barrio',
        yaxis_title='Delitos por mil habitantes',
        xaxis={'categoryorder':'total descending'},  # Asegurar que las barras se ordenen correctamente
        template='plotly_dark'  # Usar un tema oscuro para mayor impacto visual (opcional)
) 
    return bars

### $


### $


#######################
# Dashboard Main Panel
col = st.columns((0.5, 7, 0.5), gap='medium')




### $

    
### $

with col[1]:


    st.title("Título Principal de la App")
    st.subheader("Subtítulo de la Sección")

    st.write("")  # Espacio en blanco
    ######
    st.markdown('#### Delitos según barrios de Montevideo')
    st.text("Este es un comentario o texto adicional.")
    choropleth = make_choropleth(df_uy2, selected_color_theme)
    st.plotly_chart(choropleth, use_container_width=True)


    st.write("")  # Espacio en blanco
    st.write("---")  # Línea divisoria
    st.write("")  # Espacio en blanco
    ######
    
    st.markdown('#### Delitos según día y hora')
    st.text("Este es un comentario o texto adicional.")
    heatmap = make_heatmap(df_mapa, 'DIA_SEMANA', 'HORA', 'total_delitos', selected_color_theme)
    st.altair_chart(heatmap, use_container_width=True)

    st.write("")  # Espacio en blanco
    st.write("---")  # Línea divisoria
    st.write("")  # Espacio en blanco
    ######
    
    st.markdown('#### Barrios más peligrosos')
    st.text("Este es un comentario o texto adicional.")
    bars = make_bars(df_uy2, selected_color_theme)
    st.plotly_chart(bars, use_container_width=True)
    
    



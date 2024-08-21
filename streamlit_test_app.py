#######################
# Import libraries
import streamlit as st
import pandas as pd
import geopandas as gpd
import altair as alt
import plotly.express as px

#######################
# Page configuration
st.set_page_config(
    page_title="US Population Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")


#######################
# Load data
df_reshaped = pd.read_csv('data/us-population-2010-2019-reshaped.csv')
df_uy = pd.read_csv('data/geo_filtrado.csv')

# Convertir el DataFrame en un GeoDataFrame
df_uy2 = gpd.GeoDataFrame(df_uy, geometry='geo')

# Establecer el sistema de referencia de coordenadas (CRS) como WGS 84 (EPSG:4326)
df_uy2.set_crs(epsg=4326, inplace=True)


#######################
# Sidebar
with st.sidebar:
    st.title('🏂 US Population Dashboard')
    
    year_list = list(df_reshaped.year.unique())[::-1]
    
    selected_year = st.selectbox('Select a year', year_list)
    df_selected_year = df_reshaped[df_reshaped.year == selected_year]
    df_selected_year_sorted = df_selected_year.sort_values(by="population", ascending=False)

    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)


#######################
# Plots

# Heatmap
def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
            y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
            x=alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
            color=alt.Color(f'max({input_color}):Q',
                             legend=None,
                             scale=alt.Scale(scheme=input_color_theme)),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
        ).properties(width=900
        ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
        ) 
    # height=300
    return heatmap

# Choropleth map
def make_choropleth(input_df):
    # Convertir a GeoJSON si es necesario
    geojson_data = input_df.__geo_interface__ if hasattr(input_df, '__geo_interface__') else None
    
    if geojson_data:
        choropleth = px.choropleth_mapbox(
            input_df, 
            geojson=geojson_data,
            locations='BARRIO_MONTEVIDEO',  
            featureidkey="properties.BARRIO_MONTEVIDEO", 
            color='ratio',  
            mapbox_style="carto-positron",
            color_continuous_scale="Reds",
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



### $


### $


#######################
# Dashboard Main Panel
col = st.columns((1, 6, 1), gap='medium')




### $

    
### $

with col[1]:
    st.markdown('#### Delitos según barrios de Montevideo')
    
    choropleth = make_choropleth(df_uy2)
    st.plotly_chart(choropleth, use_container_width=True)
    
    heatmap = make_heatmap(df_reshaped, 'year', 'states', 'population', selected_color_theme)
    st.altair_chart(heatmap, use_container_width=True)
    



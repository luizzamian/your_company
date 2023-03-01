# Libaries
import pandas as pd
from haversine import haversine
import re
import plotly.express as px
import folium
import streamlit as st
from streamlit_folium import folium_static
from PIL import Image
# ____________________________________________________________________________________________________
# FUNÇÕES
# ____________________________________________________________________________________________________

def clean_code(df):
        
    """Esta função tem o objetivo de realizar a limpeza do Dataframe"""

    # Remover espaco da string
    df.loc[:,'ID'] = df.loc[:,'ID'].str.strip()
    df.loc[:,'Delivery_person_Age'] = df.loc[:,'Delivery_person_Age'].str.strip()
    df.loc[:,'Delivery_person_Ratings'] = df.loc[:,'Delivery_person_Ratings'].str.strip()
    df.loc[:,'Time_Orderd'] = df.loc[:,'Time_Orderd'].str.strip()
    df.loc[:,'Road_traffic_density'] = df.loc[:,'Road_traffic_density'].str.strip()
    df.loc[:,'Type_of_order'] = df.loc[:,'Type_of_order'].str.strip()
    df.loc[:,'Type_of_vehicle'] = df.loc[:,'Type_of_vehicle'].str.strip()
    df.loc[:,'multiple_deliveries'] = df.loc[:,'multiple_deliveries'].str.strip()
    df.loc[:,'Festival'] = df.loc[:,'Festival'].str.strip()
    df.loc[:,'City'] = df.loc[:,'City'].str.strip()

    # Excluir as linhas com a idade dos entregadores vazia
    # ( Conceitos de seleção condicional )
    null = df['Delivery_person_Age'] != 'NaN'
    df = df.loc[null, :]

    null_01 = df['Delivery_person_Ratings'] != 'NaN'
    df = df.loc[null_01, :]

    null_02 = df['Time_Orderd'] != 'NaN'
    df = df.loc[null_02, :]

    null_03 = df['Road_traffic_density'] != 'NaN'
    df = df.loc[null_03, :]

    null_04 = df['multiple_deliveries'] != 'NaN'
    df = df.loc[null_04, :]

    null_05 = df['Festival'] != 'NaN'
    df = df.loc[null_05, :]

    null_06 = df['City'] != 'NaN'
    df = df.loc[null_06, :]

    # Conversao de texto para data
    df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )

    # Conversao de texto/categoria/string para numeros inteiros
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)

    # Conversao de texto/categoria/strings para numeros decimais
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)

    #Conversao de texto/categoria/string para numeros inteiros
    df['multiple_deliveries'] = df['multiple_deliveries'].astype(int)

    # Limpando a coluna Time Taken
    df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)

    return df

def order_metric(df):

    df_aux = df.loc[:, ['ID','Order_Date']].groupby('Order_Date').count().reset_index()
    df_col = ['Order_Date','ID']
    fig = px.bar(df_aux, x='Order_Date', y='ID')

    return fig

def traffic_order_share(df): 

    df_aux = df.loc[:, ['ID', 'Road_traffic_density']].groupby( 'Road_traffic_density' ).count().reset_index()
    df_aux['deliveries_perc'] = 100 * (df_aux['ID'] / df_aux['ID'].sum())
    fig = px.pie( df_aux, values ='deliveries_perc', names ='Road_traffic_density' )         

    return fig

def traffic_order_city(df):

    df_aux = df.loc[:, ['ID', 'City','Road_traffic_density']].groupby(['City','Road_traffic_density']).count().reset_index()
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')

    return fig

def order_by_week(df):  

    df['week_of_year'] = df['Order_Date'].dt.strftime( "%U" )
    df_aux = df.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
    fig = px.line(df_aux, x='week_of_year', y='ID')

    return fig

def order_share_by_week(df):

    df_aux1 = df.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
    df_aux2 = df.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby( 'week_of_year').nunique().reset_index()
    df_aux = pd.merge( df_aux1, df_aux2, how='inner' )
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line( df_aux, x='week_of_year', y='order_by_delivery' )

    return fig

def country_maps(df):

    df_aux = df.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby( ['City','Road_traffic_density']).median().reset_index()
    map_ = folium.Map()
    for index, location_info in df_aux.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'], location_info['Delivery_location_longitude']], popup=location_info[['City', 'Road_traffic_density']] ).add_to( map_ )
    folium_static(map_, width = 1024, height = 600)
    return None

# _______________________________________________INICIO DA ESTRUTURA LÓGICA DO CÓDIGO__________________________________________________________

# Importando Dataframe
df1 = pd.read_csv('train.csv')
#r"C:\Users\usuario\Documents\projetos\FTC\train.csv"
# Limpando Dataframe
df = clean_code(df1)

#=======================================================================================================================
#1 VISÃO EMPRESA#
#=======================================================================================================================

#=======================================================================================================================
#1 SIDEBAR STREAMLIT#
#=======================================================================================================================

#Comando para exibir dataframe no streamlit: "st.dataframe(df)"

st.header('Marketplace - Visão Empresa')
#image_path = r'C:\Users\usuario\Documents\projetos\FTC\logo.png'
image = Image.open('logo.png')
st.sidebar.image(image, width = 120)
st.sidebar.markdown('# Your Company')
st.sidebar.markdown('## Fastest Delivery in Town')

st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite:')
date_slider = st.sidebar.slider(
    'Até qual valor ?',
    value = pd.datetime( 2022, 4, 13),
    min_value = pd.datetime(2022, 2, 11),
    max_value = pd.datetime(2022, 4, 6),
    format = 'DD-MM-YYYY')
st.header(date_slider)

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")

st.sidebar.markdown('## Powered By Luiz Zamian')
# Filtro de Data
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas, :]
# Filtro de Transito
linhas_selecionadas = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas_selecionadas, :]

#==================================================================================
#1 LAYOUT STREAMLIT#
#==================================================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])
with tab1:
    with st.container():
        fig = order_metric(df)
        st.markdown('# Order by Day')
        st.plotly_chart(fig, use_container_width = True)
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            fig = traffic_order_share(df)
            st.markdown('# Traffic Order Share')
            st.plotly_chart(fig, use_container_width = True)

        with col2:    
            fig = traffic_order_city(df)
            st.markdown('# Traffic Order City')
            st.plotly_chart(fig, use_container_width = True)
        
with tab2:
    with st.container():
        fig = order_by_week(df)
        st.markdown('# Order by Week')
        st.plotly_chart(fig, use_container_width = True)
    
    with st.container():
        fig = order_share_by_week(df)
        st.markdown('# Order Share by Week')
        st.plotly_chart(fig, use_container_width = True)
        
with tab3:
    st.markdown('# Country Maps')
    country_maps(df)
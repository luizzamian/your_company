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
# _______________________________________________INICIO DA ESTRUTURA LÓGICA DO CÓDIGO__________________________________________________________

# Importando dataframe
base = pd.read_csv('train.csv')
#r"C:\Users\usuario\Documents\projetos\FTC\train.csv"
# Fazendo uma cópia do DataFrame Lido
df = clean_code(base)

#==================================================================================
#2 VISÃO ENTREGADORES#
#==================================================================================

#==================================================================================
#1 SIDEBAR STREAMLIT#
#==================================================================================

#Comando para exibir dataframe no streamlit: "st.dataframe(df)"
st.header('Marketplace - Visão Entregadores')
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
#2 LAYOUT STREAMLIT#
#==================================================================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '-', '-'])
with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap = 'large')
        with col1:
            old = df.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior Idade', old)
        with col2:
            new = df.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor Idade', new)
        with col3:
            better = df.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor Condição de Veículos', better)
        with col4:
            worse = df.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior Condição de Veículos', worse)
    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')
        col1, col2 = st.columns(2, gap = 'large')
        with col1:
            st.markdown('##### Avaliação Média por Entregador')
            avg_ratings_per_delivery = (df.loc[:, ['Delivery_person_Ratings','Delivery_person_ID']].groupby(['Delivery_person_ID']).mean().reset_index())
            st.dataframe(avg_ratings_per_delivery)
        with col2:
            st.markdown('##### Avaliação Média por Trânsito')
            df_avg_std_rating_by_traffic = df.loc[:,['Delivery_person_Ratings', 'Road_traffic_density']].groupby('Road_traffic_density').agg({'Delivery_person_Ratings': ['mean','std']})
            df_avg_std_rating_by_traffic.columns = ['Delivery_mean','delivery_std']
            df_avg_std_rating_by_traffic.reset_index()
            st.dataframe(df_avg_std_rating_by_traffic)
            st.markdown('##### Avaliação Média por Clima')
            df_avg_std_rating_by_Weatherconditions = df.loc[:,['Delivery_person_Ratings', 'Weatherconditions']].groupby('Weatherconditions').agg({'Delivery_person_Ratings': ['mean','std']})
            df_avg_std_rating_by_Weatherconditions.columns = ['Delivery_mean','delivery_std']
            df_avg_std_rating_by_Weatherconditions.reset_index()
            st.dataframe(df_avg_std_rating_by_Weatherconditions)
    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de Entrega')
        col1, col2 = st.columns(2, gap = 'large')
        with col1:
            st.markdown('##### Top Entregadores Mais Rápidos')
            df_02 = (df.loc[:,['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby(['City','Delivery_person_ID']).mean().sort_values(['City','Time_taken(min)'], ascending=True).reset_index())
            dfaux_01 = df_02.loc[df_02['City'] == 'Metropolitian', :].head(10)
            dfaux_02 = df_02.loc[df_02['City'] == 'Urban', :].head(10)
            dfaux_03 = df_02.loc[df_02['City'] == 'Semi-Urban', :].head(10)
            df_03 = pd.concat( [dfaux_01, dfaux_02, dfaux_03]).reset_index(drop=True)
            st.dataframe(df_03)
        with col2:
            st.markdown('##### Top Entregadores Mais Lentos')
            df_02 = (df.loc[:,['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby(['City','Delivery_person_ID']).mean().sort_values(['City','Time_taken(min)'], ascending=False).reset_index())
            dfaux_01 = df_02.loc[df_02['City'] == 'Metropolitian', :].head(10)
            dfaux_02 = df_02.loc[df_02['City'] == 'Urban', :].head(10)
            dfaux_03 = df_02.loc[df_02['City'] == 'Semi-Urban', :].head(10)
            df_03 = pd.concat( [dfaux_01, dfaux_02, dfaux_03]).reset_index(drop=True)
            st.dataframe(df_03)
            
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

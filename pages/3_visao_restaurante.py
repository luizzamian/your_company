# Libaries
import pandas as pd
from haversine import haversine
import re
import plotly.express as px
import plotly.graph_objects as go
import folium
import streamlit as st
import numpy as np
from streamlit_folium import folium_static
from PIL import Image

# ____________________________________________________________________________________________________
# FUNÇÕES
# ____________________________________________________________________________________________________

def clean_code (df):
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
base = pd.read_csv(r"C:\Users\usuario\Documents\projetos\FTC\train.csv")

# Fazendo uma cópia do DataFrame Lido
df = clean_code(base)

#==================================================================================
#3 VISÃO ENTREGADORES#
#==================================================================================

#==================================================================================
#1 SIDEBAR STREAMLIT#
#==================================================================================

#Comando para exibir dataframe no streamlit: "st.dataframe(df)"
st.header('Marketplace - Visão Restaurante')
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
        st.title('Overal Metrics')
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            qtd = len(df['Delivery_person_ID'].unique())
            col1.metric('Entregadores Únicos', qtd)
        with col2:
            cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
            df['Distance'] = df.loc[:,cols].apply(lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1)
            df_avg_distance = np.round(df['Distance'].mean(),2)
            col2.metric('Distância Média das Entregas', df_avg_distance)
        with col3:
            df_aux = df.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            filtro = df_aux['Festival'] == 'Yes'
            df_aux = np.round(df_aux.loc[filtro, 'avg_time'], 2)
            col3.metric('Tempo Médio de Entrega - Festival', df_aux)
        with col4:
            df_aux = df.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            filtro = df_aux['Festival'] == 'Yes'
            df_aux = np.round(df_aux.loc[filtro, 'std_time'], 2)
            col4.metric('Tempo Médio de Entrega - Festival', df_aux)
        with col5:
            df_aux = df.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            filtro = df_aux['Festival'] == 'No'
            df_aux = np.round(df_aux.loc[filtro, 'avg_time'], 2)
            col5.metric('Desvio Padrão Médio de Entrega - No Festival', df_aux)
        with col6:
            df_aux = df.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            filtro = df_aux['Festival'] == 'No'
            df_aux = np.round(df_aux.loc[filtro, 'std_time'], 2)
            col6.metric('Desvio Padrão Médio de Entrega - No Festival', df_aux)
    with st.container():
        st.markdown("""---""")
        st.title('Tempo Médio de Entrega po Cidade')
        col1, col2 = st.columns(2)
        with col1:
            cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
            df['Distance'] = df.loc[:,cols].apply(lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1)
            df_avg_distance = df.loc[:,['Distance', 'City']].groupby('City').mean().reset_index()
            fig = go.Figure(data =[go.Pie(labels = df_avg_distance['City'], values = df_avg_distance['Distance'], pull = [0.1, 0.1, 0.1])])
            st.plotly_chart(fig)
        with col2:
            df_avg_std_city = df.loc[:,['Time_taken(min)', 'City']].groupby('City').agg({'Time_taken(min)': ['mean','std']})
            df_avg_std_city.columns = ['Delivery_mean','Delivery_std']
            df_avg_std_city = df_avg_std_city.reset_index()
            fig = go.Figure()
            fig.add_trace(go.Bar(name = 'Control', x = df_avg_std_city['City'], y = df_avg_std_city['Delivery_mean'], error_y = dict(type = 'data', array = df_avg_std_city['Delivery_std'])))
            fig.update_layout(barmode = 'group')
            st.plotly_chart(fig)  
    with st.container():
        st.markdown("""---""")
        cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
        df_avg_std_traffic = df.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean','std']})
        df_avg_std_traffic.columns = ['Traffic_Time_mean','Traffic_Time_std']
        df_avg_std_traffic = df_avg_std_traffic.reset_index()
        fig = px.sunburst(df_avg_std_traffic, path = ['City', 'Road_traffic_density'], values = 'Traffic_Time_mean', color = 'Traffic_Time_std', color_continuous_scale ='RdBu', color_continuous_midpoint = np.average(df_avg_std_traffic['Traffic_Time_std']))
        st.plotly_chart(fig)   
    with st.container():
        st.markdown("""---""")
        df_avg_std_type_order = df.loc[:,['Time_taken(min)', 'Type_of_order']].groupby('Type_of_order').agg({'Time_taken(min)': ['mean','std']})
        df_avg_std_type_order.columns = ['Order_Time_mean','Order_Time_std']
        df1 = df_avg_std_type_order.reset_index()
        st.dataframe(df1)
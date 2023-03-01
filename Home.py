import streamlit as st
from PIL import Image

st.set_page_config(page_title = 'Home')

#image_path = r'C:\Users\usuario\Documents\projetos\FTC\logo.png'
image = Image.open('logo.png')
st.sidebar.image( image, width = 120)
st.sidebar.markdown('# Your Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write(" ## Your Company Growth Dashboard")

st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as Métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar:
- Visão Empresa:
    - Visão Gerencial: Métricas gerais de comportamento;
    - Visão Tática: Indicadores semanais de crescimento;
    - Visão Geográfica: Insights de geolocalização.
- Visão Entregadores:
    - Acompanhamento dos indicadores semanais de crescimento.
- Visão Restaurantes:
    - Indicadores semanais de crescimento dos restaurantes""")
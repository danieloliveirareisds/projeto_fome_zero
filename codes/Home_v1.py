#IMPORTANDO AS BIBLIOTECAS
import pandas as pd
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
import inflection
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static
import locale


#FUNÇÕES

DATA_PATH = f"data/old/zomato.csv"

COUNTRIES = {
    1: "India",
    14: "Australia",
    30: "Brazil",
    37: "Canada",
    94: "Indonesia",
    148: "New Zeland",
    162: "Philippines",
    166: "Qatar",
    184: "Singapure",
    189: "South Africa",
    191: "Sri Lanka",
    208: "Turkey",
    214: "United Arab Emirates",
    215: "England",
    216: "United States of America",
}


COLORS = {
    "3F7E00": "darkgreen",
    "5BA829": "green",
    "9ACD32": "lightgreen",
    "CDD614": "orange",
    "FFBA00": "red",
    "CBCBC8": "darkred",
    "FF7800": "darkred",
}


def rename_columns(dataframe):
    df = dataframe.copy()

    title = lambda x: inflection.titleize(x)

    snakecase = lambda x: inflection.underscore(x)

    spaces = lambda x: x.replace(" ", "")

    cols_old = list(df.columns)

    cols_old = list(map(title, cols_old))

    cols_old = list(map(spaces, cols_old))

    cols_new = list(map(snakecase, cols_old))

    df.columns = cols_new

    return df


def country_name(country_id):
    """ 
     1. Para colocar o nome dos países com base no código de cada país
        
        Preenchimento do nome dos países
    """
    return COUNTRIES[country_id]

def create_price_tye(price_range):
    """
    2. Criar a categoria do tipo de comida com base no range de valores.

        Criação do Tipo de Categoria de Comida
    """
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
     
     return "normal"
    
    elif price_range == 3:
        return "expensive"
    
    else:
        return "gourmet"
    
def color_name(color_code):
    """
    3. Criar o nome das cores com base nos códigos de cores
        Criação do nome das Cores
    """
    return COLORS[color_code]


def adjust_columns_order(dataframe):
    df = dataframe.copy()

    new_cols_order = [
        "restaurant_id",
        "restaurant_name",
        "country_name",
        "city",
        "address",
        "locality",
        "locality_verbose",
        "longitude",
        "latitude",
        "cuisines",
        "price_type",
        "average_cost_for_two",
        "currency",
        "has_table_booking",
        "has_online_delivery",
        "is_delivering_now",
        "aggregate_rating",
        "rating_color",
        "color_name",
        "rating_text",
        "votes",
    ]

    return df.loc[:, new_cols_order]

def process_data(file_path):
    df = pd.read_csv(file_path)

    df = df.dropna()

    df = rename_columns(df)

    df["price_type"] = df.loc[:, "price_range"].apply(lambda x: create_price_tye(x))

    df["country_name"] = df.loc[:, "country_code"].apply(lambda x: country_name(x))

    df["color_name"] = df.loc[:, "rating_color"].apply(lambda x: color_name(x))

    df["cuisines"] = df.loc[:, "cuisines"].apply(lambda x: x.split(",")[0])

    df = df.drop_duplicates()

    df = adjust_columns_order(df)

    df.to_csv("data/processed/zomato.csv", index=False)

    return df

# =============================================================
# FUNÇÃO DO MAPA
# =============================================================

def create_map(df1):

    df1_aux = (df1.loc[:, ['city', 'aggregate_rating', 'restaurant_name', 'cuisines', 'average_cost_for_two', 'restaurant_id', 'currency', 'color_name', 'latitude', 'longitude']]
                                    .groupby(['city', 'cuisines', 'color_name', 'currency', 'restaurant_id', 'restaurant_name'])
                                    .median().reset_index())

    map = folium.Map()
    marker_cluster = folium.plugins.MarkerCluster().add_to(map)

    for i in range( len(df1_aux) ):
        
        popup_html = f'<div style="width: 250px;">' \
                    f"<b>{df1_aux.loc[i, 'restaurant_name']}</b><br><br>" \
                    \
                    f"Preço para dois: {df1_aux.loc[i, 'average_cost_for_two']:,.2f} ( {df1_aux.loc[i, 'currency']})<br> " \
                    f"Type: {df1_aux.loc[i, 'cuisines']}<br>" \
                    f"Nota: {df1_aux.loc[i, 'aggregate_rating']}/5.0" \
                    f'</div>'

        folium.Marker([df1_aux.loc[i, 'latitude'], df1_aux.loc[i, 'longitude']], 
                    popup=popup_html, width=500, height=500, parse_html=True, 
                    zoom_tart=30, titles='Stamen Toner', 
                    icon=folium.Icon(color=df1_aux.loc[i, 'color_name'], icon='home')).add_to(marker_cluster)

    folium_static(map, width=1024, height=768)

# =============================================================
# BARRA LATERAL
# =============================================================
def create_sidebar(df1):
    col1, col2 = st.sidebar.columns([1, 4])

    image_path=('logo.png')
    image = Image.open( image_path)
    col1.image(image, width=40)

    col2.write('# Fome Zero')

    st.sidebar.markdown('# Filtros')

    default_options = ['Brazil', 'England', 'Qatar', 'South Africa', 'Canada', 'Australia']
    
    countries = st.sidebar.multiselect('Escolha os Paises que Deseja visualizar as informações:',
                                            df1['country_name'].unique().tolist(), default=default_options )

    st.sidebar.markdown( """___""" )
    st.sidebar.write('## Dados Tratados' )

    @st.cache_data
    def convert_df(df1):
        #Função para converter o dataframe em arquivo csv
        return df1.to_csv().encode('utf-8')
        
    csv = convert_df(df1)

    st.sidebar.download_button(label='Download',
                            data=csv,
                            file_name='dados.csv',
                            mime='text/csv')
    st.sidebar.markdown( """___""" )
    st.sidebar.markdown( '#### Powered by Daniel Reis' )
    
    return list(countries)



# leitura dos dados não tratados
df_raw = pd.read_csv(DATA_PATH)


# Renomeando os dados já tratados
df1 = process_data(DATA_PATH)



# =============================================================
# Layout Streamlit
# =============================================================

st.set_page_config(page_title="Home", page_icon="📊", layout="wide")

#FUNÇÃO BARRAL LATERAL
selected_countries = create_sidebar(df1)

st.title('Fome Zero')
st.markdown('## O melhor lugar para encontrar seu mais novo restaurante favorito!')
st.markdown ('### Temos as seguintes marcas dentro da nossa plataforma:')


restaurant, country, cities, rating, cuisine = st.columns(5, gap='small')

with st.container():
    with restaurant:
        #Quantidade de restaurantes cadastrados
        df1_aux = df1.loc[:, 'restaurant_id'].nunique()
        restaurant.metric('Restaurantes Cadastrados ', df1_aux)
    
    with country:
        #Quantidade de Países
        df1_aux = df1['country_name'].nunique()
        country.metric('Países Cadastrados', df1_aux)
    
    with cities:
        #Quantidade de cidades
        df1_aux = df1['city'].nunique()
        cities.metric('Cidades Cadastradas', df1_aux)
    
    with rating:
        #Quantidade de Avaliações
        df1_aux = df1['votes'].sum()
        rating.metric("Avaliações Feitas na Plataforma",
        f"{df1_aux:,}".replace(",", ".") )
    
    with cuisine:
        #Quantidade de tipos de culinárias
        df1_aux = df1['cuisines'].nunique()
        cuisine.metric('Tipos de Culinárias Oferecidas', df1_aux)
    


st.write('### 🌎 Mapa com a Localização dos Restaurantes')

#FUNÇÃO DO MAPA COM A LOCALIZAÇÃO DOS RESTAURANTES
map_df1 = df1.loc[df1['country_name'].isin(selected_countries), :]
create_map(map_df1)


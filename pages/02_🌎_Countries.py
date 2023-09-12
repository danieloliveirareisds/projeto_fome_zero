#IMPORTANDO AS BIBLIOTECAS
import pandas as pd
import plotly.express as px
import inflection
import streamlit as st




st.set_page_config(page_title="Countries", page_icon="🌎", layout="wide")


DATA_PATH = f"data/old/zomato.csv"

# leitura dos dados não tratados
df_raw = pd.read_csv(DATA_PATH)

# =============================================================
# FUNÇÕES DE AJUDA
# =============================================================

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

def clean_code(file_path):
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
# FUNÇÃO BARRA LATERAL
# =============================================================
def create_sidebar(df1):
    st.sidebar.markdown('# Filtros')

    default_options = ['Brazil', 'England', 'Qatar', 'South Africa', 'Canada', 'Australia']
    
    country = st.sidebar.multiselect('Escolha os Paises que Deseja visualizar as informações:',
                                            df1['country_name'].unique().tolist(), default=default_options )

   
    st.sidebar.markdown( """___""" )
    st.sidebar.markdown( '#### Powered by Daniel Reis' )
    
    return list(country)

# =============================================================
# FUNÇÕES GRÁFICOS
# =============================================================

def price_country(country):
    df1_aux = (df1.loc[:, ['average_cost_for_two', 'country_name']]
                        .groupby('country_name')
                        .mean().sort_values('average_cost_for_two', ascending=False)
                        .reset_index() )
        
    fig = px.bar( df1_aux, x="country_name", y="average_cost_for_two",
        text="average_cost_for_two", text_auto=".2f", labels={
        "country_name": "Países",
        "average_cost_for_two": "Preço de prato para duas Pessoas"
        } , template='plotly_dark', )
            
    fig.update_layout(title_text='Média de Preço de um prato para duas pessoas por País', title_x=0.3)
    fig.update_traces(marker_line_color = 'rgb(8,48,107)', marker_line_width = 1.5 )
    return fig


def mean_votes(country):
    df1_aux = ( df1.loc[:,['country_name','votes']]
                        .groupby('country_name')
                        .mean()
                        .sort_values(by='votes',ascending=False)
                        .reset_index() )
        
    fig = px.bar(df1_aux, x='country_name', y='votes', 
                        text='votes', text_auto='.2f',
                        labels={
                            'country_name': 'Países',
                            'votes': 'Quantidade de Avaliações'
                        }, template='plotly_dark' )
    fig.update_layout(title_text='Média de Avaliações feitas por País', title_x=0.4)        
    fig.update_traces(marker_line_color = 'rgb(8,48,107)', marker_line_width = 1.5 )
            
    return fig



def qtd_cities(country):
    df1_aux = (df1.loc[:, ['country_name', 'city']]
                        .groupby('country_name')
                        .nunique()
                        .sort_values('city', ascending=False)
                        .reset_index() )

    fig = px.bar(df1_aux, x='country_name', y='city', 
                text_auto='city', labels={
                     'city': 'Quantidade de Cidades',
                     'country_name': 'Países'
                 }, template='plotly_dark' )
    fig.update_layout(title_text='Quantidade de Cidades por País', title_x=0.4)
    fig.update_traces(marker_line_color = 'rgb(8,48,107)', marker_line_width = 1.5)
    
    return fig


def restaurant_country(country):
    df1_aux = (df1.loc[:,['country_name','restaurant_id']]
                            .groupby(['country_name'])
                            .count()
                            .sort_values('restaurant_id', ascending=False)
                            .reset_index() )
    
    fig = px.bar(df1_aux, x='country_name', y='restaurant_id', 
                    text_auto= 'restaurant_id', labels= {
                        'country_name': 'Países',
                        'restaurant_id': 'Quantidade de Restaurantes'
                    } , template='plotly_dark')
    
    fig.update_layout(title_text='Quantidade de Restaurantes por País', title_x=0.4)
    fig.update_traces(marker_line_color = 'rgb(8,48,107)', marker_line_width = 1.5)    

    return fig


# Renomeando os dados já tratados
df1 = clean_code(DATA_PATH)

# =============================================================
# Layout Streamlit
# =============================================================

#FUNÇÃO BARRAL LATERAL
country = create_sidebar(df1)

#Filtro dos paises nos gráficos
filter_graph = df1['country_name'].isin(country)
df1 = df1.loc[filter_graph, :]


st.title('🌎 Visão Países')
with st.container():
    fig = restaurant_country(country)
    st.plotly_chart(fig, use_container_width=True)
    
    

with st.container():
    fig = qtd_cities(country)
    st.plotly_chart(fig, use_container_width=True)



with st.container():
    col1, col2 = st.columns([2,2])

    with col1:
        fig = mean_votes(country)
        st.plotly_chart(fig, use_container_width=True)
   
    
    with col2:
        fig = price_country(country)
        st.plotly_chart(fig, use_container_width=True)

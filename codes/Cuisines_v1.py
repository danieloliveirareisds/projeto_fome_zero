#IMPORTANDO AS BIBLIOTECAS
import pandas as pd
import plotly.express as px
import inflection
import streamlit as st



st.set_page_config(page_title="Cuisines", page_icon="🍽️", layout="wide")

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



def process_data(file_path):
    df = pd.read_csv(file_path)

    df = df.dropna()

    df = rename_columns(df)

    df["price_type"] = df.loc[:, "price_range"].apply(lambda x: create_price_tye(x))

    df["country_name"] = df.loc[:, "country_code"].apply(lambda x: country_name(x))

    df["color_name"] = df.loc[:, "rating_color"].apply(lambda x: color_name(x))

    df["cuisines"] = df.loc[:, "cuisines"].apply(lambda x: x.split(",")[0])

    df = df.drop_duplicates()

    df.to_csv("data/processed/zomato.csv", index=False)

    return df

def top_cuisines():
    

    cuisines = {
        "Italian": "",
        "American": "",
        "Arabian": "",
        "Japanese": "",
        "Brazilian": "",
    }

    cols = [
        "restaurant_id",
        "restaurant_name",
        "country_name",
        "city",
        "cuisines",
        "average_cost_for_two",
        "currency",
        "aggregate_rating",
        "votes",
    ]

    for key in cuisines.keys():

        lines = df1["cuisines"] == key

        cuisines[key] = (
            df1.loc[lines, cols]
            .sort_values(["aggregate_rating", "restaurant_id"], ascending=[False, True])
            .iloc[0, :]
            .to_dict()
        )

    return cuisines

def top_worst_cuisines(top_n, countries):
    
    lines = df1['country_name'].isin(countries)
            
    df_aux1 = ( df1.loc[lines, ['cuisines', 'aggregate_rating']]
                        .groupby(['cuisines'])
                        .mean()
                        .sort_values('aggregate_rating', ascending=True)
                        .reset_index().head(top_n).round(2) )

            

    fig = px.bar( df_aux1, x='cuisines', y='aggregate_rating', text='aggregate_rating', template='plotly_dark', 
                        labels={
                            'cuisines': 'Tipo de Culinária',
                            'aggregate_rating': 'Média da Avaliação Média'
                        }  )
    fig.update_layout(title_text=f'Top {top_n} Piores Tipos de Culinárias', title_x=0.4)
    fig.update_traces(marker_line_color = 'rgb(8,48,107)', marker_line_width = 1.5)
            

    return fig

def top_best_cuisines(top_n, countries):
            
            lines = df1['country_name'].isin(countries)
            
            df_aux1 = ( df1.loc[lines, ['cuisines', 'aggregate_rating']]
                        .groupby(['cuisines'])
                        .mean()
                        .sort_values('aggregate_rating', ascending=False)
                        .reset_index().head(top_n).round(2) )

            

            fig = px.bar( df_aux1, x='cuisines', y='aggregate_rating', text='aggregate_rating', template='plotly_dark', 
                        labels={
                            'cuisines': 'Tipo de Culinária',
                            'aggregate_rating': 'Média da Avaliação Média'
                        }  )
            fig.update_layout(title_text=f'Top {top_n} Melhores Tipos de Culinárias', title_x=0.4)
            fig.update_traces(marker_line_color = 'rgb(8,48,107)', marker_line_width = 1.5)

            return fig

def top_restaurants(countries, cozinhas, top_n):
    
    st.markdown(f'## Top {top_n} Restaurantes')
    
    lines = (df1['cuisines'].isin(cozinhas)) & (df1['country_name'].isin(countries))
        
    cols = ['restaurant_name', 'restaurant_id', 'country_name','city', 'cuisines' , 'average_cost_for_two' ,'aggregate_rating', 'votes']

    tabela = df1.loc[lines, cols].sort_values(['aggregate_rating', 'restaurant_id'], ascending=[False, True]).head(top_n) 
    
    return tabela

# leitura dos dados não tratados
df_raw = pd.read_csv(DATA_PATH)


# Renomeando os dados já tratados
df1 = process_data(DATA_PATH)

# =============================================================
# BARRA LATERAL
# =============================================================
def make_sidebar(df1):

    st.sidebar.markdown( """___""" )
    st.sidebar.markdown('# Filtros')

    default_options = ['Brazil', 'England', 'Qatar', 'South Africa', 'Canada', 'Australia']
            
    countries = st.sidebar.multiselect('Escolha os Paises que Deseja visualizar as informações:',
                        df1['country_name'].unique().tolist(), default=default_options )

    top_n = st.sidebar.slider('Selecione a quantidade de Restaurantes que deseja visualizar', 1, 20, 10)
            
    default_options2 = ['Home-made', 'BBQ', 'Japanese', 'Brazilian', 
                            'Arabian', 'American', 'Italian']   
    cozinhas = st.sidebar.multiselect('Escolha os Tipos de Culinárias:',
    df1.loc[:, 'cuisines'].unique().tolist(), default=default_options2)
   
   
    st.sidebar.markdown( """___""" )
    st.sidebar.markdown( '#### Powered by Daniel O. Reis' )

    return list(countries), top_n, list(cozinhas)

# =============================================================
# Layout Streamlit
# =============================================================
st.title('🍽️ Visão Tipos de Cozinhas')
st.markdown('## Melhores Restaurantes dos Principais tipos Culinários:')

cuisines = top_cuisines()

italian, american, arabian, japonese, brazilian = st.columns(len(cuisines))

with st.container():
    with italian:
       st.metric(
            label=f'Italiana: {cuisines["Italian"]["restaurant_name"]}',
            value=f'{cuisines["Italian"]["aggregate_rating"]}/5.0',
            help=f"""
            País: {cuisines["Italian"]['country_name']}\n
            Cidade: {cuisines["Italian"]['city']}\n
            Média Prato para dois: {cuisines["Italian"]['average_cost_for_two']} ({cuisines["Italian"]['currency']})
            """,
        )
    with american:
        st.metric(
            label=f'Italiana: {cuisines["American"]["restaurant_name"]}',
            value=f'{cuisines["American"]["aggregate_rating"]}/5.0',
            help=f"""
            País: {cuisines["American"]['country_name']}\n
            Cidade: {cuisines["American"]['city']}\n
            Média Prato para dois: {cuisines["American"]['average_cost_for_two']} ({cuisines["American"]['currency']})
            """,
        )
    
    with arabian:
        st.metric(
            label=f'Italiana: {cuisines["Arabian"]["restaurant_name"]}',
            value=f'{cuisines["Arabian"]["aggregate_rating"]}/5.0',
            help=f"""
            País: {cuisines["Arabian"]['country_name']}\n
            Cidade: {cuisines["Arabian"]['city']}\n
            Média Prato para dois: {cuisines["Arabian"]['average_cost_for_two']} ({cuisines["Arabian"]['currency']})
            """,
        )
    
    with japonese:
        st.metric(
            label=f'Italiana: {cuisines["Japanese"]["restaurant_name"]}',
            value=f'{cuisines["Japanese"]["aggregate_rating"]}/5.0',
            help=f"""
            País: {cuisines["Japanese"]['country_name']}\n
            Cidade: {cuisines["Japanese"]['city']}\n
            Média Prato para dois: {cuisines["Japanese"]['average_cost_for_two']} ({cuisines["Japanese"]['currency']})
            """,
        )
    
    with brazilian:
        st.metric(
            label=f'Italiana: {cuisines["Brazilian"]["restaurant_name"]}',
            value=f'{cuisines["Brazilian"]["aggregate_rating"]}/5.0',
            help=f"""
            País: {cuisines["Brazilian"]['country_name']}\n
            Cidade: {cuisines["Brazilian"]['city']}\n
            Média Prato para dois: {cuisines["Brazilian"]['average_cost_for_two']} ({cuisines["Brazilian"]['currency']})
            """,
        )



countries, top_n, cozinhas = make_sidebar(df1)

tabela = top_restaurants(countries, cozinhas, top_n)
st.dataframe(tabela)

top_best, top_worst = st.columns([1,1], gap='small')

with top_best:
    fig = top_best_cuisines(top_n, countries)
    st.plotly_chart(fig, use_container_width=True ) 
    
with top_worst:
    fig = top_worst_cuisines(top_n, countries)
    st.plotly_chart(fig, use_container_width=True ) 
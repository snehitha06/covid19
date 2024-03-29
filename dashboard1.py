import pandas as pd
pd.set_option('max_rows',20)
import plotly.express as px
import plotly.io as pio
pio.renderers.default = "browser"
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
CONF_URL = 'https://raw.githubusercontent.com/snehitha06/covid19/main/time_series_covid_19_confirmed.csv'
DEAD_URL = 'https://raw.githubusercontent.com/snehitha06/covid19/main/time_series_covid_19_deaths.csv'
RECV_URL = 'https://raw.githubusercontent.com/snehitha06/covid19/main/time_series_covid_19_recovered.csv'
covid_conf_ts = pd.read_csv(CONF_URL)
covid_dead_ts = pd.read_csv(DEAD_URL)
covid_recv_ts = pd.read_csv(RECV_URL)
#get data in cleaned time series format for country
def process_data(data,cntry='India',window=3):
    conf_ts = data
    conf_ts_cntry = conf_ts[conf_ts['Country/Region']==cntry]
    final_dataset = conf_ts_cntry.T[4:].sum(axis='columns').diff().rolling(window=window).mean()[40:]
    df = pd.DataFrame(final_dataset,columns=['Total'])
    return df
#get overall wordlwide total for confirmed, recovered and dead cases
def get_overall_total(df):
    return df.iloc[:,-1].sum()

conf_overall_total = get_overall_total(covid_conf_ts)
dead_overall_total = get_overall_total(covid_dead_ts)
recv_overall_total = get_overall_total(covid_recv_ts)
print('Overall Confirmed:',conf_overall_total)
print('Overall Dead:',dead_overall_total)
print('Overall Recovered:',recv_overall_total)
#get total for confirmed, recovered and dead for country 
def get_cntry_total(df,cntry='India'):
    return df[df['Country/Region']==cntry].iloc[:,-1].sum()

cntry = 'India'
conf_cntry_total = get_cntry_total(covid_conf_ts,cntry)
dead_cntry_total = get_cntry_total(covid_dead_ts,cntry)
recv_cntry_total = get_cntry_total(covid_recv_ts,cntry)
print(f'{cntry} Confirmed:',conf_cntry_total)
print(f'{cntry} Dead:',dead_cntry_total)
print(f'{cntry} Recovered:',recv_cntry_total)
def fig_world_trend(cntry='India',window=3):
    df = process_data(data=covid_conf_ts,cntry=cntry,window=window)
    df.head(10)
    if window==1:
        yaxis_title = "Daily Cases"
    else:
        yaxis_title = "Daily Cases ({}-day MA)".format(window)
    fig = px.line(df, y='Total', x=df.index, title='Daily confirmed cases trend for {}'.format(cntry),height=600,color_discrete_sequence =['maroon'])
    fig.update_layout(title_x=0.5,plot_bgcolor='#F2DFCE',paper_bgcolor='#F2DFCE',xaxis_title="Date",yaxis_title=yaxis_title)
    return fig
external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Covid-19 Dashboard'
colors = {
    'background': '#111111',
    'bodyColor':'#F2DFCE',
    'text': '#7FDBFF'
}
def get_page_heading_style():
    return {'backgroundColor': colors['background']}


def get_page_heading_title():
    return html.H1(children='COVID-19 Dashboard',
                                        style={
                                        'textAlign': 'center',
                                        'color': colors['text']
                                    })

def get_page_heading_subtitle():
    return html.Div(children='Visualize Covid-19 data generated from sources all over the world.',
                                         style={
                                             'textAlign':'center',
                                             'color':colors['text']
                                         })

def generate_page_header():
    main_header =  dbc.Row(
                            [
                                dbc.Col(get_page_heading_title(),md=12)
                            ],
                            align="center",
                            style=get_page_heading_style()
                        )
    subtitle_header = dbc.Row(
                            [
                                dbc.Col(get_page_heading_subtitle(),md=12)
                            ],
                            align="center",
                            style=get_page_heading_style()
                        )
    header = (main_header,subtitle_header)
    return header
def get_country_list():
    return covid_conf_ts['Country/Region'].unique()

def create_dropdown_list(cntry_list):
    dropdown_list = []
    for cntry in sorted(cntry_list):
        tmp_dict = {'label':cntry,'value':cntry}
        dropdown_list.append(tmp_dict)
    return dropdown_list

def get_country_dropdown(id):
    return html.Div([
                        html.Label('Select Country'),
                        dcc.Dropdown(id='my-id'+str(id),
                            options=create_dropdown_list(get_country_list()),
                            value='India'
                        ),
                        html.Div(id='my-div'+str(id))
                    ])
def graph1():
    return dcc.Graph(id='graph1',figure=fig_world_trend('India'))
def generate_card_content(card_header,card_value,overall_value):
    card_head_style = {'textAlign':'center','fontSize':'150%'}
    card_body_style = {'textAlign':'center','fontSize':'200%'}
    card_header = dbc.CardHeader(card_header,style=card_head_style)
    card_body = dbc.CardBody(
        [
            html.H5(f"{int(card_value):,}", className="card-title",style=card_body_style),
            html.P(
                "Worlwide: {:,}".format(overall_value),
                className="card-text",style={'textAlign':'center'}
            ),
        ]
    )
    card = [card_header,card_body]
    return card
def generate_cards(cntry='India'):
    conf_cntry_total = get_cntry_total(covid_conf_ts,cntry)
    dead_cntry_total = get_cntry_total(covid_dead_ts,cntry)
    recv_cntry_total = get_cntry_total(covid_recv_ts,cntry)
    cards = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(dbc.Card(generate_card_content("Recovered",recv_cntry_total,recv_overall_total), color="success", inverse=True),md=dict(size=2,offset=3)),
                    dbc.Col(dbc.Card(generate_card_content("Confirmed",conf_cntry_total,conf_overall_total), color="warning", inverse=True),md=dict(size=2)),
                    dbc.Col(dbc.Card(generate_card_content("Dead",dead_cntry_total,dead_overall_total),color="dark", inverse=True),md=dict(size=2)),
                ],
                className="mb-4",
            ),
        ],id='card1'
    )
    return cards
def get_slider():
    return html.Div([  
                        dcc.Slider(
                            id='my-slider',
                            min=1,
                            max=15,
                            step=None,
                            marks={
                                1: '1',
                                3: '3',
                                5: '5',
                                7: '1-Week',
                                14: 'Fortnight'
                            },
                            value=3,
                        ),
                        html.Div([html.Label('Select Moving Average Window')],id='my-div'+str(id),style={'textAlign':'center'})
                    ])
def generate_layout():
    page_header = generate_page_header()
    layout = dbc.Container(
        [
            page_header[0],
            page_header[1],
            html.Hr(),
            generate_cards(),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(get_country_dropdown(id=1),md=dict(size=4,offset=4))                    
                ]
            
            ),
            dbc.Row(
                [                
                    
                    dbc.Col(graph1(),md=dict(size=6,offset=3))
        
                ],
                align="center",

            ),
            dbc.Row(
                [
                    dbc.Col(get_slider(),md=dict(size=4,offset=4))                    
                ]
            
            ),
        ],fluid=True,style={'backgroundColor': colors['bodyColor']}
    )
    return layout
app.layout = generate_layout()
@app.callback(
    [Output(component_id='graph1',component_property='figure'), #line chart
    Output(component_id='card1',component_property='children')], #overall card numbers
    [Input(component_id='my-id1',component_property='value'), #dropdown
     Input(component_id='my-slider',component_property='value')] #slider
)
def update_output_div(input_value1,input_value2):
    return fig_world_trend(input_value1,input_value2),generate_cards(input_value1)
app.run_server(host= '0.0.0.0',debug=False)
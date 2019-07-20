import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import plotly.figure_factory as ff
import numpy as np
import pandas as pd
from scipy import stats
import flask
from sqlalchemy import create_engine

################    Read data in from DB      #############################
engine = create_engine('sqlite:///data/HealthIndicatorsData.db')
county_data = pd.read_sql('county_data', con=engine)
state_data = pd.read_sql('state_data', con=engine)
all_counties = pd.read_sql('county_health_rankings_data', con=engine)
pstates = pd.read_sql('pstates', con=engine)

################    Define Variables for Drop downs     #############################
laura_dropdowns = ['Binge Drinking', 'Cancer Excl Skin Cancer', 'Asthma', 'COPD', 'High Blood Pressure', 'Smoking CDC', 'Kidney Disease', 'Poor Mental Health', 'Poor Physical Health' ,'% Smokers', '% Excessive Drinking', '% Unemployed', 'Drug Overdose Mortality Rate']
ayo_dropdowns = ['High Cholesterol', 'Cholesterol Screening', 'Obesity CDC', '% Obese', 'Dental Visits', 'Teeth Lost']
pre_care_dropdowns = ['Select Preventative Care Factor','Cholesterol Screening','Colon Screening',
                 'Core Med Services Female', 'Core Med Services Male', 'Dental Visits', '% Mammography', 'Routine Checkup']
finan_heal_dropdowns = ['Select Financial Factor','Lack Health Insurance', '% Children in Poverty', '% Unemployed', 'Household Income']
state_dropdowns = state_data['State']
state_dropdowns.append(pd.Series(['All']))
county_dropdowns = county_data['County']
county_dropdowns.append(pd.Series(['All']))
PAGE_SIZE = 25
pcts = [col for col in all_counties if col.startswith('% ')]

################    Function to mak the map      #############################
fips=all_counties['fips_county'].tolist()
val=all_counties['% Obese']
val=val.tolist()
fips,val = zip(*sorted(zip(fips,val)))

fig1 = ff.create_choropleth(
                fips=fips, 
                values=val,
                scope=['usa'],
                title='% Obese in County',
                binning_endpoints=np.histogram_bin_edges(val, bins=20, range=[0,100]).tolist(),
                showlegend=True)

def lm(x,y):
    slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
    return slope * x + intercept

def model_data(x,y):
    slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
    df = pd.DataFrame([[slope, intercept, r_value, p_value, std_err]],columns=['slope', 'intercept', 'r_value', 'p_value', 'std_err'])
    return df


################   Define the Dash APP     #############################

app = dash.Dash(
    __name__
)

server = app.server

url_bar_and_content_div = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

layout_index = html.Div([
    html.Div([
        html.H2('''
        UNCC Data Analysis and Visualization Bootcamp - Project2
        ''', className="display-3"),
        html.P('Ayo, Laura, Mark and Scott ', className='lead')
    ],className='jumbotron'),
    html.Div([
        html.Div([
            dcc.Link("Navigate to Ayo's page", href='/ayo', className='btn btn-primary btn-lg'),
        ],className='col-3'),
        html.Div([
            dcc.Link("Navigate to Laura's page", href='/laura', className='btn btn-primary btn-lg'),
        ],className='col-3'),
        html.Div([
            dcc.Link("Navigate to Mark's page", href='/mark', className='btn btn-primary btn-lg'),
        ],className='col-3'),
        html.Div([
           dcc.Link('Navigate to the data tables', href='/data', className='btn btn-primary btn-lg'),
        ],className='col-3')
    ], className='row'),
    html.Br(),
    html.Div([
        html.Div(
            dcc.Graph(id='choropleth-graph',figure=fig1)
        ,className='col-8'),
        html.Div([
            html.Br(),
            html.H4('Health Indicator'),
            dcc.Dropdown(
                id='indicator-dropdown',
                options=[{'label': i, 'value': i} for i in all_counties[pcts].columns],
                value='% Obese')
        ],className='col-4')
    ], className='row')
],className='container-fluid')

layout_page_ayo = html.Div([
    html.Div([
        html.Div(html.H2("Ayo's Place")
        ,className='col-4'),
        html.Div(
            html.Nav(className = "nav nav-pills", children=[html.A('Homepage', className="nav-item nav-link active btn", href='/')])
        ,className='col-2'),
        html.Div(
            html.Nav(className = "nav nav-pills", children=[html.A("Laura's", className="nav-item nav-link active btn", href='/laura')])
        ,className='col-2'),
        html.Div(
            html.Nav(className = "nav nav-pills", children=[html.A("Mark's", className="nav-item nav-link active btn", href='/mark')])
        ,className='col-2'),
        html.Div(
            html.Nav(className = "nav nav-pills", children=[html.A('Data Tables', className="nav-item nav-link active btn", href='/data')])
        ,className='col-2')       
    ], className='row mx-md-5'),

    html.Div([
        html.Div([
            html.H4('X Axis'),
                dcc.Dropdown(
                id='crossfilter-xaxis-column',
                #options=[{'label': i, 'value': i} for i in county_data.select_dtypes('float').columns],
                options=[{'label': i, 'value': i} for i in ayo_dropdowns],
                value='% Obese')
            ], className='col-md-3'),
        html.Div([
            html.H4('Y Axis'),
                dcc.Dropdown(
                id='crossfilter-yaxis-column',
                options=[{'label': i, 'value': i} for i in ayo_dropdowns],
                value='High Cholesterol')
            ], className='col-md-3'),
        html.Div(className='col-md-6'),
    ],className='row mx-md-5'),
    
    html.Div([
        dcc.Graph(id='page-ayo-scatter',
                figure={
                    'data': [ go.Scatter(x=county_data['% Obese'], y=county_data['High Cholesterol'], mode = 'markers', opacity=0.5) ],
                    'layout': go.Layout(xaxis={'title': '% Obese'}, 
                                        yaxis={'title': 'High Cholesterol'}, 
                                        margin={'l': 10, 'b': 10, 't': 10, 'r': 10},
                                        hovermode='closest',
                                        autosize=False
                )
                }
        , className='col-md-6'),
        dcc.Markdown('''
                    ### Is There a Correlation Between % Obese and High Cholesterol by County/State?
                    - Looking at the scatter plot, we see that it is clustered moving upwards. Each circle represents a county in a State. There is a connection between the two variables. As high cholesterol variable increases (range 28 - 40), so does the % obese for the counties represented. A lot of the counties are clustered together. The interactive scatter plot also shows different measures against obesity, which was a particular interest. The scatter plot reveals much of the same trend using both the Health Data Rankings and the CDC Data for obesity, high cholesterol, and cholesterol screening.
                    ### Is There a Correlation Between Teeth Lost prevalence and Dental Visits for Age 65 and up by State?
                    - Looking at the bar chart, I was curious to see what kind of relationship I will see between the prevalence of all teeth lost among adults 65 years and up to the dental visits. Hawaii, for example, has the lowest teeth lost predominance (7) and very high dental visits (72). So, no correlation there. However, if we look at Delaware and Mississippi, they both have the highest measure of teeth lost prevalence (24 and 25, respectively) with dental visits not as high (51 and 52). The more teeth lost the less dental visits for age 65 and up in both these States. Overall the bar chart shows very little correlation between these variables.
                    ''',className='col-md-6')
    ], className='row mx-md-5'),

    html.Div([
        html.Div(id='page-ayo-table', children=dash_table.DataTable( 
                                        columns=[{'name':n, 'id':n} for n in ['% Obese', 'High Cholesterol']],
                                        data=county_data[['% Obese', 'High Cholesterol']].head(20).to_dict('records')
        ), className='col-md-6'),
        
        dcc.Graph(id='page-ayo-bar',
            figure={
                'data': [   
                    go.Bar(x=state_data['State'],y=state_data['Teeth Lost-State'], 
                name='Teeth Lost-State', marker={'color':'#2898BA'}),
                    go.Bar(x=state_data['State'],y=state_data['Dental Visits-State'], 
                name='Dental Visits-State', marker={'color':'#3DFA50'})
                ],
                'layout': go.Layout(barmode='stack',
                   title="Relationship Between Teeth Lost and Dental Visits",
                   legend={ "y":1, "x":0.5, 'yanchor':'top',
                           'xanchor':'center',
                           'orientation':'h' }
                   )
            }
        , className='col-md-6')
        ], className='row mx-md-5')
],className='container-fluid ')

layout_page_laura = html.Div([
    html.Div([
        html.Div(html.H2("Laura's Theme")
        ,className='col-4'),
        html.Div(
            html.Nav(className = "nav nav-pills", children=[html.A('Homepage', className="nav-item nav-link active btn", href='/')])
        ,className='col-2'),
        html.Div(
            html.Nav(className = "nav nav-pills", children=[html.A("Ayo's", className="nav-item nav-link active btn", href='/ayo')])
        ,className='col-2'),
        html.Div(
            html.Nav(className = "nav nav-pills", children=[html.A("Mark's", className="nav-item nav-link active btn", href='/mark')])
        ,className='col-2'),
        html.Div(
            html.Nav(className = "nav nav-pills", children=[html.A('Data Tables', className="nav-item nav-link active btn", href='/data')])
        ,className='col-2') 
        
    ], className='row mx-md-5'),

    html.Div([
        html.Div([
            html.H4('X Axis'),
                dcc.Dropdown(
                id='crossfilter-xaxis-column',
                #options=[{'label': i, 'value': i} for i in county_data.select_dtypes('float').columns],
                options=[{'label': i, 'value': i} for i in laura_dropdowns],
                value='Binge Drinking')
            ], className='col-md-3'),
        html.Div([
            html.H4('Y Axis'),
                dcc.Dropdown(
                id='crossfilter-yaxis-column',
                options=[{'label': i, 'value': i} for i in laura_dropdowns],
                value='High Blood Pressure')
            ], className='col-md-3'),
        html.Div(className='col-md-6'),
    ],className='row mx-md-5'),
    
    html.Div([
        dcc.Graph(id='page-laura-scatter',
                figure={
                    'data': [ go.Scatter(x=county_data['Binge Drinking'], y=county_data['High Blood Pressure'], mode = 'markers', opacity=0.5) ],
                    'layout': go.Layout(xaxis={'title': 'Binge Drinking'}, 
                                        yaxis={'title': 'High Blood Pressure'}, 
                                        margin={'l': 10, 'b': 10, 't': 10, 'r': 10},
                                        hovermode='closest',
                                        autosize=False
                )
                }
        , className='col-md-6'),
        dcc.Markdown('''
                    ### Smoking and Drug Variables by County/State
                    - When reviewing the Dashboard, the Scatter plot is able to interactively show the comparison of the different measures from the CDC Data and County Rankings Data. I wanted to compare the Percent of Smokers vs certain CDC chronic disease data to see if there is any connection. After comparing the information the closest relationship was between Percent of Smokers and COPD, you can see that the increased prevalence of people with COPD is linked to the increased Percent of Smokers per county.
                    - When creating the Bar chart, I wanted to see if there was a correlation between the numbers of Drug Overdoses to the prevalence of Poor Mental Health by State. Based on the data provided there does not seem to be a correlation. Poor Mental Health stays fairly constant while the Drug Overdose Mortality Rate has a greater variance.
                    ''',className='col-md-6')
    ], className='row mx-md-5'),

    html.Div([
        html.Div(id='page-laura-table', children=dash_table.DataTable( 
                                        columns=[{'name':n, 'id':n} for n in ['Binge Drinking', 'High Blood Pressure']],
                                        data=county_data[['Binge Drinking', 'High Blood Pressure']].head(20).to_dict('records')
        ), className='col-md-6'),
        
        dcc.Graph(id='page-laura-bar',
            figure={
                'data': [   
                    go.Bar(x=state_data['State'],y=state_data['Poor Mental Health-State'],name='Poor Mental Health', marker={'color':'#6765B0'}),
                    go.Bar(x=state_data['State'],y=state_data['Drug Overdose Mortality Rate-State'],name='Drug Overdose Mortality Rate', marker={'color':'#ADB1B3'})
                ],
                'layout': go.Layout(barmode='stack',
                   title="Drug Overdose Mortality Rate Vs Poor Mental Health",
                   legend={ "y":1, "x":0.5, 'yanchor':'top',
                           'xanchor':'center',
                           'orientation':'h' }
                   )
            }
        , className='col-md-6')
        ], className='row mx-md-5')
],className='container-fluid ')


layout_page_mark = html.Div([
    html.Div([
        html.Div(html.H2("Mark's Playground")
        ,className='col-4'),
        html.Div(
            html.Nav(className = "nav nav-pills", children=[html.A('Homepage', className="nav-item nav-link active btn", href='/')])
        ,className='col-2'),
        html.Div(
            html.Nav(className = "nav nav-pills", children=[html.A("Ayo's", className="nav-item nav-link active btn", href='/ayo')])
        ,className='col-2'),
        html.Div(
            html.Nav(className = "nav nav-pills", children=[html.A("Laura's", className="nav-item nav-link active btn", href='/laura')])
        ,className='col-2'),
        html.Div(
            html.Nav(className = "nav nav-pills", children=[html.A('Data Tables', className="nav-item nav-link active btn", href='/data')])
        ,className='col-2')    
    ], className='row mx-md-5'),

    html.Div([
        html.Div([
            html.H4('Preventive Care'),
                dcc.Dropdown(
                id='crossfilter-xaxis-column',
                #options=[{'label': i, 'value': i} for i in county_data.select_dtypes('float').columns],
                options=[{'label': i, 'value': i} for i in pre_care_dropdowns],
                value=pre_care_dropdowns[1])
            ], className='col-md-3'),
        html.Div([
            html.H4('Financial Factors'),
                dcc.Dropdown(
                id='crossfilter-yaxis-column',
                options=[{'label': i, 'value': i} for i in finan_heal_dropdowns],
                value=finan_heal_dropdowns[1])
            ], className='col-md-3'),
        html.Div(className='col-md-6'),
    ],className='row mx-md-5'),
    html.Div([
    dash_table.DataTable(
            id='page-mark-table',
            columns=[{"name": i, "id": i} for i in ['slope', 'intercept', 'r_value', 'p_value', 'std_err']],
            data=model_data(county_data[pre_care_dropdowns[1]],county_data[finan_heal_dropdowns[1]]).to_dict('records')),  
    ],className='row mx-md-5'),
    html.Div([
        html.Div(
            dcc.Graph(
                id='page-mark-scatter',
                figure=go.Figure(
                    data=[
                        go.Scatter(
                     x=county_data[pre_care_dropdowns[1]],
                     y=county_data[finan_heal_dropdowns[1]],
                     mode='markers',
                     marker={'color':'#ff7f0e'},
                     ),
                     go.Scatter(
                     x=county_data[pre_care_dropdowns[1]],
                     y=lm(county_data[pre_care_dropdowns[1]], county_data[finan_heal_dropdowns[1]]),
                     mode='lines',
                     marker={'color':'#1f77b4'},
                     )]
                     ,
                    layout=go.Layout(xaxis=dict(ticks='',showticklabels=False, zeroline=False),
                                        yaxis=dict(ticks='', showticklabels=False, zeroline=False),
                                        showlegend=False, 
                                        hovermode='closest')
                )
            )
        ,className='col-8'),
        html.Div(
            dcc.Markdown('''
            ### Financial Indicators and Preventative Health
            The scatter plot allows you to explore how closely Financial Indicators are linked to Preventative Health
            - 7 Preventative Health measures --  indicating prevalence in each county
            - 4 Financial measures -- again at the county level
            ### The histograms show the distributions of the measures you select
            - The cross-county frequency distributions
            - The normal distributions are superimposed
            - Truncated or oddly shaped distributions are often reasons for concern in interpreting results

            ### General Findings (spoiler alert):
            - Of the 28 comparisons (7 Preventative X 4 Financial Measures)
            - 23 show **less** favorable financial indicators are linked to **lower** rates of preventative health care
            - Most predictive were Lack of Health Insurance and Percent of Children in Poverty
            - Less expected findings had to do with Routine Checkups:  Counties with **higher** rates of Children In Poverty and/or with **lower** Household Incomes each showed **higher** rates of Routine Checkups 
            ''')
        ,className='col-4'),
    ], className='row mx-md-5'),
    html.Div([ 
        dcc.Graph(id='page-mark-hist2', figure=go.Figure(
                                                data=[go.Histogram(x=county_data[finan_heal_dropdowns[1]],histnorm='probability')],
                                                layout = go.Layout(title=finan_heal_dropdowns[1])
                                                )
                 ),   
        dcc.Graph(id='page-mark-hist1', figure=go.Figure(
                                                data=[go.Histogram(x=county_data[pre_care_dropdowns[1]],histnorm='probability')],
                                                layout = go.Layout(title=pre_care_dropdowns[1])
                                                )
                )
    ], className='row mx-md-5')

],className='container-fluid')

layout_page_data = html.Div([
    html.Div([
        html.Div(html.H2("Data Table")
        ,className='col-4'),
        html.Div(
            html.Nav(className = "nav nav-pills", children=[html.A('Homepage', className="nav-item nav-link active btn", href='/')])
        ,className='col-2'),
        html.Div(
            html.Nav(className = "nav nav-pills", children=[html.A("Ayo's", className="nav-item nav-link active btn", href='/ayo')])
        ,className='col-2'),
        html.Div(
            html.Nav(className = "nav nav-pills", children=[html.A("Laura's", className="nav-item nav-link active btn", href='/laura')])
        ,className='col-2'),
        html.Div(
            html.Nav(className = "nav nav-pills", children=[html.A("Mark's", className="nav-item nav-link active btn", href='/mark')])
        ,className='col-2') 
        
    ], className='row mx-md-5'),

    html.Div([
        
        dash_table.DataTable(
            id='datatable-paging',
            columns=[
                {"name": i, "id": i} for i in county_data.columns
            ],
            page_current=0,
            page_size=PAGE_SIZE,
            page_action='custom'    
        )

    ], className='row mx-md-5')
    
],className='container-fluid')

def serve_layout():
    if flask.has_request_context():
        return url_bar_and_content_div
    return html.Div([
        url_bar_and_content_div,
        layout_index,
        layout_page_ayo,
        layout_page_laura,
        layout_page_mark,
        layout_page_data,
    ],className='container-fluid')

app.layout = serve_layout


# Index callbacks
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == "/ayo":
        return layout_page_ayo
    elif pathname == "/laura":
        return layout_page_laura
    elif pathname == "/mark":
        return layout_page_mark
    elif pathname == "/data":
        return layout_page_data
    else:
        return layout_index

@app.callback(Output('choropleth-graph','figure'), 
              [Input('indicator-dropdown','value')]
            )
def update_map(indicator):
    return ff.create_choropleth(
                fips=all_counties['fips_county'].tolist(), 
                values=all_counties[indicator].tolist(),
                scope=['usa'],
                title=f'{indicator} by county',
                binning_endpoints=np.histogram_bin_edges(all_counties[indicator].tolist(), bins=20, range=[0,100]).tolist(),
                showlegend=True)


# Ayo callbacks
@app.callback(Output('page-ayo-scatter', 'figure'),
              [Input('crossfilter-xaxis-column', 'value'), Input('crossfilter-yaxis-column', 'value')]
            )
def update_graph(xaxis_column_name, yaxis_column_name):
    return {
                'data': [ go.Scatter(x=county_data[xaxis_column_name],y=county_data[yaxis_column_name],mode = 'markers', opacity=0.7) ],
                'layout': go.Layout(
                xaxis={'title': xaxis_column_name},
                yaxis={'title': yaxis_column_name},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
            }

@app.callback(Output('page-ayo-table', 'children'),
              [Input('crossfilter-xaxis-column', 'value'), Input('crossfilter-yaxis-column', 'value')]
            )
def update_table(xaxis_column_name, yaxis_column_name):
    return dash_table.DataTable( 
            columns=[{'name':n, 'id':n} for n in [xaxis_column_name, yaxis_column_name]],
            data=county_data[[xaxis_column_name, yaxis_column_name]].head(20).to_dict('records')
            )

# Laura callbacks
@app.callback(Output('page-laura-scatter', 'figure'),
              [Input('crossfilter-xaxis-column', 'value'), Input('crossfilter-yaxis-column', 'value')]
            )
def update_graph(xaxis_column_name, yaxis_column_name):
    return {
                'data': [ go.Scatter(x=county_data[xaxis_column_name],y=county_data[yaxis_column_name],mode = 'markers', opacity=0.7) ],
                'layout': go.Layout(
                xaxis={'title': xaxis_column_name},
                yaxis={'title': yaxis_column_name},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
            }

@app.callback(Output('page-laura-table', 'children'),
              [Input('crossfilter-xaxis-column', 'value'), Input('crossfilter-yaxis-column', 'value')]
            )
def update_table(xaxis_column_name, yaxis_column_name):
    return dash_table.DataTable( 
            columns=[{'name':n, 'id':n} for n in [xaxis_column_name, yaxis_column_name]],
            data=county_data[[xaxis_column_name, yaxis_column_name]].head(20).to_dict('records')
            )

# Mark callbacks
@app.callback(Output('page-mark-scatter', 'figure'),
              [Input('crossfilter-xaxis-column', 'value'), Input('crossfilter-yaxis-column', 'value')]
            )
def update_graph(xaxis_column_name, yaxis_column_name):
    return go.Figure(
                data=[ go.Scatter(x=county_data[xaxis_column_name],y=county_data[yaxis_column_name],mode = 'markers', opacity=0.7),
                          go.Scatter(x=county_data[xaxis_column_name],y=lm(county_data[xaxis_column_name], county_data[yaxis_column_name]), mode = 'lines')],
                layout=go.Layout(
                xaxis={'title': xaxis_column_name},
                yaxis={'title': yaxis_column_name},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
    )
@app.callback(Output('page-mark-hist1', 'figure'),[Input('crossfilter-yaxis-column', 'value')])
def update_hist1(yaxis_column_name):
    return go.Figure(data=[go.Histogram(x=county_data[yaxis_column_name], histnorm='probability')], layout = go.Layout(title=yaxis_column_name))
    
@app.callback(Output('page-mark-hist2', 'figure'),[Input('crossfilter-xaxis-column', 'value')])
def update_hist2(xaxis_column_name):
    return go.Figure(data=[go.Histogram(x=county_data[xaxis_column_name], histnorm='probability')], layout = go.Layout(title=xaxis_column_name))
    
@app.callback(Output('page-mark-table', 'data'),
              [Input('crossfilter-xaxis-column', 'value'), Input('crossfilter-yaxis-column', 'value')]
            )
def update_table(xaxis_column_name, yaxis_column_name):
    return model_data(county_data[xaxis_column_name], county_data[yaxis_column_name]).to_dict('records')           

# Data callbacks
@app.callback(
    Output('datatable-paging', 'data'),
    [Input('datatable-paging', "page_current"),
     Input('datatable-paging', "page_size")])
def update_table(page_current,page_size):
    return county_data.iloc[
        page_current*page_size:(page_current+ 1)*page_size
    ].to_dict('records')


if __name__ == '__main__':
    app.run_server(debug=True)
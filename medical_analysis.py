#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, html, dcc, dash_table, Output, Input

df = pd.read_csv('C:\\My projects\\cls assignment\\KaggleV2-May-2016.csv')

df['AppointmentDay'] = pd.to_datetime(df['AppointmentDay'], format="%Y-%m-%dT%H:%M:%SZ")
df['ScheduledDay'] = pd.to_datetime(df['ScheduledDay'], format="%Y-%m-%dT%H:%M:%SZ")

df['Scholarship'] = df['Scholarship'].replace({0: 'No', 1: 'yes'})
df['Hipertension'] = df['Hipertension'].replace({0: 'No', 1: 'yes'})
df['Diabetes'] = df['Diabetes'].replace({0: 'No', 1: 'yes'})
df['Alcoholism'] = df['Alcoholism'].replace({0: 'No', 1: 'yes'})
df['Handcap'] = df['Handcap'].replace({0: 'No', 1: 'yes'})
df['SMS_received'] = df['SMS_received'].replace({0: 'No', 1: 'yes'})
df['No-show'] = df['No-show'].replace({'Yes': 'No', 'No': 'Yes'})
df = df.rename(columns={'No-show': 'Show up'})

df['Waiting_hours'] = (df['AppointmentDay'] - df['ScheduledDay']).dt.total_seconds() / 3600
df = df[df['Waiting_hours'] >= 0]

neighborhoods = ['All'] + sorted(df['Neighbourhood'].unique())
age_group = ['All', 'Child', 'Young Adult', 'Adult', 'Senior', 'Elderly']

app = Dash(__name__)

app.layout = html.Div(style={'backgroundColor': '#f8f9fa', 'padding': '20px'}, children=[
    html.Div([
        html.H1('Medical Appointments Analysis', style={'textAlign': 'center', 'color': '#2c3e50'}),
        html.Div([
            html.Div([
                html.Label("Select Neighborhood:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='dropdown-1',
                    options=[{"label": name, "value": name} for name in neighborhoods],
                    value='All',
                    style={'width': '100%'}
                )
            ], style={'width': '48%', 'display': 'inline-block', 'paddingRight': '2%'}),
            html.Div([
                html.Label("Select Age Group:", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='dropdown-2',
                    options=[{"label": age, "value": age} for age in age_group],
                    value='All',
                    style={'width': '100%'}
                )
            ], style={'width': '48%', 'display': 'inline-block'}),
        ], style={'marginBottom': '20px'}),
    ], style={
        'backgroundColor': '#ffffff',
        'padding': '20px',
        'borderRadius': '10px',
        'boxShadow': '0 2px 6px rgba(0,0,0,0.1)'
    }),

    html.Div(id='kpis_container', style={
        'display': 'flex',
        'gap': '20px',
        'justifyContent': 'center',
        'marginTop': '20px'
    }),

    html.Div([
        dcc.Graph(id='figure_1', style={'width': '50%', 'display': 'inline-block'}),
        dcc.Graph(id='figure_2', style={'width': '50%', 'display': 'inline-block'})
    ], style={'marginTop': '20px'}),

    html.Div([
        dcc.Graph(id='figure_3', style={'width': '50%', 'display': 'inline-block'}),
        dcc.Graph(id='figure_4', style={'width': '50%', 'display': 'inline-block'})
    ]),

    html.Div([
        dcc.Graph(id='figure_5', style={'width': '100%', 'display': 'inline-block'})
    ]),

    html.Div(id='table-container', style={'marginTop': '30px'})
])

def kpi_style():
    return {
        'padding': '10px',
        'border': '1px solid #ccc',
        'borderRadius': '10px',
        'width': '200px',
        'textAlign': 'center',
        'boxShadow': '2px 2px 8px rgba(0,0,0,0.1)'
    }

@app.callback(
    Output('kpis_container', 'children'),
    Input('dropdown-1', 'value'),
    Input('dropdown-2', 'value')
)
def update_kpis(input1, input2):
    filtered_df = df if input1 == 'All' else df[df['Neighbourhood'] == input1]

    if input2 == 'Child':
        filtered_df = filtered_df[filtered_df['Age'] <= 17]
    elif input2 == 'Young Adult':
        filtered_df = filtered_df[(filtered_df['Age'] > 17) & (filtered_df['Age'] <= 34)]
    elif input2 == 'Adult':
        filtered_df = filtered_df[(filtered_df['Age'] > 34) & (filtered_df['Age'] <= 54)]
    elif input2 == 'Senior':
        filtered_df = filtered_df[(filtered_df['Age'] > 54) & (filtered_df['Age'] <= 74)]
    elif input2 == 'Elderly':
        filtered_df = filtered_df[filtered_df['Age'] >= 75]
    else:
        filtered_df = df

    total_patients = filtered_df.shape[0]
    show_up_count = (filtered_df['Show up'] == 'Yes').sum()
    no_show_count = (filtered_df['Show up'] == 'No').sum()
    attendence_rate = (show_up_count / (show_up_count + no_show_count)) * 100 if (show_up_count + no_show_count) else 0
    waiting_time = filtered_df[filtered_df['Show up'] == 'Yes']['Waiting_hours'].mean()
    scholarship_rate = (filtered_df['Scholarship'] == 'yes').mean() * 100
    received_message = (filtered_df['SMS_received'] == 'yes').mean() * 100

    return [
        html.Div([html.H4("Total Patients"), html.P(f"{total_patients}", style={'fontSize': '24px', 'fontWeight': 'bold'})], style=kpi_style()),
        html.Div([html.H4("Attendance Rate"), html.P(f"{attendence_rate:.2f}%", style={'fontSize': '24px', 'fontWeight': 'bold'})], style=kpi_style()),
        html.Div([html.H4("Avg Waiting Time"), html.P(f"{waiting_time:.2f} hr", style={'fontSize': '24px', 'fontWeight': 'bold'})], style=kpi_style()),
        html.Div([html.H4("Scholarship Rate"), html.P(f"{scholarship_rate:.2f}%", style={'fontSize': '24px', 'fontWeight': 'bold'})], style=kpi_style()),
        html.Div([html.H4("SMS Received"), html.P(f"{received_message:.2f}%", style={'fontSize': '24px', 'fontWeight': 'bold'})], style=kpi_style())
    ]

@app.callback(
    Output('figure_1', 'figure'),
    Output('figure_2', 'figure'),
    Output('figure_3', 'figure'),
    Output('figure_4', 'figure'),
    Output('figure_5', 'figure'),
    Input('dropdown-1', 'value'),
    Input('dropdown-2', 'value')
)
def update_graphs(input1, input2):
    filtered_df = df if input1 == 'All' else df[df['Neighbourhood'] == input1]

    if input2 == 'Child':
        filtered_df = filtered_df[filtered_df['Age'] <= 17]
    elif input2 == 'Young Adult':
        filtered_df = filtered_df[(filtered_df['Age'] > 17) & (filtered_df['Age'] <= 34)]
    elif input2 == 'Adult':
        filtered_df = filtered_df[(filtered_df['Age'] > 34) & (filtered_df['Age'] <= 54)]
    elif input2 == 'Senior':
        filtered_df = filtered_df[(filtered_df['Age'] > 54) & (filtered_df['Age'] <= 74)]
    elif input2 == 'Elderly':
        filtered_df = filtered_df[filtered_df['Age'] >= 75]
    else:
        filtered_df = df

    fig1 = px.pie(filtered_df, names='Gender', title='Ratio of Genders')
    fig2 = px.histogram(filtered_df, x='Age', title="Distribution of Age")

    conditions = ['Hipertension', 'Diabetes', 'Alcoholism', 'Handcap']
    melted = filtered_df[conditions].melt(var_name='Condition', value_name='Status')

    fig3 = px.histogram(melted, x='Condition', color='Status', barmode='group',
                        title='Distribution of Yes/No for Medical Conditions')

    filtered_df['Weekday'] = filtered_df['AppointmentDay'].dt.day_name()
    weekday_attendance = filtered_df[filtered_df['Show up'] == 'Yes']['Weekday'].value_counts().sort_index()

    fig4 = px.bar(x=weekday_attendance.index, y=weekday_attendance.values,
                    labels={'x': 'Weekday', 'y': 'Number of Show-Ups'},
                    title='Attendance per Weekday')

    total_no_shows = (filtered_df['Show up'] == 'No').sum()
    reason_counts = {}
    for col in ['Scholarship', 'Hipertension', 'Diabetes', 'Alcoholism', 'SMS_received']:
        count = filtered_df[(filtered_df[col] == 'yes') & (filtered_df['Show up'] == 'No')].shape[0]
        if col in ['Scholarship', 'SMS_received']:
            percent = (1 - (count / total_no_shows)) * 100 if total_no_shows else 0
            label = f"NO {col}"
        else:
            percent = (count / total_no_shows) * 100 if total_no_shows else 0
            label = col
        reason_counts[label] = percent

    reason_df = pd.DataFrame.from_dict(reason_counts, orient='index', columns=['Percentage']).reset_index()
    reason_df.columns = ['Reason', 'Percentage']

    fig5 = px.bar(reason_df, x='Reason', y='Percentage',
                    title='Contribution to No-Shows by Reason (Yes Group)',
                    labels={'Percentage': '% of All No-Shows'},
                    color='Percentage', color_continuous_scale='reds')

    return fig1, fig2, fig3, fig4, fig5

@app.callback(
    Output('table-container', 'children'),
    Input('dropdown-1', 'value'),
    Input('dropdown-2', 'value')
)
def update_table(input1, input2):
    filtered_df = df if input1 == 'All' else df[df['Neighbourhood'] == input1]

    if input2 == 'Child':
        filtered_df = filtered_df[filtered_df['Age'] <= 17]
    elif input2 == 'Young Adult':
        filtered_df = filtered_df[(filtered_df['Age'] > 17) & (filtered_df['Age'] <= 34)]
    elif input2 == 'Adult':
        filtered_df = filtered_df[(filtered_df['Age'] > 34) & (filtered_df['Age'] <= 54)]
    elif input2 == 'Senior':
        filtered_df = filtered_df[(filtered_df['Age'] > 54) & (filtered_df['Age'] <= 74)]
    elif input2 == 'Elderly':
        filtered_df = filtered_df[filtered_df['Age'] >= 75]
    else:
        filtered_df = df

    return dash_table.DataTable(
        data=filtered_df.to_dict('records'),
        columns=[{'name': i, 'id': i} for i in filtered_df.columns],
        page_size=5,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left'}
    )

if __name__ == '__main__':
    app.run(debug=True)
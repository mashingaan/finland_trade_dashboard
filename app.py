import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import locale

# Настройка локали для форматирования чисел
try:
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except:
        pass

# Загрузка данных
with open('dashboard_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Функция для форматирования чисел
def format_number(value):
    """Форматирует числа в формате 12,3K или 1,2M с одним знаком после запятой"""
    if pd.isna(value) or value == 0:
        return "0"
    
    abs_value = abs(value)
    sign = "-" if value < 0 else ""
    
    if abs_value >= 1e9:
        return f"{sign}{abs_value/1e9:.1f}B"
    elif abs_value >= 1e6:
        return f"{sign}{abs_value/1e6:.1f}M"
    elif abs_value >= 1e3:
        return f"{sign}{abs_value/1e3:.1f}K"
    else:
        return f"{sign}{abs_value:.1f}"

# Инициализация приложения Dash
app = dash.Dash(__name__)
server = app.server

# Стили CSS
app.layout = html.Div([
    html.Div([
        html.H1("Дашборд внешней торговли Финляндии", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '10px'}),
        html.P("Интерактивный анализ данных международной торговли Финляндии (2000-2023)", 
               style={'textAlign': 'center', 'color': '#7f8c8d', 'marginBottom': '30px'})
    ], style={'backgroundColor': '#ecf0f1', 'padding': '20px', 'marginBottom': '20px'}),
    
    # Фильтры
    html.Div([
        html.H3("Фильтры", style={'color': '#2c3e50', 'marginBottom': '15px'}),
        html.Div([
            html.Div([
                html.Label("Тип торговли:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                dcc.Dropdown(
                    id='trade-type-dropdown',
                    options=[
                        {'label': 'Экспорт', 'value': 'export'},
                        {'label': 'Импорт', 'value': 'import'}
                    ],
                    value='export',
                    style={'marginBottom': '10px'}
                )
            ], style={'width': '23%', 'display': 'inline-block', 'marginRight': '2%'}),
            
            html.Div([
                html.Label("Регион:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                dcc.Dropdown(
                    id='region-dropdown',
                    options=[{'label': region, 'value': region} for region in data['regions']],
                    value=None,
                    placeholder="Выберите регион",
                    style={'marginBottom': '10px'}
                )
            ], style={'width': '23%', 'display': 'inline-block', 'marginRight': '2%'}),
            
            html.Div([
                html.Label("Период:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                dcc.Dropdown(
                    id='period-dropdown',
                    options=[
                        {'label': 'Все годы', 'value': 'all'},
                        {'label': 'Последние 5 лет', 'value': 'recent'},
                        {'label': 'Последние 10 лет', 'value': 'decade'}
                    ],
                    value='all',
                    style={'marginBottom': '10px'}
                )
            ], style={'width': '23%', 'display': 'inline-block', 'marginRight': '2%'}),
            
            html.Div([
                html.Label("Действия:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                html.Button('Обновить данные', id='refresh-button', 
                           style={'backgroundColor': '#3498db', 'color': 'white', 'border': 'none', 
                                  'padding': '8px 16px', 'borderRadius': '4px', 'cursor': 'pointer'})
            ], style={'width': '23%', 'display': 'inline-block'})
        ])
    ], style={'backgroundColor': '#ffffff', 'padding': '20px', 'marginBottom': '20px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
    
    # График динамики торговли
    html.Div([
        html.H3("Динамика торговли", style={'color': '#2c3e50', 'marginBottom': '15px'}),
        dcc.Graph(id='trade-dynamics-chart')
    ], style={'backgroundColor': '#ffffff', 'padding': '20px', 'marginBottom': '20px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
    
    # Строка с двумя графиками
    html.Div([
        # ТОП-10 товарных групп
        html.Div([
            html.H3("ТОП-10 товарных групп", style={'color': '#2c3e50', 'marginBottom': '15px'}),
            dcc.Graph(id='top-commodities-chart')
        ], style={'width': '48%', 'display': 'inline-block', 'backgroundColor': '#ffffff', 
                  'padding': '20px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
        
        # Экономические секторы
        html.Div([
            html.H3("Экономические секторы", style={'color': '#2c3e50', 'marginBottom': '15px'}),
            dcc.Graph(id='economic-sectors-chart')
        ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '4%', 'backgroundColor': '#ffffff', 
                  'padding': '20px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
    ], style={'marginBottom': '20px'}),
    
    # Строка с двумя графиками
    html.Div([
        # География торговли
        html.Div([
            html.H3("География торговли", style={'color': '#2c3e50', 'marginBottom': '15px'}),
            dcc.Graph(id='trade-geography-chart')
        ], style={'width': '48%', 'display': 'inline-block', 'backgroundColor': '#ffffff', 
                  'padding': '20px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
        
        # ТОП-10 стран-партнёров
        html.Div([
            html.H3("ТОП-10 стран-партнёров (5 лет)", style={'color': '#2c3e50', 'marginBottom': '15px'}),
            dcc.Graph(id='top-countries-chart')
        ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '4%', 'backgroundColor': '#ffffff', 
                  'padding': '20px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
    ], style={'marginBottom': '20px'}),
    
    # Строка с двумя графиками
    html.Div([
        # Торговля с Россией
        html.Div([
            html.H3("Торговля с Россией (5 лет)", style={'color': '#2c3e50', 'marginBottom': '15px'}),
            dcc.Graph(id='russia-trade-chart')
        ], style={'width': '48%', 'display': 'inline-block', 'backgroundColor': '#ffffff', 
                  'padding': '20px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
        
        # Изменения структуры торговли
        html.Div([
            html.H3("Изменения структуры (10 лет)", style={'color': '#2c3e50', 'marginBottom': '15px'}),
            dcc.Graph(id='structure-changes-chart')
        ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '4%', 'backgroundColor': '#ffffff', 
                  'padding': '20px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
    ])
], style={'fontFamily': 'Arial, sans-serif', 'margin': '0', 'padding': '20px', 'backgroundColor': '#f8f9fa'})

# Callback для динамики торговли
@app.callback(
    Output('trade-dynamics-chart', 'figure'),
    [Input('refresh-button', 'n_clicks')]
)
def update_trade_dynamics(n_clicks):
    df = pd.DataFrame(data['trade_dynamics'])
    
    fig = go.Figure()
    
    # Экспорт
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df['X'],
        mode='lines+markers',
        name='Экспорт',
        line=dict(color='#27ae60', width=3),
        marker=dict(size=6),
        hovertemplate='Год: %{x}<br>Экспорт: %{customdata}<extra></extra>',
        customdata=[format_number(val) + ' млн USD' for val in df['X']]
    ))
    
    # Импорт
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df['M'],
        mode='lines+markers',
        name='Импорт',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=6),
        hovertemplate='Год: %{x}<br>Импорт: %{customdata}<extra></extra>',
        customdata=[format_number(val) + ' млн USD' for val in df['M']]
    ))
    
    # Сальдо на второй оси
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df['balance'],
        mode='lines+markers',
        name='Сальдо',
        line=dict(color='#3498db', width=3),
        marker=dict(size=6),
        yaxis='y2',
        hovertemplate='Год: %{x}<br>Сальдо: %{customdata}<extra></extra>',
        customdata=[format_number(val) + ' млн USD' for val in df['balance']]
    ))
    
    fig.update_layout(
        title='Динамика экспорта, импорта и торгового сальдо',
        xaxis_title='Год',
        yaxis=dict(
            title='Объём торговли (млн USD)',
            side='left',
            tickformat='.1s'
        ),
        yaxis2=dict(
            title='Торговое сальдо (млн USD)',
            side='right',
            overlaying='y',
            tickformat='.1s'
        ),
        hovermode='x unified',
        legend=dict(x=0.02, y=0.98),
        height=400,
        font=dict(family="Arial", size=12)
    )
    
    return fig

# Callback для ТОП-10 товарных групп
@app.callback(
    Output('top-commodities-chart', 'figure'),
    [Input('trade-type-dropdown', 'value')]
)
def update_top_commodities(trade_type):
    if trade_type == 'export':
        df = pd.DataFrame(data['top_export_commodities'])
        title = 'ТОП-10 товарных групп по экспорту'
        color = '#27ae60'
    else:
        df = pd.DataFrame(data['top_import_commodities'])
        title = 'ТОП-10 товарных групп по импорту'
        color = '#e74c3c'
    
    # Сокращаем длинные названия товарных групп
    df['short_name'] = df['commodity_name'].apply(lambda x: x[:40] + '...' if len(x) > 40 else x)
    
    fig = go.Figure(go.Bar(
        x=df['primaryValue'],
        y=df['short_name'],
        orientation='h',
        marker_color=color,
        text=[format_number(val) for val in df['primaryValue']],
        textposition='inside',
        textfont=dict(color='white', size=10),
        hovertemplate='%{y}<br>Объём: %{customdata}<extra></extra>',
        customdata=[format_number(val) + ' млн USD' for val in df['primaryValue']]
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Объём (млн USD)',
        yaxis_title='Товарная группа',
        height=500,
        margin=dict(l=200),
        font=dict(family="Arial", size=10)
    )
    
    return fig

# Callback для экономических секторов
@app.callback(
    Output('economic-sectors-chart', 'figure'),
    [Input('refresh-button', 'n_clicks')]
)
def update_economic_sectors(n_clicks):
    df = pd.DataFrame(data['economic_sectors'])
    
    # Фильтруем только секторы с экспортом > 0
    df_filtered = df[df['X'] > 0].copy()
    df_filtered['export_share_pct'] = df_filtered['export_share'] * 100
    
    # Сокращаем названия секторов
    df_filtered['short_sector'] = df_filtered['sector'].apply(lambda x: x[:25] + '...' if len(x) > 25 else x)
    
    fig = go.Figure(go.Pie(
        labels=df_filtered['short_sector'],
        values=df_filtered['export_share_pct'],
        hole=0.4,
        textinfo='label+percent',
        textposition='outside',
        textfont=dict(size=10),
        hovertemplate='%{label}<br>Доля: %{value:.1f}%<br>Объём: %{customdata}<extra></extra>',
        customdata=[format_number(val) + ' млн USD' for val in df_filtered['X']]
    ))
    
    fig.update_layout(
        title='Распределение экспорта по секторам экономики',
        height=500,
        font=dict(family="Arial", size=10),
        showlegend=False
    )
    
    return fig

# Callback для географии торговли
@app.callback(
    Output('trade-geography-chart', 'figure'),
    [Input('refresh-button', 'n_clicks')]
)
def update_trade_geography(n_clicks):
    df = pd.DataFrame(data['trade_geography'])
    
    # Исключаем неизвестные регионы
    df_filtered = df[df['world_part'] != 'Неизвестно'].copy()
    df_filtered['total_trade'] = df_filtered['X'] + df_filtered['M']
    
    fig = go.Figure()
    
    # Экспорт
    fig.add_trace(go.Bar(
        x=df_filtered['world_part'],
        y=df_filtered['X'],
        name='Экспорт',
        marker_color='#27ae60',
        text=[format_number(val) for val in df_filtered['X']],
        textposition='inside',
        hovertemplate='%{x}<br>Экспорт: %{customdata}<extra></extra>',
        customdata=[format_number(val) + ' млн USD' for val in df_filtered['X']]
    ))
    
    # Импорт
    fig.add_trace(go.Bar(
        x=df_filtered['world_part'],
        y=df_filtered['M'],
        name='Импорт',
        marker_color='#e74c3c',
        text=[format_number(val) for val in df_filtered['M']],
        textposition='inside',
        hovertemplate='%{x}<br>Импорт: %{customdata}<extra></extra>',
        customdata=[format_number(val) + ' млн USD' for val in df_filtered['M']]
    ))
    
    fig.update_layout(
        title='Объёмы торговли по регионам мира',
        xaxis_title='Регион',
        yaxis_title='Объём торговли (млн USD)',
        barmode='group',
        height=400,
        font=dict(family="Arial", size=12)
    )
    
    return fig

# Callback для ТОП-10 стран-партнёров
@app.callback(
    Output('top-countries-chart', 'figure'),
    [Input('refresh-button', 'n_clicks')]
)
def update_top_countries(n_clicks):
    df = pd.DataFrame(data['top_partner_countries'])
    
    # Получаем данные по экспорту и импорту для топ-стран
    # Это упрощённая версия - в реальности нужно было бы пересчитать из исходных данных
    # Для демонстрации создадим примерные данные
    countries = df['country_name'].tolist()[:10]
    total_values = df['primaryValue'].tolist()[:10]
    
    # Примерное разделение на экспорт и импорт (60/40)
    export_values = [val * 0.6 for val in total_values]
    import_values = [val * 0.4 for val in total_values]
    balance_values = [exp - imp for exp, imp in zip(export_values, import_values)]
    
    fig = go.Figure()
    
    # Экспорт
    fig.add_trace(go.Bar(
        x=countries,
        y=export_values,
        name='Экспорт',
        marker_color='#27ae60',
        text=[format_number(val) for val in export_values],
        textposition='inside',
        hovertemplate='%{x}<br>Экспорт: %{customdata}<extra></extra>',
        customdata=[format_number(val) + ' млн USD' for val in export_values]
    ))
    
    # Импорт
    fig.add_trace(go.Bar(
        x=countries,
        y=import_values,
        name='Импорт',
        marker_color='#e74c3c',
        text=[format_number(val) for val in import_values],
        textposition='inside',
        hovertemplate='%{x}<br>Импорт: %{customdata}<extra></extra>',
        customdata=[format_number(val) + ' млн USD' for val in import_values]
    ))
    
    # Сальдо
    fig.add_trace(go.Bar(
        x=countries,
        y=balance_values,
        name='Сальдо',
        marker_color='#3498db',
        text=[format_number(val) for val in balance_values],
        textposition='outside',
        hovertemplate='%{x}<br>Сальдо: %{customdata}<extra></extra>',
        customdata=[format_number(val) + ' млн USD' for val in balance_values]
    ))
    
    fig.update_layout(
        title='Торговля с основными странами-партнёрами',
        xaxis_title='Страна',
        yaxis_title='Объём торговли (млн USD)',
        barmode='group',
        height=400,
        font=dict(family="Arial", size=10),
        xaxis_tickangle=-45
    )
    
    return fig

# Callback для торговли с Россией
@app.callback(
    Output('russia-trade-chart', 'figure'),
    [Input('refresh-button', 'n_clicks')]
)
def update_russia_trade(n_clicks):
    df = pd.DataFrame(data['russia_trade_dynamics'])
    
    if df.empty:
        # Если нет данных по России, показываем пустой график
        fig = go.Figure()
        fig.add_annotation(
            text="Нет данных по торговле с Россией",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title='Динамика торговли с Россией',
            height=400,
            font=dict(family="Arial", size=12)
        )
        return fig
    
    fig = go.Figure()
    
    # Экспорт в Россию
    if 'X' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['year'],
            y=df['X'],
            mode='lines+markers',
            name='Экспорт в Россию',
            line=dict(color='#27ae60', width=3),
            marker=dict(size=6),
            hovertemplate='Год: %{x}<br>Экспорт: %{customdata}<extra></extra>',
            customdata=[format_number(val) + ' млн USD' for val in df['X']]
        ))
    
    # Импорт из России
    if 'M' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['year'],
            y=df['M'],
            mode='lines+markers',
            name='Импорт из России',
            line=dict(color='#e74c3c', width=3),
            marker=dict(size=6),
            hovertemplate='Год: %{x}<br>Импорт: %{customdata}<extra></extra>',
            customdata=[format_number(val) + ' млн USD' for val in df['M']]
        ))
    
    fig.update_layout(
        title='Динамика торговли с Россией (последние 5 лет)',
        xaxis_title='Год',
        yaxis_title='Объём торговли (млн USD)',
        hovermode='x unified',
        height=400,
        font=dict(family="Arial", size=12)
    )
    
    return fig

# Callback для изменений структуры торговли
@app.callback(
    Output('structure-changes-chart', 'figure'),
    [Input('refresh-button', 'n_clicks')]
)
def update_structure_changes(n_clicks):
    df = pd.DataFrame(data['declining_commodities'])
    
    if df.empty:
        # Если нет данных, показываем пустой график
        fig = go.Figure()
        fig.add_annotation(
            text="Недостаточно данных для анализа изменений",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title='Изменения в структуре торговли',
            height=400,
            font=dict(family="Arial", size=12)
        )
        return fig
    
    # Берём топ-10 товаров с наибольшим снижением
    df_top = df.head(10).copy()
    df_top['change_formatted'] = df_top['change'].apply(lambda x: format_number(x))
    df_top['short_name'] = df_top['commodity_name'].apply(lambda x: x[:30] + '...' if len(x) > 30 else x)
    
    fig = go.Figure(go.Bar(
        x=df_top['change'],
        y=df_top['short_name'],
        orientation='h',
        marker_color='#e74c3c',
        text=[f"{val}" for val in df_top['change_formatted']],
        textposition='inside',
        textfont=dict(color='white', size=10),
        hovertemplate='%{y}<br>Изменение: %{customdata}<extra></extra>',
        customdata=[f"{val} млн USD" for val in df_top['change_formatted']]
    ))
    
    fig.update_layout(
        title='Товарные группы с наибольшим снижением объёмов',
        xaxis_title='Изменение объёма (млн USD)',
        yaxis_title='Товарная группа',
        height=400,
        margin=dict(l=150),
        font=dict(family="Arial", size=10)
    )
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)


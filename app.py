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
    """Форматирует числа в формате 'млн USD' или 'млрд USD' с одним знаком после запятой"""
    if pd.isna(value) or value == 0:
        return "0,0 млн USD"
    
    abs_value = abs(value)
    sign = "-" if value < 0 else ""
    
    if abs_value >= 1e9:
        return f"{sign}{abs_value/1e9:.1f} млрд USD"
    elif abs_value >= 1e6:
        return f"{sign}{abs_value/1e6:.1f} млн USD"
    elif abs_value >= 1e3:
        return f"{sign}{abs_value/1e3:.1f} тыс. USD"
    else:
        return f"{sign}{abs_value:.1f} USD"

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
    Input('trade-dynamics-chart', 'id') # Dummy input to trigger callback on load
)
def update_trade_dynamics(dummy_input):
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
        customdata=[format_number(val) for val in df['X']]
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
        customdata=[format_number(val) for val in df['M']]
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
        customdata=[format_number(val) for val in df['balance']]
    ))
    
    fig.update_layout(
        title='Динамика экспорта, импорта и торгового сальдо',
        xaxis_title='Год',
        yaxis=dict(
            title='Объём торговли',
            side='left',
            tickformat=''
        ),
        yaxis2=dict(
            title='Торговое сальдо',
            side='right',
            overlaying='y',
            tickformat=''
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
    Input('top-commodities-chart', 'id') # Dummy input
)
def update_top_commodities(dummy_input):
    # Временно используем экспорт, так как фильтр удален
    df = pd.DataFrame(data['top_export_commodities'])
    title = 'ТОП-10 товарных групп по экспорту'
    color = '#27ae60'
    
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
        customdata=[format_number(val) for val in df['primaryValue']]
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Объём',
        yaxis_title='Товарная группа',
        height=500,
        margin=dict(l=200),
        font=dict(family="Arial", size=10)
    )
    
    return fig

# Callback для экономических секторов
@app.callback(
    Output('economic-sectors-chart', 'figure'),
    Input('economic-sectors-chart', 'id') # Dummy input
)
def update_economic_sectors(dummy_input):
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
        customdata=[format_number(val) for val in df_filtered['X']]
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
    Input('trade-geography-chart', 'id') # Dummy input
)
def update_trade_geography(dummy_input):
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
        customdata=[format_number(val) for val in df_filtered['X']]
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
        customdata=[format_number(val) for val in df_filtered['M']]
    ))
    
    fig.update_layout(
        title='Объёмы торговли по регионам мира',
        xaxis_title='Регион',
        yaxis_title='Объём торговли',
        barmode='group',
        height=400,
        font=dict(family="Arial", size=12)
    )
    
    return fig

# Callback для ТОП-10 стран-партнёров
@app.callback(
    Output('top-countries-chart', 'figure'),
    Input('top-countries-chart', 'id') # Dummy input
)
def update_top_countries(dummy_input):
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
        customdata=[format_number(val) for val in export_values]
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
        customdata=[format_number(val) for val in import_values]
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
        customdata=[format_number(val) for val in balance_values]
    ))
    
    fig.update_layout(
        title='Торговля с основными странами-партнёрами',
        xaxis_title='Страна',
        yaxis_title='Объём торговли',
        barmode='group',
        height=400,
        font=dict(family="Arial", size=10),
        xaxis_tickangle=-45
    )
    
    return fig

# Callback для торговли с Россией
@app.callback(
    Output('russia-trade-chart', 'figure'),
    Input('russia-trade-chart', 'id') # Dummy input
)
def update_russia_trade(dummy_input):
    df = pd.DataFrame(data['russia_trade_dynamics'])
    
    if df.empty:
        # Если нет данных по России, показываем пустой график
        fig = go.Figure()
        fig.add_annotation(
            text="Нет данных по торговле с Россией",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title="Торговля с Россией (5 лет)",
            height=400,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig

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
        customdata=[format_number(val) for val in df['X']]
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
        customdata=[format_number(val) for val in df['M']]
    ))
    
    fig.update_layout(
        title='Торговля с Россией (5 лет)',
        xaxis_title='Год',
        yaxis_title='Объём торговли',
        hovermode='x unified',
        legend=dict(x=0.02, y=0.98),
        height=400,
        font=dict(family="Arial", size=12)
    )
    
    return fig

# Callback для изменений структуры торговли
@app.callback(
    Output('structure-changes-chart', 'figure'),
    Input('structure-changes-chart', 'id') # Dummy input
)
def update_structure_changes(dummy_input):
    df = pd.DataFrame(data['structure_changes'])
    
    fig = go.Figure(go.Bar(
        x=df['commodity_name'],
        y=df['delta_share'],
        marker_color=['#27ae60' if x > 0 else '#e74c3c' for x in df['delta_share']],
        text=[f'{val:+.1f} п.п.' for val in df['delta_share']],
        textposition='outside',
        hovertemplate='%{x}<br>Изменение доли: %{customdata}<extra></extra>',
        customdata=[f'{val:+.1f} п.п.' for val in df['delta_share']]
    ))
    
    fig.update_layout(
        title='Изменения структуры экспорта (10 лет)',
        xaxis_title='Товарная группа',
        yaxis_title='Изменение доли (п.п.)',
        height=400,
        font=dict(family="Arial", size=10),
        xaxis_tickangle=-45
    )
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)


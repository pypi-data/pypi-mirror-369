import plotly.express as px # type: ignore
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots # type: ignore
import plotly.io as pio
pio.renderers.default = 'browser'

def create_double_axis_barchart(df, title, x_var, x_title, 
                              primary_vars, primary_title,
                              secondary_vars, secondary_title,
                              explanation_text,
                              save_file=False, file_name="barchart", file_location=""):
    """
    Creates a bar chart with two y-axes and all styling elements.
    """
    # Create subplot with two y-axes
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add primary axis bars
    for i, col in enumerate(primary_vars):
        fig.add_trace(
            go.Bar(
                x=df[x_var],
                y=df[col],
                name=col,
                marker_color=px.colors.qualitative.Alphabet[i],
                opacity=0.9,
                hovertemplate=f"<b>{col}</b><br>{x_title}: %{{x}}<br>{primary_title}: %{{y}}<extra></extra>"
            ),
            secondary_y=False
        )
    
    # Add secondary axis bars
    for i, col in enumerate(secondary_vars):
        fig.add_trace(
            go.Scatter(
                x=df[x_var],
                y=df[col],
                name=col,
                marker_color=px.colors.qualitative.Dark24[i],
                opacity=0.9,
                hovertemplate=f"<b>{col}</b><br>{x_title}: %{{x}}<br>{secondary_title}: %{{y}}<extra></extra>"
            ),
            secondary_y=True
        )
    
    # Layout configuration
    layout_config = {
        'title': f'<span style="font-size:24px; font-weight:700">{title.upper()}</span>',
        'plot_bgcolor': '#F8F8F8',
        'paper_bgcolor': 'white',
        'font_family': 'Arial, sans-serif',
        'title_x': 0.5,
        'title_y': 0.95,
        'margin': dict(l=50, r=220, b=150, t=100, pad=10),
        'legend': {
            'title_text': '<b>VARIABELEN</b>',
            'orientation': 'v',
            'yanchor': 'top',
            'y': 0.98,
            'xanchor': 'left',
            'x': 1.02,
            'font': dict(size=10),
            'bgcolor': 'rgba(255,255,255,0.8)'
        },
        'barmode': 'group',
        'bargap': 0.15,
        'bargroupgap': 0.1
    }
    
    fig.update_layout(**layout_config)
    
    # Axis customization
    fig.update_xaxes(
        title=f'<b>{x_title.upper()}</b>',
        showline=True,
        linecolor='#D3D3D3',
        tickangle=-45,
        gridcolor='#E0E0E0'
    )
    
    fig.update_yaxes(
        title=f'<b>{primary_title.upper()}</b>',
        showline=True,
        linecolor='#D3D3D3',
        gridcolor='#E0E0E0',
        secondary_y=False
    )
    
    fig.update_yaxes(
        title=f'<b>{secondary_title.upper()}</b>',
        showline=True,
        linecolor='#4A8B39',
        gridcolor='rgba(210,210,210,0.3)',
        secondary_y=True
    )
    
    # Explanation button
    fig.add_annotation(
        x=0.5,
        y=-0.25,
        xref='paper',
        yref='paper',
        text="<span style='font-size:14px; color:#4A8B39'>ℹ️ KLIK HIER VOOR Uitleg</span>",
        showarrow=False,
        align='center',
        bordercolor='#4A8B39',
        borderwidth=1,
        borderpad=6,
        bgcolor='white',
        hovertext=explanation_text,
        hoverlabel=dict(
            bgcolor='white',
            font_size=13,
            font_family='Arial',
            bordercolor='#4A8B39'
        )
    )
    
    # Save functionality
    if save_file:
        if not file_name.endswith('.html'):
            file_name += '.html'
        
        if file_location:
            os.makedirs(file_location, exist_ok=True)
            save_path = os.path.join(file_location, file_name)
        else:
            save_path = file_name
        
        fig.write_html(save_path)
        print(f"Chart saved to: {os.path.abspath(save_path)}")
    
    return fig


def create_uitstroom_linegraph(df, title, x_var, x_title, explanation_text, 
                         save_file=False, file_name="uitstroom_plot", file_location=""):
    """
    Maakt een professionele uitstroomgrafiek met alle opmaakelementen en opslagmogelijkheid.
    """
    # Maak de plot
    fig = px.line(
        df,
        x=x_var,
        y=df.columns.drop(x_var),
        title=f'<span style="font-size:24px; font-weight:700">{title.upper()}</span>',
        labels={'value': 'Percentage', 'variable': 'Kanaal'},
        range_y=[0, 1],
        color_discrete_sequence=px.colors.qualitative.Alphabet[:20]  # 20 verschillende kleuren
    )

    # Lijnstijl
    fig.update_traces(
        hovertemplate="<b>%{fullData.name}</b><br>Percentage: %{y:.1%}<extra></extra>",
        line_width=2.5,
        opacity=0.9
    )

    # Layout-opmaak
    fig.update_layout(
        hovermode='x unified',
        plot_bgcolor='#F8F8F8',
        paper_bgcolor='white',
        font_family='Arial, sans-serif',
        title_x=0.5,
        title_y=0.95,
        margin=dict(l=50, r=220, b=150, t=100, pad=10),
        legend=dict(
            title_text='<b>INSTROOM KANALEN</b>',
            orientation='v',
            yanchor='top',
            y=0.98,
            xanchor='left',
            x=1.02,
            font=dict(size=10),
            bgcolor='rgba(255,255,255,0.8)'
        )
    )

    # As-opmaak
    fig.update_xaxes(
        title=f'<b>{x_title.upper()}</b>',
        showline=True,
        linecolor='#D3D3D3',
        tickangle=-45,
        gridcolor='#E0E0E0'
    )
    
    fig.update_yaxes(
        title='<b>PERCENTAGE UITSTROOM</b>',
        tickformat='.0%',
        showline=True,
        linecolor='#D3D3D3',
        gridcolor='#E0E0E0'
    )

    # Uitlegknop - NU MET CORRECTE POSITIONERING
    fig.add_annotation(
        x=0.5,
        y=-0.25,  # Iets lager geplaatst
        xref='paper',
        yref='paper',
        text="<span style='font-size:14px; color:#4A8B39'>ℹ️ KLIK HIER VOOR Uitleg</span>",
        showarrow=False,
        align='center',
        bordercolor='#4A8B39',
        borderwidth=1,
        borderpad=6,
        bgcolor='white',
        hovertext=explanation_text,
        hoverlabel=dict(
            bgcolor='white',
            font_size=13,
            font_family='Arial',
            bordercolor='#4A8B39'
        )
    )

    # Opslagfunctionaliteit
    if save_file:
        if not file_name.endswith('.html'):
            file_name += '.html'
        
        if file_location:
            os.makedirs(file_location, exist_ok=True)
            save_path = os.path.join(file_location, file_name)
        else:
            save_path = file_name
        
        fig.write_html(save_path)
        print(f"Grafiek opgeslagen als: {os.path.abspath(save_path)}")

    return fig

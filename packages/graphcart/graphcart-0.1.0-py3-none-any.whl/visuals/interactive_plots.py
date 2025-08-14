import plotly.express as px

def interactive_scatter(df, x, y, color=None, size=None, title=None):
    fig = px.scatter(df, x=x, y=y, color=color, size=size, title=title)
    fig.show()
    return fig

def interactive_map(df, lat_col, lon_col, hover_name=None, color=None, title=None, zoom=3):
    fig = px.scatter_mapbox(df, lat=lat_col, lon=lon_col, hover_name=hover_name, color=color, zoom=zoom)
    fig.update_layout(mapbox_style="open-street-map", title=title)
    fig.show()
    return fig

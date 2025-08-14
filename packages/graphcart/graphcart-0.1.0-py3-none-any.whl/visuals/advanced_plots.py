import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def hexbin_plot(df, x, y, gridsize=30, title=None):
    plt.figure(figsize=(8, 6))
    plt.hexbin(df[x], df[y], gridsize=gridsize)
    plt.xlabel(x); plt.ylabel(y)
    if title: plt.title(title)
    plt.colorbar(label="count")
    plt.tight_layout()
    plt.show()


def bubble_plot(df, x, y, size, title=None):
    plt.figure(figsize=(8, 6))
    plt.scatter(df[x], df[y], s=df[size], alpha=0.5)
    plt.xlabel(x); plt.ylabel(y)
    if title: plt.title(title)
    plt.tight_layout()
    plt.show()


def radar_chart(categories, values, title=None):
    from math import pi
    values = list(values)
    categories = list(categories)
    N = len(categories)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    # close the loop
    values += values[:1]
    angles += angles[:1]

    ax = plt.subplot(111, polar=True)
    plt.xticks(angles[:-1], categories)
    ax.plot(angles, values)
    ax.fill(angles, values, alpha=0.25)
    if title: plt.title(title)
    plt.tight_layout()
    plt.show()


def waterfall_chart(values, labels, title=None):
    import plotly.graph_objects as go
    fig = go.Figure(go.Waterfall(measure=["relative"]*len(values), x=labels, y=values))
    if title: fig.update_layout(title=title)
    fig.show()
    return fig

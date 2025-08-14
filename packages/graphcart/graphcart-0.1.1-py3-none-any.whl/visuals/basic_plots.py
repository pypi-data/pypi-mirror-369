import matplotlib.pyplot as plt
import seaborn as sns

sns.set()  # pleasant defaults

def bar_plot(df, x, y=None, horizontal=False, title=None):
    """Bar or count plot. If y is None, plots counts of x."""
    plt.figure(figsize=(8, 6))
    if y is None:
        sns.countplot(data=df, x=x)
    else:
        if horizontal:
            sns.barplot(data=df, y=x, x=y)
        else:
            sns.barplot(data=df, x=x, y=y)
    if title: plt.title(title)
    plt.tight_layout()
    plt.show()


def line_plot(df, x, y, title=None):
    plt.figure(figsize=(9, 5))
    sns.lineplot(data=df, x=x, y=y)
    if title: plt.title(title)
    plt.tight_layout()
    plt.show()


def scatter_plot(df, x, y, hue=None, size=None, title=None):
    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=df, x=x, y=y, hue=hue, size=size)
    if title: plt.title(title)
    plt.tight_layout()
    plt.show()


def histogram(df, column, bins=30, kde=True, title=None):
    plt.figure(figsize=(8, 5))
    sns.histplot(df[column].dropna(), bins=bins, kde=kde)
    if title: plt.title(title)
    plt.tight_layout()
    plt.show()


def box_plot(df, x=None, y=None, title=None):
    plt.figure(figsize=(8, 6))
    if x is not None and y is not None:
        sns.boxplot(data=df, x=x, y=y)
    elif y is not None:
        sns.boxplot(y=df[y])
    else:
        raise ValueError("Provide y or both x and y for box_plot")
    if title: plt.title(title)
    plt.tight_layout()
    plt.show()


def pie_chart(df_or_values, column_or_labels=None, title=None, top_n=None):
    """Pie chart from a DF column (value counts) or from values+labels arrays."""
    import numpy as np
    import pandas as pd
    plt.figure(figsize=(7,7))
    if isinstance(df_or_values, (pd.DataFrame,)):
        counts = df_or_values[column_or_labels].value_counts()
        if top_n:
            counts = counts.nlargest(top_n)
        values, labels = counts.values, counts.index.tolist()
    else:
        values = df_or_values
        labels = column_or_labels
    plt.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    if title: plt.title(title)
    plt.axis("equal")
    plt.tight_layout()
    plt.show()


def area_plot(df, x, y, title=None):
    plt.figure(figsize=(9, 5))
    plt.fill_between(df[x], df[y], alpha=0.4)
    plt.plot(df[x], df[y])
    if title: plt.title(title)
    plt.tight_layout()
    plt.show()

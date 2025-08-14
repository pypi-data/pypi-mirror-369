import matplotlib.pyplot as plt
import pandas as pd

def ts_line(df, date_col, value_col, title=None):
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col)
    plt.figure(figsize=(10,5))
    plt.plot(df[date_col], df[value_col])
    if title: plt.title(title)
    plt.tight_layout()
    plt.show()


def rolling_mean(df, date_col, value_col, window=7, title=None):
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col)
    roll = df[value_col].rolling(window=window).mean()
    plt.figure(figsize=(10,5))
    plt.plot(df[date_col], df[value_col], alpha=0.4, label=value_col)
    plt.plot(df[date_col], roll, label=f"{window}-period mean")
    plt.legend()
    if title: plt.title(title)
    plt.tight_layout()
    plt.show()

import matplotlib.pyplot as plt
import seaborn as sns

def violin_plot(df, x, y, title=None):
    plt.figure(figsize=(8, 6))
    sns.violinplot(data=df, x=x, y=y)
    if title: plt.title(title)
    plt.tight_layout()
    plt.show()


def swarm_plot(df, x, y, title=None):
    plt.figure(figsize=(8, 6))
    sns.swarmplot(data=df, x=x, y=y)
    if title: plt.title(title)
    plt.tight_layout()
    plt.show()


def strip_plot(df, x, y, title=None):
    plt.figure(figsize=(8, 6))
    sns.stripplot(data=df, x=x, y=y, jitter=True)
    if title: plt.title(title)
    plt.tight_layout()
    plt.show()


def kde_plot(df, column, shade=True, bw_adjust=1.0, title=None):
    plt.figure(figsize=(8, 5))
    sns.kdeplot(df[column].dropna(), fill=shade, bw_adjust=bw_adjust)
    if title: plt.title(title)
    plt.tight_layout()
    plt.show()

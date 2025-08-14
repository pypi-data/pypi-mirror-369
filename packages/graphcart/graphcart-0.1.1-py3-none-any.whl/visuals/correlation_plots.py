import matplotlib.pyplot as plt
import seaborn as sns

def correlation_heatmap(df, annot=False, cmap="coolwarm", title="Correlation Matrix"):
    corr = df.corr(numeric_only=True)
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=annot, cmap=cmap)
    plt.title(title)
    plt.tight_layout()
    plt.show()


def pair_plot(df, hue=None):
    sns.pairplot(df, hue=hue)
    plt.show()

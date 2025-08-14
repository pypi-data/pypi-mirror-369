from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np

def scatter3d(df, x, y, z, title=None):
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(df[x], df[y], df[z])
    ax.set_xlabel(x); ax.set_ylabel(y); ax.set_zlabel(z)
    if title: ax.set_title(title)
    plt.tight_layout()
    plt.show()


def surface3d(Z, X=None, Y=None, title=None):
    Z = np.array(Z)
    ny, nx = Z.shape
    if X is None or Y is None:
        X, Y = np.meshgrid(np.arange(nx), np.arange(ny))
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(X, Y, Z)
    if title: ax.set_title(title)
    plt.tight_layout()
    plt.show()

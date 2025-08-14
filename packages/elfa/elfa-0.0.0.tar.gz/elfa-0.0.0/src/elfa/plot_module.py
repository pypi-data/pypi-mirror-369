"""Plot module"""

import sys

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from .utils import resize_map

matplotlib.rcParams["mathtext.fontset"] = "stix"
matplotlib.rcParams["font.family"] = "STIXGeneral"


def plot_gallery(
    images, images_shape, n_col=1, n_row=1, cmap=plt.cm.gray, figsize=None, path=""
):
    """
    Plots different images as a grid (in subplots).

    Parameters
    -------
    images : array-like of shape (nº pixels, nº images)
        Batch of images.

    images_shape : duple (int, int)
        Shape of each the images.

    n_col : int, default=1
        Number of columns in the grid.

    n_row : int, default=1
        Number of rows in the grid.

    cmap : str, default=plt.cm.gray
        Color map.

    figsize : duple (int, int), default=None
        Shape of the whole figure. If None, equal to (2*n_cols, 2*n_row)

    path : str, default=""
        Saving path.

    Returns
    -------
    figure
    """
    if figsize == None:
        figsize = (2 * n_col, 2 * n_row)
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(n_row, n_col, hspace=0, wspace=0)
    axs = gs.subplots(sharex=True, sharey=True)
    n = 0
    _, b = images.shape
    N = n_col * n_row
    images_copy = images
    if N == 1:
        image = images_copy.reshape(images_shape)
        axs.imshow(image, cmap=cmap)
    else:
        for ax in axs.flat:
            if n < b:
                image = images_copy[:, n].reshape(images_shape)
                ax.imshow(image, cmap=cmap)
            n = n + 1

    fig.subplots_adjust(wspace=0, hspace=0)

    plt.setp(plt.gcf().get_axes(), xticks=[], yticks=[])
    if path:
        fig.savefig(path, bbox_inches="tight")
    plt.show()


def plot_matrix(matrix, figsize=None, cmap="RdBu_r", path=""):
    """
    Plots a matrix as a grid with colors in each cell corresponding to the value of that coefficient in the matrix.

    Parameters
    -------
    matrix : 2D array to plot.

    figsize : duple (int,int)
        Shape of the whole figure. If None, equal to matrix shape.

    cmap : str, default="RdBu_r"
        Color map.

    path : str, default=""
        Saving path

    Returns
    ------
    figure
    """
    if figsize == None:
        figsize = matrix.shape
    maxValue = np.abs(matrix).max()
    plt.figure(figsize=figsize)
    # plt.rcParams.update({"font.size": 32, "font.family": "sans-serif"})
    plt.imshow(matrix, cmap=cmap, vmax=maxValue, vmin=-maxValue)
    if matrix.shape[0] < matrix.shape[1]:
        plt.colorbar(location="bottom", aspect=40, pad=0.01)
    else:
        plt.colorbar(location="left", aspect=40, pad=0.01)

    if path:
        plt.savefig(path, bbox_inches="tight")

    plt.show()


def images_montage(images):
    """
    Montage of images

    Parameters
    -------
    images : array-like of shape (px, px, channels, nº images)

    Returns
    -------
    figure
    """
    d = images.shape[3]
    n_row = round(np.sqrt(d))
    fig = plt.figure()
    gs = fig.add_gridspec(n_row, n_row, hspace=0, wspace=0)
    axs = gs.subplots(sharex=True, sharey=True)
    n = 0
    for ax in axs.flat:
        if n < d:
            im = ax.imshow(images[:, :, :, n], interpolation="bilinear")
        n = n + 1
    plt.show


def similar_to_factor(
    WT, n_factor, output, factors, num_img, img_size, max_value=0.8, path=""
):
    """
    Displays a given latent factor and the most similar channels (observed variables)
    In order to obtain "similar_to_channel" you only need to provide WT transpose, n_factor = num channel, output=latent factors, and factors=output data

    Parameters
    -------
    WT : array-like of shape (n_component, n_features)
        Factor loading matrix

    n_factor : int
        Latent factor chosen

    output : array-like of shape (n_samples, n_features)
        Data (observed variables).

    factors : array-like of shape (n_samples, n_components)
        Latent factors obtained from the data.

    num_img : int
        Image chosen from the batch.

    img_size : duple (int,int)
        Size of the images of the data (activation map).

    max_value : float, default=0.8
        The features (channels) with correlation value with the chosen latent factor grater than max_value are chosen.

    path : str, default=""
        Saving path.

    Returns
    -------
    figure
    """
    Wrow = abs(WT[n_factor, :])
    h = img_size[0]
    w = img_size[1]
    num_pixels = h * w
    data = output[num_pixels * num_img : num_pixels * (num_img + 1), Wrow > max_value]
    factor = factors[num_pixels * num_img : num_pixels * (num_img + 1), n_factor]

    num_channels = data.shape[1]
    if num_channels == 1:
        sys.exit("Just one match in", np.where(Wrow > max_value)[0][0])
    ncol = np.minimum(np.floor(num_channels / 2).astype("int"), 4)
    ncol = ncol + 2

    rel = w / h
    fig = plt.figure(figsize=(ncol * rel, 2), constrained_layout=False)
    gs = fig.add_gridspec(2, ncol, wspace=0, hspace=0)

    ax0 = fig.add_subplot(gs[:, :2])
    factor = factor.reshape(img_size, order="F")
    ax0.imshow(factor, cmap=plt.cm.gray)
    ax0.set_xticks([])
    ax0.set_yticks([])

    row = 0
    col = 2
    m = (ncol - 2) * 2
    for i in range(m):
        col = col + row
        row = i % 2
        ax = fig.add_subplot(gs[row, col])
        data0 = data[:, i].reshape(img_size, order="F")
        ax.imshow(data0, cmap=plt.cm.gray)
        ax.set_xticks([])
        ax.set_yticks([])

    if path:
        fig.savefig(path, bbox_inches="tight")
    plt.show()


def plot_attributions(
    num_images, images, attribution_maps, mode=None, cmap="jet", path=""
):
    """
    Displays the attribution maps associated to given images

    Parameters
    -------
    num_images : int
        Number of images

    images : list
        List of images to show

    attribution_maps : dict
        Dictionary of the different types of attribution maps computed for all the images given

    mode : str, default=None
        Display mode, which could be superposition or mask. If None, the heatmap alone is displayed

    cmap : default=plt.cm.jet

    path : str, default=""
        Directory to save the figure
    """
    keys = list(attribution_maps.keys())
    ncols = len(keys) + 1
    fig, axes = plt.subplots(
        nrows=num_images, ncols=ncols, figsize=(ncols + 1, num_images + 0.5)
    )
    for i in range(num_images):
        img = np.uint8(images[i])
        axes[i, 0].imshow(img)
        axes[i, 0].axis("off")
        for j in range(ncols - 1):
            h_img = attribution_maps[keys[j]][i]
            if mode == "mask":
                h_img = resize_map(h_img)
                h_img = (h_img - np.min(h_img)) / (np.max(h_img) - np.min(h_img))
                heatmap = np.uint8(255 * h_img)
                img_feature = (
                    img * (heatmap[:, :, None].astype(np.float64) / np.amax(heatmap))
                ).astype(np.uint8)
                axes[i, j + 1].imshow(
                    img_feature, alpha=1, interpolation="gaussian", cmap=plt.cm.jet
                )
            elif mode == "superposition":
                h_img = resize_map(h_img)
                h_img = (h_img - np.min(h_img)) / (np.max(h_img) - np.min(h_img))
                heatmap = np.uint8(255 * h_img)

                axes[i, j + 1].imshow(img)
                axes[i, j + 1].imshow(heatmap, alpha=0.5, cmap=cmap)
            else:
                axes[i, j + 1].imshow(h_img, cmap=cmap)
            if i == 0:
                axes[i, j + 1].title.set_text(keys[j])
            axes[i, j + 1].axis("off")
    plt.tight_layout()
    if path:
        fig.savefig(path, dpi=500, bbox_inches="tight")
    plt.show()

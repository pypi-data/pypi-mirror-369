"""Module to generate attribution maps from factor matrix"""

import numpy as np
import tensorflow as tf


def efam_factors(WT, factors, act_shape, norm_method="max_min"):
    """
    Obtain the Essential Feature Attribution Maps (EFAM).

    Parameters
    -------
    WT : array-like of shape (n_components, n_features)
        Transpose factor loading matrix

    factors : array-like of shape (n_samples, n_components)
        Latent factors

    act_shape : array-like
        activation maps shape

    norm_method : str, default="max_min"
        Method for heatmap normalization

    model : bool, default=True
        Whether using a tensorflow (True) or MATLAB model

    Returns
    -------
    heatmap_norm : array-like of shape (batch, act_shape)
        Normalized heatmaps
    """
    a = np.sum(abs(WT), axis=1)  # vector of dimension n_components
    heatmap = np.sum(factors * a, axis=1)  # dimension n_samples
    heatmap = heatmap.reshape(-1, act_shape[0], act_shape[1])  # a heatmap per sample
    if np.all(heatmap == 0.0):
        return heatmap
    # For visualization purpose, we will normalize the heatmap between 0 & 1 or -1 & 1
    heatmap_norm = _normalize_heatmap(heatmap, norm_method)

    return heatmap_norm


def _normalize_heatmap(heatmap, norm_method="max_min"):
    """Normalize heatmap"""
    h_max = tf.math.reduce_max(heatmap, axis=(1, 2), keepdims=True)
    h_min = tf.math.reduce_min(heatmap, axis=(1, 2), keepdims=True)
    habs_max = tf.math.reduce_max(tf.math.abs(heatmap), axis=(1, 2), keepdims=True)

    if norm_method == "relu":
        heatmap_norm = tf.maximum(heatmap, 0) / h_max
    elif norm_method == "max_min":
        heatmap_norm = (heatmap - h_min) / (h_max - h_min)
    elif norm_method == "max":
        heatmap_norm = heatmap / habs_max

    return heatmap_norm

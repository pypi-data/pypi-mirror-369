"""Module to process convolutional neural networks"""

import numpy as np
import tensorflow as tf

from . import utils


def get_conv_indx(model):
    """Apply to a NN to obtain the indexes of all the convolutional layers.
    Be aware that the output of a conv layer includes the activation function.

    Parameters
    ----------
    model : neural network model.

    Returns
    -------
    idxConvLayers : 1D array-like
        Indices of conv layers according to Layers .
    """
    # Get the layers of the model
    layers = model.layers
    len_layers = len(layers)
    idx_conv_layers = []
    # Obtain only the convolutional ones
    for i in range(len_layers):
        if isinstance(layers[i], tf.keras.layers.Conv2D):
            idx_conv_layers.append(i)

    return idx_conv_layers


def partial_model(base_model, num_conv):
    """Apply to a NN to return the output of
    certain convolutional layer.

    Parameters
    ----------
    base_model : neural network model

    num_conv : int
        Convolutional layer (first=0, second=1,...).

    Returns
    -------
    partial_model : new NN model .
    """
    # Get the indices of the convolutional layers
    idx_conv_layers = get_conv_indx(base_model)
    # Check that the index given is right
    if num_conv > len(idx_conv_layers) - 1 and num_conv != -1:
        raise ValueError(
            "Not so many convolutional layers"
            ": %d > %d" % (num_conv, len(idx_conv_layers) - 1)
        )
    # Obtain the modified NN
    out_layers = [base_model.layers[idx_conv_layers[num_conv]].output]
    partial_model = tf.keras.Model(inputs=base_model.input, outputs=out_layers)

    return partial_model


def conv_output_data(partial_model, img, layer_name):
    """Obtain the output of a convolutional layer in the required data shape.
    For this use a modified NN that returns the desired output.

    Assume the convolutional output is of shape (hpx,wpx,N) with N the number of channels/kernels.

    Parameters
    ----------
    partial_model : modified NN model

    img : array-like of shape (batch_size, input_size, input_size, input_channels)
        Input batch of images already preprocessed.

    layer_name : string
        If torch, name of the layer studied

    Returns
    -------
    data_grad : torch Tensor
        Output of the torch partial model. None in the case of a keras model

    data : array-like of shape (hpx*wpx*batch_size, num_channels)
        Output of partial model

    hpx : int
        Number of row pixels

    wpx : int
        Number of column pixels

    num_channels :  int
        Number of output channels
    """
    # Get the output of the model
    conv_features = partial_model.predict(img)
    # Reshape it
    batch, hpx, wpx, num_channels = conv_features.shape
    data = conv_features.reshape(hpx * wpx * batch, num_channels)

    return data, hpx, wpx, num_channels


def get_fa_input(
    batch_size,
    dstrain,
    img_size,
    partial_model,
    name_layer,
    normalize=True,
    ite=20,
):
    # Obtain images batch
    print("Batch...")
    images_batch, _ = utils.get_batch(batch_size, dstrain, img_size)

    # Obtain input data for FA method
    print("Input data...")
    _, data, hpx, wpx, num_channels = conv_output_data(
        partial_model, images_batch, name_layer
    )

    # Normalize input data
    it = 0
    if normalize:
        while 0 in np.std(data, axis=0) and it < ite:
            it += 1
            print("Standard deviation has a zero value")
            images_batch, _ = utils.get_batch(batch_size, dstrain, img_size)
            _, data, hpx, wpx, num_channels = conv_output_data(
                partial_model, images_batch, name_layer
            )
        if it == ite:
            print(
                "Standard deviation has a zero value in all iterations. It will be only normalized by the mean"
            )
            data = data - np.mean(data, axis=0)
        else:
            data = (data - np.mean(data, axis=0)) / np.std(data, axis=0)

    return data, hpx, wpx, num_channels

"""Module to reconstruct image from factor matrix"""

import IPython.display as display
import numpy as np
import tensorflow as tf

from . import loadshow


def factor_loading_features(WT, num_factor, hpx, wpx, num_channels):
    """Compute an output of a convolutional layer with the values of the factor loading matrix associated to the desired value

    Parameters
    -------
    WT : array-like of shape (n_components, n_features)
        Transpose factor loading matrix

    num_factor : int
        Number of the factor you want to study.

    hpx : int
        Number of row pixels.

    wpx : int
        Number of columns pixels.

    num_channels : int
        Number of channels of the output of the convolution (or kernels).

    Returns
    -------
    loadings_features : array-like of shape (hpx, wpx, num_channels)
        Array with the values of the factor loadings for the desired factor.
    """
    w = WT[num_factor, :]
    loadings_features = np.zeros((hpx, wpx, num_channels))
    for i in range(hpx):
        for j in range(wpx):
            loadings_features[i, j, :] = w  # + data_mean

    return loadings_features


def _calc_loss(img, model, w_column):
    """Compute the value of the loss given an input image.

    Parameters
    -------
    img : 2D array
        Input image.

    model : TensorFlow Model
        Neural Network model.

    w_column : 1D array of shape n_features
        Column of the factor loading matrix associated to the desired factor.

    Returns
    -------
    Loss value
    """
    # Pass forward the image through the model to retrieve the activations.
    # Converts the image into a batch of size 1.
    img_batch = tf.expand_dims(img, axis=0)
    layer_activations = model(img_batch)
    if len(layer_activations) == 1:
        layer_activations = [layer_activations]

    losses = []
    for act in layer_activations:
        # act_mean = tf.math.reduce_mean(act, (1,2), keepdims=True)
        # act_normalize = tf.subtract(act,act_mean)
        act_flat = tf.reshape(act, [-1])
        w_flat = tf.reshape(tf.convert_to_tensor(w_column, np.float32), [-1])
        remainder = tf.math.squared_difference(act_flat, w_flat)
        numerator = tf.math.reduce_sum(remainder)
        norm_w_column = tf.math.reduce_sum(tf.math.square(w_flat)) + 1e-8
        loss = numerator / norm_w_column
        losses.append(loss)

    return tf.reduce_sum(losses)


class DeepDream(tf.Module):
    """Class to compute gradient descend of a NN model given a loss function"""

    def __init__(self, model):
        self.model = model

    @tf.function(
        input_signature=(
            tf.TensorSpec(shape=[None, None, 3], dtype=tf.float32),
            tf.TensorSpec(shape=[None, None, None], dtype=tf.float32),
            tf.TensorSpec(shape=[], dtype=tf.int32),
            tf.TensorSpec(shape=[], dtype=tf.float32),
        )
    )
    def __call__(self, img, w_column, steps, step_size):
        """Compute gradient descend wrt the input image using _calc_loss as
        loss function

        Parameters
        -------
        img : array-like
            Input image.

        w_column : 1D array of shape n_features
            Column of the factor loading matrix.

        steps : int
            Number of steps in gradient descend.

        step_size : int
            Learning rate for gradient descend.

        Returns
        -------
        loss : float
            Loss value.

        img : 2D array of same shape as input image
            Optimized image with values between -1 and 1.
        """
        print("Tracing")
        loss = tf.constant(0.0)
        for n in tf.range(steps):
            with tf.GradientTape() as tape:
                # This needs gradients relative to `img`
                # `GradientTape` only watches `tf.Variable`s by default
                tape.watch(img)
                loss = _calc_loss(img, self.model, w_column)

            # Calculate the gradient of the loss with respect to the pixels of the input image.
            gradients = tape.gradient(loss, img)

            # Normalize the gradients.
            gradients /= tf.math.reduce_std(gradients) + 1e-8

            # In gradient ascent, the "loss" is maximized so that the input image increasingly "excites" the layers.
            # You can update the image by directly adding the gradients (because they're the same shape!)
            img = img - gradients * step_size

            # de momento da problemas https://github.com/pranshu28/cnn-viz/blob/master/viz_gradient_ascent.py
            # Define weights for individual regularization
            # reg_func = l2_decay_reg
            # weights = np.float32(3)
            # weights /= np.sum(weights)

            # Apply regularization on the gradient ascent output image
            # images = reg_func(img)
            # weighted_images = np.float32(weights*images)
            # img = np.sum(weighted_images, axis=0)
            img = tf.clip_by_value(img, -1, 1)

        return loss, img


def run_deep_dream_simple(
    img, partial_model, w_column, model, steps=100, step_size=0.01
):
    """
    Obtain the optimize image associated with certain latent factor.

    Images are plotted as they are being optimized each 100 steps. The step and
    the loss value are printed.

    Parameters
    -------
    img : 2D array-like
        Input image already preprocessed.

    partial_model : Neural Network model.

    w_column : 1D array of shape n_features
        Column of the factor loading matrix associated to the desired latent
        factor.

    model : NN model

    steps : int, default=100
        Number of steps in gradient descend.

    step_size : int, defaults=0.01
        Learning rate for gradient descend.

    Returns
    -------
    loss : float
        Loss value

    result : 2D array of same shape as input image
        Optimized image.
    """
    deepdream = DeepDream(partial_model)
    img = tf.convert_to_tensor(img)
    step_size = tf.convert_to_tensor(step_size)
    steps_remaining = steps
    step = 0
    while steps_remaining:
        if steps_remaining > 100:
            run_steps = tf.constant(100)
        else:
            run_steps = tf.constant(steps_remaining)
        steps_remaining -= run_steps
        step += run_steps
        loss, img = deepdream(img, w_column, run_steps, tf.constant(step_size))

        display.clear_output(wait=True)
        loadshow.show(loadshow.deprocess(img))
        print("Step {}, loss {}".format(step, loss))

    result = loadshow.deprocess(img)
    display.clear_output(wait=True)
    loadshow.show(result)
    loadshow.show(result, gray=True)

    return loss, result

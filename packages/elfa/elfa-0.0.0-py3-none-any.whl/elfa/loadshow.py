"""Module to download, show and work with images"""

import IPython.display as display
import numpy as np
import PIL.Image
import tensorflow as tf
import tensorflow_datasets as tfds


def load(image_path, size):
    """Open and image, resize it and return as as a NumPy array.

    Parameters
    -------
    image_path : str

    size : int

    Returns
    -------
    Image of shape (size, size)
    """
    image = PIL.Image.open(image_path)
    img = image.resize((size, size))
    return np.array(img)


def download(url, size):
    """Download an image and resize it.

    Parameters
    -------
    url : str

    size : int

    Returns
    -------
    Image of shape (size,size)
    """
    name = url.split("/")[-1]
    image_path = tf.keras.utils.get_file(name, origin=url)
    img = PIL.Image.open(image_path)
    img = img.resize((size, size))
    return np.array(img)


def deprocess(img):
    """Normalize an image whose values are between -1 and 1

    Parameters
    -------
    img : array-like with values between -1 and 1

    Returns
    -------
    Image array-like with values between 0 and 255
    """
    img = 255 * (img + 1.0) / 2.0
    return tf.cast(img, tf.uint8)


def show(img, gray=False):
    """Display and image (only IPython)"""
    if gray:
        img = PIL.Image.fromarray(np.array(img, dtype="uint8")).convert("L")
    else:
        img = PIL.Image.fromarray(np.array(img, dtype="uint8"))

    display.display(img)


def import_tf_dataset(data_name, set_name, shuffle=True, buffer_size=10_000):
    """
    Import a tensorflow dataset
    If it is not imagenette take care of the number when shuffeling

    Parameters
    -------
    data_name : str
        Name of the dataset to import

    set_name : str
        Name of the subset of the dataset to import (e.g., 'test', 'train', 'validation')

    shuffle : bool, default=True
        Whether to perform a new shuffle before each extraction of a subset of the dataset

    Returns
    -------
    test : tf.data.Dataset
    """
    dataset_builder = tfds.builder(data_name)
    dataset_builder.download_and_prepare()
    datasets = dataset_builder.as_dataset(as_supervised=True)
    test: tf.data.Dataset = datasets[set_name]
    if shuffle:
        test = test.shuffle(buffer_size, reshuffle_each_iteration=True)
    return test

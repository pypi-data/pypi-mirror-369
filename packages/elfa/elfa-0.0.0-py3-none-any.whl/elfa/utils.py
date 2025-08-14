import csv

import numpy as np
import tensorflow as tf

from .constants import IMG_SIZE


def write_data(data, file_name, mode="w", delimiter=","):
    """Write data in a csv file with name file_name"""
    with open(file_name, mode=mode, newline="") as file:
        writer = csv.writer(file, delimiter=delimiter)
        writer.writerow(data)


def get_batch(batch_size, test: tf.data.Dataset, img_size):
    """
    Batch of images of shape (batch_size, H, W, num_channels)

    Parameters
    -------
    batch_size : int

    test : tf.data.Dataset

    img_size : tuple (H,W)
      Shape in order to resize images if necessary

    Returns
    -------
    images_batch : array-like
      Batch of images

    images_list : list[np.ndarray]
      List of images
    """
    images_list = []
    for images, labels in test.take(batch_size):
        images = tf.image.resize(images, img_size)
        images_list.append(images.numpy())

    images_batch = np.stack(images_list, 0)

    return images_batch, images_list


def get_batch_labels(batch_size, test, img_size):
    """
    Batch of images of shape (batch_size, H, W, num_channels)

    Parameters
    -------
    batch_size : int

    test : tf.data.Dataset

    img_size : tuple (H,W)
      Shape in order to resize images if necessary

    Returns
    -------
    images_batch : array-like
      Batch of images

    images_list : list[np.ndarray]
      List of images

    labels_list : list[int]
      List of labels
    """
    images_list = []
    labels_list = []
    for images, labels in test.take(batch_size):
        images = tf.image.resize(images, img_size)
        images_list.append(images.numpy())
        labels_list.append(labels)

    images_batch = np.stack(images_list, 0)

    return images_batch, images_list, labels_list


def resize_map(map, size=IMG_SIZE):
    return tf.image.resize(map[:, :, tf.newaxis], (size[0], size[1]))[:, :, 0]


def set_batch(x_list, labels, batch_size=8):
    """Batch of random images taken from a list, and their corresponding labels"""
    idx_batch = np.random.choice(len(x_list), batch_size, replace=False).astype(int)
    x_batch_list = [x_list[i] for i in idx_batch]
    x_batch = np.array(x_batch_list)
    y_batch = np.array([labels[i] for i in idx_batch])
    return x_batch_list, x_batch, y_batch, idx_batch

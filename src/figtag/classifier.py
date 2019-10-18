import joblib

from PIL import Image

import numpy as np
import torch


def classifier(image_path: str, vae_model_path: str, kmeans_model_path: str) -> str:
    """
    Return cluster id assigned to specified image.

    Parameters:
    :param image_path:          path to an image.
    :param vae_model_path:      path to serialized VAE model.
    :param kmeans_model_path:   path to serialized Kmeans model.
    """
    _classifier = _Classifier(vae_model_path, kmeans_model_path)
    return _classifier.classify_image(image_path)


class _Classifier:
    def __init__(self, vae_model_path: str, kmeans_model_path: str):
        self._encoder = load_vae_model(vae_model_path)
        self._kmeans = load_kmeans_model(kmeans_model_path)

    def classify_image(self, image_path: str) -> str:
        im = load_image_as_tensor(image_path)
        X = torch.Tensor.reshape(im, [1, 1, 100, 100])
        mu = self._encoder.infer(X)
        return self._kmeans.predict(mu)[0]


def load_vae_model(path: str):
    """
    Return Variational Auto Encoder model.
    :aparam path: path to a serialized instance of KMeans model.
    """
    def make_device(use_gpu=True):
        """ Return device: cpu or gpu
        """
        return torch.device("cuda:0" if torch.cuda.is_available() else "cpu") \
            if use_gpu \
            else torch.device("cpu")

    # Read checkpoint file and re-map storage to lowest common denominator - 'cpu'.
    checkpoint = torch.load(path, map_location=lambda storage, loc: storage)
    model = checkpoint['model']
    model.to(make_device())
    return model


def load_kmeans_model(path: str):
    """
    Return KMeans model.
    :aparam path: path to a serialized instance of KMeans model.
    """
    return joblib.load(path)


def load_image_as_tensor(path):
    """ Load image as gray scale image and
        resize it to 100 x 100 while keeping aspect ratio.

        Return tensor representing the image.

        Parameters:
        :param path: path to an image.
    """
    image = Image.open(path).convert('L')

    im_size = 100

    # Resize image, keeping aspect ratio, such that
    # smaller side of the image is set to 100 px.
    width, height = image.size
    if width > height:
        ratio = width / height
        new_w, new_h = (int(0.5 + im_size * ratio), im_size)
    else:
        ratio = height / width
        new_w, new_h = (im_size, int(0.5 + im_size * ratio))
    image = image.resize((new_w, new_h))
    width, height = image.size

    # Crop center of the image
    crop_width, crop_height = (im_size, im_size)
    dx = (width - crop_width) // 2
    dy = (height - crop_height) // 2
    left, right = dx, dx + crop_width
    top, bottom = dy, dy + crop_height
    image = image.crop((left, top, right, bottom))

    np_image = np.array(image, dtype=np.float32)
    np_image = np.reshape(np_image, (im_size, im_size, 1))
    np_image /= 255.
    np_image = np_image.transpose((2, 0, 1))

    X = torch.from_numpy(np_image).type(torch.FloatTensor)
    return X

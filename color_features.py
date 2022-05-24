from sklearn.cluster import MiniBatchKMeans
import cv2
from PIL import Image
from PIL import ImageStat

import numpy as np
import skimage.measure


def get_brightness_of_image(image_path):
    """
    return the brightness of a given image
    :param image_path: an image path
    :return: the brightness (1-255)
    """
    im = Image.open(image_path).convert('L')
    stat = ImageStat.Stat(im)
    return stat.mean[0]


def get_saturation_of_image(image_path):
    """
    return the saturation of a given image
    :param image_path: an image path
    :return: the saturation (1-240)
    """
    img = cv2.imread(image_path)
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    return img_hsv[:, :, 1].mean()


def get_image_entropy(image_path):
    """
    the function returns the entropy of an image
    :param image_path: the path to the given image
    :return: the image's entropy
    """
    gray_img = Image.open(image_path).convert('L')  # converting to grayscale
    gray_img_array = np.array(gray_img)
    # using the shannon entropy function to calculate the entropy
    return skimage.measure.shannon_entropy(gray_img_array)



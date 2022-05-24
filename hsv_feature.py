import numpy as np
from PIL import Image


def get_all_colors_in_frame(img_path):
    """
    a function that get all the colors from an image and how much they appear in the image
    :param img_path: the path to the wanted image
    :return: all the colors in the image and how many times they appear
    """
    im = Image.open(img_path).convert('RGB')
    na = np.array(im)
    return np.unique(na.reshape(-1, 3), axis=0, return_counts=True)  # first = all colors, second = num of appearance


def get_most_close_color(img_path):
    """
    a function that return how much 12 colors appear in an image
    :param img_path: the path to the wanted image
    :return: how much 12 colors appear in an image
    """
    color_dict = {(0, 0, 0): 0, (25, 25, 25): 0, (50, 50, 50): 0, (136, 204, 111): 0, (80,151,53): 0, (54,102,36): 0,
                  (91,200,208): 0, (250,194,50): 0, (255,255,255): 0, (176,163,64): 0,
                  (192,192,192): 0}
    # black_1 black_2 black_3 green_1 green_2 green_3 light_blue orange white brown gray
    color_list = list(color_dict)
    colors, counts = get_all_colors_in_frame(img_path)
    for color_index in range(len(colors)):
        results_list = []
        for color in color_list:
            res = np.linalg.norm(colors[color_index] - list(color))  # calculate dist between vectors
            res = abs(res)
            results_list.append(res)
        minimum = results_list[0]
        min_index = 0
        for result_index in range(len(results_list)):
            if minimum > results_list[result_index]:
                minimum = results_list[result_index]
                min_index = result_index
        color_dict[color_list[min_index]] += counts[color_index]
    return get_percentage(color_dict)


def get_percentage(color_dict):
    """
    return how many times something appear in a dict (in percentage)
    :param color_dict: a dict to get values from
    :return: percentage of how times the color appear
    """
    color_percent = {}
    sum_of_all = sum(color_dict.values())
    for color in color_dict.keys():
        color_percent[color] = (color_dict[color] / sum_of_all) * 100
    return color_percent

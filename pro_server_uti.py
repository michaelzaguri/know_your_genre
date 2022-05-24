import yolo_commands
from PIL import Image
import numpy as np
import skimage.measure


SELECTED_CLASSES_IDS = {"person": 0, "motorcycle": 3, "airplane": 4, "bus": 5,
                        "train": 6, "traffic light": 9, "dog": 16, "couch": 57,
                        "tv": 62}
SELECTED_CLASSES = SELECTED_CLASSES_IDS.keys()


def get_frame_objects(net, ln, img_path):
    obj_dict = yolo_commands.getting_objects_from_picture(net, ln, img_path)
    return {key: obj_dict[value] for key, value in SELECTED_CLASSES_IDS.items()}


def update_object_counts(frames_obj_count, total_obj_appear, classes_in_frame):
    """
    updates the object related features for a whole video after every frame
    :param frames_obj_count: number of frames the objects were in, a list for all of the objects
    :param total_obj_appear: the average number of appearances in a frame, a list fpr all the objects
    :param classes_in_frame: all the classes counts that were in a certain frame
    :return: none
    """
    for class_name in SELECTED_CLASSES:
        if classes_in_frame[SELECTED_CLASSES_IDS[class_name]] != 0:  # if the count for that object != 0
            if(class_name == 'person'):
                total_obj_appear[class_name + '_avr_appear_count'] += classes_in_frame[SELECTED_CLASSES_IDS[class_name]]
            else:
                frames_obj_count[class_name + '_frames_percent'] += 1


def create_objects_record(frames_obj_count, total_obj_appear, frames_num):
    """
    the functions creates the final list that represents the relevant object-related
    features in the correct order for the whole video
    :param frames_obj_count: number of frames the objects were in, a list for all of the objects
    :param total_obj_appear: the average number of appearances in a frame, a list fpr all the objects
    :param frames_num:
    :return:
    """
    objects_record = []
    for class_name in SELECTED_CLASSES:
        if(class_name == "person"):
            objects_record.append(total_obj_appear[class_name + '_avr_appear_count'] / frames_num)
        else:
            objects_record.append(frames_obj_count[class_name + '_frames_percent'] / frames_num * 100)

    return objects_record

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


def update_color_counts(color_total_counts, colors_in_frame):
    """
    the function updates the color count feature for a whole video after every frame
    :param color_total_counts:
    :param colors_in_frame:
    :return:
    """
    for color_id in range(len(color_total_counts)):
        color_total_counts[color_id] += colors_in_frame[color_id]


def create_colors_record(color_total_counts, frames_num):
    """
    the functions creates the final list that represents the relevant colors-related
    feature for the whole video
    :param color_total_counts:
    :param frames_num:
    :return:
    """
    colors_record = []
    for i in range(len(color_total_counts)):
        colors_record.append(color_total_counts[i] / frames_num)
    return colors_record

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
    color_dict = {(0, 0, 0): 0, (25, 25, 25): 0, (50, 50, 50): 0, (136, 204, 111): 0, (250,194,50): 0,
                  (192,192,192): 0}
    # black_1 black_2 black_3 green_1 orange gray
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

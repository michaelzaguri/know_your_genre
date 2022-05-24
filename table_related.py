import pandas as pd
import yolo_commands
import os
import csv
import color_features
import hsv_feature
from itertools import chain

COLORS_DICT_KEYS = ["movie", "genre", "black_1", "black_2", "black_3", "green_1", "green_2", "green_3",
                    "light_blue", "orange", "white", "brown", "gray"]
frame_dict_keys = ["frame_id", "clip_id", "genre_id", "brightness", "saturation", "entropy",
                   "black_1", "black_2", "black_3", "green_1", "green_2",
                   "green_3", "light_blue", "orange", "white",
                   "brown", "gray"]
features_table_dict_keys = ["clip_id", "genre_id", "avg_brightness", "avg_saturation", "avg_entropy",
                            "avg_black_1", "avg_black_2", "avg_black_3", "avg_green_1", "avg_green_2",
                            "avg_green_3", "avg_light_blue", "avg_orange", "avg_white",
                            "avg_brown", "avg_gray"]
classes_count = 80
colors_count = 11


def create_classes_dict_for_frames_table(classes_file_path):
    """
    the function creates a dictionary with all the classes the yolo algorithm can detect,
    the function exists to make the process of making the frames table easier.
    the values will later have the count of each class' appearances on each frame
    :param classes_file_path: the path to a file containing all the classes it can detect
    :return: the dictionary with all the classes
    """
    classes_dict = {}
    with open(classes_file_path) as classes_file:
        classes_dict = {line.strip(): [] for line in classes_file}
        # empty value, we don't need any
    return classes_dict


def create_classes_dict_for_features_table(classes_file_path):
    """
    the function creates a dictionary with all the classes the yolo algorithm can detect,
    the function exists to make the process of making the feature table easier.
    the values will later have the average count of each class' appearances on each frame
    and the percent of the frames that had that object
    :param classes_file_path: the path to a file containing all the classes it can detect
    :return: the dictionary with all the classes
    """
    classes_dict = {}
    with open(classes_file_path) as classes_file:
        keys = chain.from_iterable(
            [(line.strip() + "_frames_percent", line.strip() + "_avr_appear_count") for line in classes_file])
        classes_dict = dict.fromkeys(keys, [])
        # empty values, we don't need any
    return classes_dict


def create_frames_table():
    """
    the function creates the frame table's dataframe
    :return: the frame table's dataframe
    """
    # white black red blue lime orange pink purple sky-blue yellow turquoise green
    table_dct = {frame_dict_key: [] for frame_dict_key in frame_dict_keys}

    # adding all of the classes yolo can detect to the dictionary
    table_dct.update(create_classes_dict_for_frames_table("/home/magshimim/know_your_genre/yolo/coco.names"))
    table_df = pd.DataFrame(data=table_dct)
    return table_df


def create_features_table():
    """
    the function creates the feature table's dataframe
    :return: the feature table's dataframe
    """
    table_dct = {features_table_dict_key: [] for features_table_dict_key in features_table_dict_keys}
    # adding all of the classes yolo can detect to the dictionary
    table_dct.update(create_classes_dict_for_features_table("/home/magshimim/know_your_genre/yolo/coco.names"))
    table_df = pd.DataFrame(data=table_dct)
    return table_df


def writing_movie_frames_into_tables(net, ln, dir_path, clip_id, genre_id):
    """
    the function writes all the frames of a certain movie into the frames and feature tables
    :param net: a value we get from the configuration of the model
    :param ln: a value we get from the configuration of the model
    :param dir_path: the path to the movie frames dir
    :param clip_id: the id of the trailer
    :param genre_id: the id of the genre of the trailer
    :return: none
    """
    with open("/home/magshimim/know_your_genre/frames_table.csv", "a") as frames_table, \
            open("/home/magshimim/know_your_genre/features_table.csv", "a") as features_table:
        frames_table_writer = csv.writer(frames_table)
        features_table_writer = csv.writer(features_table)
        frames_obj_count = [0]*classes_count
        # a list that each member represents the
        # number of frames that certain objects was in
        total_obj_appear = [0]*classes_count
        # a list that each member represents the
        # number of appearances the object had in the video

        total_brightness = 0
        total_satur = 0
        total_entropy = 0
        frames_num = len(os.listdir(dir_path))

        color_total_counts = [0]*colors_count

        for img in os.listdir(dir_path):
            image_path = dir_path + "/" + img
            frame_id = img[img.find("_") + 1: img.find(".")]
            classes = yolo_commands.getting_objects_from_picture(net, ln, image_path)
            update_object_counts(frames_obj_count, total_obj_appear, classes)

            brightness = color_features.get_brightness_of_image(image_path)
            total_brightness += brightness

            satur = color_features.get_saturation_of_image(image_path)
            total_satur += satur

            entropy = color_features.get_image_entropy(image_path)
            total_entropy += entropy

            colors = list(hsv_feature.get_most_close_color(image_path).values())
            update_color_counts(color_total_counts, colors)

            row = [frame_id, clip_id, genre_id, brightness, satur, entropy]
            row.extend(colors)
            row.extend(list(classes.values()))
            frames_table_writer.writerow(row)

        row = [clip_id, genre_id, total_brightness/frames_num,
               total_satur/frames_num, total_entropy/frames_num]
        row.extend(create_colors_record(color_total_counts, frames_num))
        row.extend(create_objects_record(frames_obj_count, total_obj_appear, frames_num))
        features_table_writer.writerow(row)
        print("done with", clip_id)


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


def update_object_counts(frames_obj_count, total_obj_appear, classes_in_frame):
    """
    updates the object related features for a whole video after every frame
    :param frames_obj_count: number of frames the objects were in, a list for all of the objects
    :param total_obj_appear: the average number of appearances in a frame, a list fpr all the objects
    :param classes_in_frame: all the classes counts that were in a certain frame
    :return: none
    """
    for class_id in range(classes_count):
        if classes_in_frame[class_id]:  # if the count for that object != 0
            frames_obj_count[class_id] += 1
            total_obj_appear[class_id] += classes_in_frame[class_id]


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
    for i in range(classes_count):
        objects_record.append(frames_obj_count[i] / frames_num * 100)
        objects_record.append(total_obj_appear[i] / frames_num)
    return objects_record


def append_movie_colors_to_csv(dir_path, clip_id, genre_id):
    classes_dict = {x: [] for x in COLORS_DICT_KEYS}
    df = pd.DataFrame(data=classes_dict)
    df.to_csv("/home/magshimim/know_your_genre/colors_table.csv")
    with open("/home/magshimim/know_your_genre/colors_table.csv", "a") as colors_table:
        colors_table_writer = csv.writer(colors_table)
        frames_num = len(os.listdir(dir_path))
        color_total_counts = [0] * colors_count

        for img in os.listdir(dir_path):
            image_path = dir_path + "/" + img

            colors = list(hsv_feature.get_most_close_color(image_path).values())
            update_color_counts(color_total_counts, colors)

        row = [clip_id, genre_id]
        row.extend(create_colors_record(color_total_counts, frames_num))
        colors_table_writer.writerow(row)
        print("done with", clip_id)


def append_genre_colors_to_csv(dir_path):
    for movie_dir in os.listdir(dir_path):
        append_movie_colors_to_csv(dir_path + movie_dir,
                                   movie_dir[movie_dir.find("_") + 1:],
                                   movie_dir[:movie_dir.find("_")])

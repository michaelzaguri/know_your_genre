from pytube import YouTube
import os
from pathlib import Path
import pandas as pd

import cv2
import yolo_commands
import table_related
import pro_server_uti


def download_trailer(genre, name, link):
    """
    the function downloads a youtube video as an mp4 file
    :param genre: the genre of the trailer
    :param name: the name of the movie of the trailer
    :param link: the link to the youtube video
    :return: none
    """
    path_suffix = genre + "_" + name.replace(" ", "_")
    path_to_download_folder = str(os.path.join(Path.home(), "know_your_genre/trailers_dir", genre))
    v_path = Path(path_to_download_folder)/f"{genre}_{name.replace(' ', '_')}"
    print(v_path)
    if not v_path.is_file():  # if the file has not been downloaded already
        url = YouTube(link)
        video = url.streams.get_highest_resolution()
        video.download(path_to_download_folder, path_suffix)


def fill_dirs_with_trailers(file_name):
    """
    fills a genre dirs with the trailers
    :param file_name: the name of the csv file containing all the links to the
    trailers with their names and genre
    :return: none
    """
    df = pd.read_csv(file_name)
    for index, row in df.iterrows():
        download_trailer(row['genre'], row['name'], row['link'])


def divide_into_frames(frame_divider, trailer_path, dst_path):
    """
    the function divides a trailer into frames and saves it
    :param frame_divider: decides by what number the trailer will be divided into frames
    :param trailer_path: the path of the trailer that will be divided
    :param dst_path: the path where the frames will be saved
    :return: none
    """
    cap = cv2.VideoCapture(trailer_path)
    count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            frame_path = Path(str(os.path.join(dst_path + 'frame_' + str(count) + '.jpg')))
            if not frame_path.is_file():  # if it doesnt exist already
                cv2.imwrite(dst_path + 'frame_' + str(count) + '.jpg', frame)
            count += frame_divider
            cap.set(cv2.CAP_PROP_POS_FRAMES, count)
        else:
            cap.release()
            break


def divide_frames_in_genre_dir(source_dir_path, dst_dir_path):
    """
    divides all the trailers of a certain genre into frames
    :param source_dir_path: the path to the dir with all the trailers of a certain genre
    :param dst_dir_path: the path where all the frames will be saved at
    :return: none
    """
    for filename in os.listdir(source_dir_path):
        (Path(dst_dir_path) / filename).mkdir(parents=True, exist_ok=False)
        # creating the dir for the frames of a certain trailer

        divide_into_frames(10,
                           source_dir_path + filename,
                           dst_dir_path + filename + "/")


def write_all_movies_into_tables(dir_path):
    """
    the function writes all the movies of the same genre into the frames table
    :param dir_path: the path to the dirs with all the movies of the same genre
    :return: none
    """
    net, ln = yolo_commands.configuration()
    for movie_dir in os.listdir(dir_path):
        # substring so we'll take only the movie name without the genre prefix
        table_related.writing_movie_frames_into_tables(net, ln, dir_path + movie_dir,
                                                       movie_dir[movie_dir.find("_") + 1:],
                                                       movie_dir[:movie_dir.find("_")])


if __name__ == '__main__':
    # divide_frames_in_dir("/home/magshimim/know_your_genre/trailers_dir/horror/",
    #                      "/home/magshimim/know_your_genre/frames_dir/horror_frames_dir/")
    # divide_frames_in_dir("/home/magshimim/know_your_genre/trailers_dir/action/",
    #                      "/home/magshimim/know_your_genre/frames_dir/action_frames_dir/")

    # table_related.create_frames_table().to_csv("/home/magshimim/know_your_genre/frames_table.csv",
    #                                            index=False)
    # table_related.create_features_table().to_csv("/home/magshimim/know_your_genre/features_table.csv",
    #                                              index=False)
    # write_all_movies_into_tables("/home/magshimim/know_your_genre/frames_dir/action_frames_dir/")
    # print("DONE WITH ACTION GENRE")
    # write_all_movies_into_tables("/home/magshimim/know_your_genre/frames_dir/horror_frames_dir/")
    """
    data = pd.read_csv("/home/magshimim/know_your_genre/features_table.csv")
    index_list = list(data)[5:17]
    print(index_list)
    data.drop(columns=index_list, axis=1, inplace=True)
    data.to_csv("/home/magshimim/know_your_genre/check.csv")
    """
    # table_related.append_genre_colors_to_csv("/home/magshimim/know_your_genre/frames_dir/action_frames_dir/")
    # print("DONE WITH ACTION")
    # table_related.append_genre_colors_to_csv("/home/magshimim/know_your_genre/frames_dir/horror_frames_dir/")

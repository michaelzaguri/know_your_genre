import pickle
import threading
import socket
import json
from pytube import YouTube
from pathlib import Path
import os
import moviepy.editor
import pandas as pd
import pro_server_uti
import yolo_commands
from PIL import Image
import numpy as np
import shutil
import time

"""
TO DO LIST:
1. add threads to the color extraction - Done also added lower res
2. made the model to run with the code - Done
3. add locks the the server code 
4. add threads to all of the feature extraction - sound like a bad idea bet we'll see
"""


CLASSES_DICT = ["avg_entropy", "person_avr_appear_count", "motorcycle_frames_percent", "airplane_frames_percent", "bus_frames_percent",
                    "train_frames_percent", "traffic light_frames_percent", "dog_frames_percent", "couch_frames_percent",
                    "tv_frames_percent", "black_1", "black_2", "black_3", "green_1", "orange", "gray"]
ALL_OBJECTS = ["person_avr_appear_count", "motorcycle_frames_percent", "airplane_frames_percent", "bus_frames_percent",
                    "train_frames_percent", "traffic light_frames_percent", "dog_frames_percent", "couch_frames_percent", "tv_frames_percent"]
ALL_COLORS = ["black_1", "black_2", "black_3", "green_1", "orange", "gray"]
classes_dict = {x: [] for x in CLASSES_DICT}
NUM_OF_THREADS = 5
MODEL_FILE_NAME = "finalized_model.sav"
NUM_OF_COLORS = 6


class server:
    __server_ip = '127.0.0.1'
    __server_port = 2811
    __stats_dict = {}

    def start_connection(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', self.__server_port))
        print("socket binded to port", self.__server_port)
        s.listen()
        print("socket is listening")
        while True:
            # establish connection with client
            client_socket, client_address = s.accept()
            print('Connected to :', client_address[0], ':', client_address[1])
            __stats_df = pd.DataFrame(data=classes_dict)
            self.__stats_dict[client_address[1]] = pd.DataFrame(data=classes_dict)
            self.__stats_dict[client_address[1]].append(classes_dict, ignore_index=True)  # the info dict for every client
            print(self.__stats_dict)
            t1 = threading.Thread(target=self.__client_handler, args=(client_socket, client_address,), daemon=True)
            t1.start()

    def __client_handler(self, client_socket, client_address):
        """
        handle all the client requests
        :param client_socket: the socket that connected to the client
        :param client_address: all the info about the connection
        :return: None
        """
        try:
            while True:
                data = client_socket.recv(40)
                if not data:
                    raise
                data = data.decode("utf-8")
                code = data[:8]  # getting the msg code
                msg_len = data[8:]  # getting the msg total size
                msg_len = int(msg_len, 2)  # converting the total size from binary to int
                msg_len = msg_len + (8 - msg_len % 8)  # round it to a number that is divided by 8
                if code == "00000001":
                    data = client_socket.recv(msg_len)  # getting the actual msg
                    data = data.decode("utf-8")
                    start_time = time.time()  # start the counting of time
                    json_str = self.__convert_to_json(data)
                    vid_path = self.__download_vid(json_str["youtubePath"], client_address)
                    if vid_path == "":
                        json_res = {"error_code": "wrong video link, "
                                                 "you could copy it like a normal person but you "
                                                 "decided to copy it by hand, or did you tried to troll us??"}
                        # making good to send to the client by protocol
                        respond = '00000000' + '{0:b}'.format(len(json.dumps(json_res)) * 8).zfill(32) +  \
                        (''.join(format(ord(i), '08b') for i in json.dumps(json_res))).zfill(len(json.dumps(json_res)) * 8)
                        client_socket.send(respond.encode())
                    else:
                        vid_dir_path = Path(vid_path[0:-4])  # to remove the .mp4 end
                        vid_dir_path.mkdir(parents=True, exist_ok=False)
                        low_res_dir_path = Path("low_res_" + str(vid_dir_path))
                        low_res_dir_path.mkdir(parents=True, exist_ok=False)
                        self.__save_all_frames(vid_path, vid_dir_path, json_str["frameSector"])
                        self.__get_objects_in_frames(vid_dir_path, client_address)
                        print("finished objects " + str(time.time() - start_time))
                        self.__get_antropy(vid_dir_path, client_address)
                        print("finished entropy " + str(time.time() - start_time))
                        self.__get_all_colors(low_res_dir_path, client_address)
                        print("finished colors")
                        print("end time is " + str(time.time() - start_time))
                        os.remove(str(vid_path))
                        shutil.rmtree(vid_dir_path)
                        shutil.rmtree(low_res_dir_path)
                        result = self.__predict_genre(client_address)
                        json_res = {"actionPrediction": float(result), "horrorPrediction": float(1-result)}
                        respond = '00000011' + '{0:b}'.format(len(json.dumps(json_res)) * 8).zfill(32) +  \
                        (''.join(format(ord(i), '08b') for i in json.dumps(json_res))).zfill(len(json.dumps(json_res)) * 8)
                        client_socket.send(respond.encode())
        except:
            client_socket.close()

    def __convert_to_json(self, data):
        """
        convert binary data to json
        :param data: data to translate
        :return: the json string
        """
        data = [data[index: index + 8] for index in range(0, len(data), 8)]
        json_string = ''.join(chr(int(x, 2)) for x in data)
        json_string = json.loads(json_string)
        return json_string

    def __download_vid(self, link, client_address):
        """
        download YouTube video from link
        :param link: the link to the YouTube video
        :param client_address: the info about the connection to the client for easy space management
        :return: the name that the video is saved on
        """
        try:
            name_to_save = "video_" + str(client_address[1]) + ".mp4"
            url = YouTube(link)
            video = url.streams.get_highest_resolution()
            video.download(filename=name_to_save)
            return name_to_save
        except:
            return ""

    def __save_all_frames(self, video_path, dir_video_path, frame_jump):
        """
        save every tenth frame in the video to an original res dir and low res dir
        :param video_path: the path to the video that all the frames will be taken from
        :param dir_video_path: the dir that the frame will be saved on(the low res frames will be saved on
        "low_res_" + the same name
        :param frame_jump: the jump between frames (client choice)
        :return: None
        """
        trailer_name = video_path
        clip = moviepy.editor.VideoFileClip(trailer_name)
        count = 0
        frame_num = 0
        time_gap = clip.duration / (clip.reader.nframes / frame_jump)
        for i in range(int(clip.reader.nframes / frame_jump)):
            image_path = Path(dir_video_path)/('frame_' + str(frame_num) + '.jpg')
            clip.save_frame(image_path, count)
            image_file = Image.open(image_path)
            image_file.save("low_res_" + str(image_path), quality=1)  # it will round all the color and make the color extraction faster to run
            frame_num += 10  # just for the name of it
            count += time_gap
        clip.close()

    def __get_all_colors(self, dir_path, client_address):
        """
        extract all the frames from the video
        :param dir_path: the path of the dir to take the frames from
        :param client_address: for an easier saving of the data
        :return: None
        """
        color_total_counts = [0]*NUM_OF_COLORS
        color_count_list = [[0]*NUM_OF_COLORS]*NUM_OF_THREADS
        threads = [None]*NUM_OF_THREADS
        start = 0
        end = int((len(os.listdir(dir_path)))/NUM_OF_THREADS)
        step = end
        for i in range(len(threads)):  # starting all the threads
            threads[i] = threading.Thread(target=self.__extract_colors_from_a_section_of_frames,
                                  args=(dir_path, start, end, color_count_list, i))
            threads[i].start()
            start = end + 1
            end += step
            if i == NUM_OF_THREADS - 2:  # for any case that the jumping doesn't round to the number of frames
                end = len(os.listdir(dir_path)) - 1

        color_total_counts = np.array(color_total_counts)  # had to switch to np array because in a list I can't add only the values of 2 lists
        for i in range(len(threads)):  # waiting for the threads
            threads[i].join()
            color_total_counts = color_total_counts + np.array(color_count_list[i])
        color_total_counts = color_total_counts.tolist()  # switching back to list
        color_list_in_vid = pro_server_uti.create_colors_record(color_total_counts, len(os.listdir(dir_path)))
        count = 0
        for color in ALL_COLORS:
            self.__stats_dict[client_address[1]].loc[1, color] = color_list_in_vid[count]
            count += 1

    def __get_objects_in_frames(self, dir_path, client_address):
        """
        get all the objects from the video and the stats related to them
        :param dir_path: the path of the dir to take the frames from
        :param client_address: for an easier saving of the data
        :return: None
        """
        frames_obj_count = {x: 0 for x in ALL_OBJECTS[1:]}
        total_obj_appear = {"person_avr_appear_count": 0}
        net, ln = yolo_commands.configuration()
        for img in os.listdir(dir_path):
            frame_path = Path(dir_path)/img
            classes = yolo_commands.getting_objects_from_picture(net, ln, str(frame_path))
            pro_server_uti.update_object_counts(frames_obj_count, total_obj_appear, classes)
        object_list_in_vid = pro_server_uti.create_objects_record(frames_obj_count, total_obj_appear, len(os.listdir(dir_path)))
        count = 0
        for object in ALL_OBJECTS:
            self.__stats_dict[client_address[1]].loc[1, object] = object_list_in_vid[count]
            count += 1

    def __get_antropy(self, dir_path, client_address):
        """
        get the avg entropy in the video
        :param dir_path: the path of the dir to take the frames from
        :param client_address: for an easier saving of the data
        :return: None
        """
        total_entropy = 0
        for img in os.listdir(dir_path):
            frame_path = Path(dir_path)/img
            entropy = pro_server_uti.get_image_entropy(frame_path)
            total_entropy += entropy
        self.__stats_dict[client_address[1]].loc[1, "avg_entropy"] = total_entropy/len(os.listdir(dir_path))

    def __extract_colors_from_a_section_of_frames(self, dir_path, start, end, color_count_list, index):
        """
        get all the colors from a section of frames
        :param dir_path: the path of the dir to take the frames from
        :param start: the start of the section
        :param end: the end of the section
        :param color_count_list: a dict to save all the percents of colors
        :param index: the index the info will be saved on
        :return: None
        """
        color_total_counts = [0]*NUM_OF_COLORS
        for frame_num in range(start, end + 1):
            frame_path = Path(dir_path)/("frame_" + str(frame_num * 10) + ".jpg")
            colors = list(pro_server_uti.get_most_close_color(frame_path).values())
            pro_server_uti.update_color_counts(color_total_counts, colors)
        print("end " + str(index))
        color_count_list[index] = color_total_counts

    def __get_objects_from_a_section_of_frames(self, dir_path, start, end, net, ln, frames_obj_count, total_obj_appear, index):
        """
        no use for now
        :param dir_path:
        :param start:
        :param end:
        :param net:
        :param ln:
        :param frames_obj_count:
        :param total_obj_appear:
        :param index:
        :return:
        """
        for frame_num in range(start, end + 1):
            frame_path = Path(dir_path)/("frame_" + str(frame_num * 10) + ".jpg")
            classes = yolo_commands.getting_objects_from_picture(net, ln, str(frame_path))
            pro_server_uti.update_object_counts(frames_obj_count[index], total_obj_appear[index], classes)
        print("end " + str(index))

    def __predict_genre(self, client_address):
        """
        predict the genre of the trailer
        :param client_address: to get only the data of the connected client
        :return: the result of the prediction
        """
        loaded_model = pickle.load(open(MODEL_FILE_NAME, 'rb'))  # loading the model
        result = loaded_model.predict(self.__stats_dict[client_address[1]])
        return result


server1 = server()
server1.start_connection()

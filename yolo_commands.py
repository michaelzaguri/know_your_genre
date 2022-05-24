import cv2 as cv
import numpy as np


classes_count = 80


def getting_objects_from_picture(net, ln, img_path):
    """
    the function is getting the a path to an image and return a dict with all of the objects that are in the image
    :param net: a configuration var that is needed to ran the yolo algorithm
    :param ln: a configuration var that is needed to ran the yolo algorithm
    :param img_path: the path to the image that the function will get all the objects from
    :return: a dict with all of the objects that are in the image
    """
    classes_in_pic = []
    boxes = []
    confidences = []
    class_ids = []
    img = cv.imread(img_path)
    h, w = img.shape[:2]
    blob = cv.dnn.blobFromImage(img, 1 / 255.0, (416, 416), swapRB=True, crop=False)  # construct a blob from the image
    net.setInput(blob)
    outputs = net.forward(ln)

    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                box = detection[:4] * np.array([w, h, w, h])
                (centerX, centerY, width, height) = box.astype("int")
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))
                box = [x, y, int(width), int(height)]
                boxes.append(box)
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indices = cv.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    if len(indices) > 0:
        for i in indices.flatten():
            # here we appended all of the objects that are in the pictures (only their types)
            classes_in_pic.append(class_ids[i])

    # returning a dictionary with the classes as keys and their number of appearances as values
    return fill_classes_count(
        dict((object_class, classes_in_pic.count(object_class)) for object_class in set(classes_in_pic)))


def fill_classes_count(classes_count_dict):
    """
    fill the a given dict with 0 where there is no value
    :param classes_count_dict: a dict to fill
    :return: a filled dict
    """
    for class_id in range(classes_count):
        if class_id not in classes_count_dict:
            classes_count_dict[class_id] = 0
    return classes_count_dict


def configuration():
    """
    configure all the needed stuff to run yolo
    :return: a tuple with values from the configuration
    """
    np.random.seed(42)
    # Give the configuration and weight files for the model and load the network.
    net = cv.dnn.readNetFromDarknet('yolo\\yolov3.cfg', 'yolo\\yolov3.weights')
    net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
    # determine the output layer
    ln = net.getLayerNames()
    ln = [ln[i - 1] for i in net.getUnconnectedOutLayers()]
    params = (net, ln)
    return params


from flask import Flask, render_template, url_for, request
import sqlite3
import shutil
import os
import sys
import cv2  # working with, mainly resizing, images
import numpy as np  # dealing with arrays
import os  # dealing with directories
from random import shuffle  # mixing up or currently ordered data that might lead our network astray in training.
from tqdm import \
    tqdm  # a nice pretty percentage bar for tasks. Thanks to viewer Daniel BA1/4hler for this suggestion
import tflearn
from tflearn.layers.conv import conv_2d, max_pool_2d
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression
import tensorflow as tf

connection = sqlite3.connect('user_data.db')
cursor = connection.cursor()

command = """CREATE TABLE IF NOT EXISTS user(name TEXT, password TEXT, mobile TEXT, email TEXT)"""
cursor.execute(command)

command = """CREATE TABLE IF NOT EXISTS seller(Id INTEGER PRIMARY KEY AUTOINCREMENT, crop TEXT, cost TEXT, district TEXT, image BLOB)"""
cursor.execute(command)

command = """CREATE TABLE IF NOT EXISTS buyer(Id INTEGER PRIMARY KEY AUTOINCREMENT, crop TEXT, cost TEXT, district TEXT, image BLOB)"""
cursor.execute(command)

def Analyse(image):
    IMG_SIZE = 50
    LR = 1e-3
    MODEL_NAME = 'HEMMORRHAGE-{}-{}.model'.format(LR, '2conv-basic')

    def process_verify_data():
        verifying_data = []
        path = 'static/test/cnn/'+image
        img_num = image.split('.')[0]
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
        verifying_data.append([np.array(img), img_num])
        np.save('verify_data.npy', verifying_data)
        return verifying_data

    verify_data = process_verify_data()
    #verify_data = np.load('verify_data.npy')

    
    tf.compat.v1.reset_default_graph()
    #tf.reset_default_graph()

    convnet = input_data(shape=[None, IMG_SIZE, IMG_SIZE, 3], name='input')

    convnet = conv_2d(convnet, 32, 3, activation='relu')
    convnet = max_pool_2d(convnet, 3)

    convnet = conv_2d(convnet, 64, 3, activation='relu')
    convnet = max_pool_2d(convnet, 3)

    convnet = conv_2d(convnet, 128, 3, activation='relu')
    convnet = max_pool_2d(convnet, 3)

    convnet = conv_2d(convnet, 32, 3, activation='relu')
    convnet = max_pool_2d(convnet, 3)

    convnet = conv_2d(convnet, 64, 3, activation='relu')
    convnet = max_pool_2d(convnet, 3)

    convnet = fully_connected(convnet, 1024, activation='relu')
    convnet = dropout(convnet, 0.8)

    convnet = fully_connected(convnet, 2, activation='softmax')
    convnet = regression(convnet, optimizer='adam', learning_rate=LR, loss='categorical_crossentropy', name='targets')

    model = tflearn.DNN(convnet, tensorboard_dir='log')

    if os.path.exists('{}.meta'.format(MODEL_NAME)):
        model.load(MODEL_NAME)
        print('model loaded!')

    for num, data in enumerate(verify_data):

        img_num = data[1]
        img_data = data[0]

        # y = fig.add_subplot(3, 4, num + 1)
        orig = img_data
        data = img_data.reshape(IMG_SIZE, IMG_SIZE, 3)
        # model_out = model.predict([data])[0]
        model_out = model.predict([data])[0]
        print(model_out)
        print('model {}'.format(np.argmax(model_out)))

        res="The predicted result with the probability of : {}".format(model_out[np.argmax(model_out)]*100)
    return np.argmax(model_out),res


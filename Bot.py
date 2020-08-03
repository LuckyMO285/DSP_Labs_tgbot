import os
import glob
import subprocess

import cv2
import numpy as np

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

class FFmpeg:
    def __init__(self, cmds_path):
        self.cmds = cmds_path

    def ogg_wav(self, file):
        if file.endswith('ogg'):
            output = file[:-4] + ".wav"
            p = subprocess.Popen(self.cmds + " -i " + file + " -ar 16000 " + output) 
            p.communicate()

updater = Updater(token='set_your_token', use_context=True)
dispatcher = updater.dispatcher

def voice_message(update, context):
    file = context.bot.get_file(update.message.voice.file_id) # get voice message file_id
    user_id = update.effective_chat.id # get user_id
    directory = 'path_to_save_Voice_Messages\\{}'.format(user_id) #directory to save file
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_num = len(glob.glob(directory + '\\audio_message_*.ogg')) # number of audio_message_* files
    file.download(directory + '\\audio_message_{}.ogg'.format(file_num))
    context.bot.send_message(chat_id=update.effective_chat.id, text='The file is saved in .ogg format')

    ffmpeg_class = FFmpeg('path_to_ffmpeg.exe')
    ffmpeg_class.ogg_wav(directory + '\\audio_message_{}.ogg'.format(file_num))
    context.bot.send_message(chat_id=update.effective_chat.id, text='The file is saved in .wav format with 16KHz sample rate')
    
voice_handler = MessageHandler(Filters.voice & (~Filters.command), voice_message)
dispatcher.add_handler(voice_handler)

def check_face(context, user_id, file_path):
    imagePath = file_path
    cascPath = "haarcascade_frontalface_default.xml"

    # Create the haar cascade
    faceCascade = cv2.CascadeClassifier(cascPath)

    # Read the image
    image = cv2.imread(imagePath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags = cv2.CASCADE_SCALE_IMAGE
    )
    if len(faces) > 0:
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        new_file_path = file_path[:-4] + '_faces.jpg'
        cv2.imwrite(new_file_path, image)
        context.bot.send_message(chat_id=user_id, text='I found {} faces'.format(len(faces)))
        context.bot.send_photo(chat_id=user_id, photo=open(new_file_path, 'rb'))
        os.remove(new_file_path)
    else:
        context.bot.send_message(chat_id=user_id, text='I have not found faces')
        os.remove(file_path)

def image_message(update, context):
    file = context.bot.get_file(update.message.photo[-1].file_id)
    user_id = update.effective_chat.id
    directory = 'path_to_save_Image_Messages\\{}'.format(user_id)
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_num = len(glob.glob(directory + '\\photo_message_*.jpg'))
    file.download(directory + '\\photo_message_{}.jpg'.format(file_num))
    check_face(context, user_id, directory + '\\photo_message_{}.jpg'.format(file_num))

face_handler = MessageHandler(Filters.photo & (~Filters.command), image_message)
dispatcher.add_handler(face_handler)

def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=
                             "I am a bot that can:\n" \
                             "1. Save audio messages from a dialogue to disk by user IDs.\n" \
                             "2. Convert all audio messages to wav format with a sampling rate of 16 kHz.\n" \
                             "3. Determine whether there is a face in the sent photos or not. I keep only those where it is.\n\n" \
                             "When a voice message is sent, it will be automatically saved in two extensions in the following format:\n" \
                             "uid -> [audio_message_0, audio_message_1, ..., audio_message_N].\n\n" \
                             "After the image is sent, it will be scanned for faces. If they are not there, the message \"I have not found faces\" will be returned. " \
                             "Otherwise, the number of faces and the image with their detection will be returned.")

help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I don't understand that command.")

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

updater.start_polling()



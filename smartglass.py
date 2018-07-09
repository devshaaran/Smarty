import os.path
from demo_opts import get_device
from PIL import Image, ImageSequence, ImageFont
from luma.core.sprite_system import framerate_regulator
import RPi.GPIO as GPIO
import picamera
import random as rand
import io
import face_recognition
import numpy as np
from luma.core.virtual import viewport
from luma.core.render import canvas
import urllib.request, json
from bs4 import BeautifulSoup
from nltk import word_tokenize
from time import sleep
from cv2 import imread, putText, imwrite, FONT_HERSHEY_COMPLEX
import math
import datetime
import argparse
from google.cloud import translate
from google.cloud import vision
import six
import re
from google.cloud import storage
from google.protobuf import json_format
from os import environ
import multiprocessing

cn1 = 33
cn2 = 35
cn3 = 37
GPIO.setmode(GPIO.BOARD)

# PIN 7 AND 3.3V
# normally 0 when connected 1
GPIO.setup(cn1, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(cn2, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(cn3, GPIO.IN, GPIO.PUD_UP)

environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/your/file/here.json"

def posn(angle, arm_length):
    dx = int(math.cos(math.radians(angle)) * arm_length)
    dy = int(math.sin(math.radians(angle)) * arm_length)
    return (dx, dy)


def clocky():
    today_last_time = "Unknown"
    while True:
        now = datetime.datetime.now()
        today_date = now.strftime("%d %b %y")
        today_time = now.strftime("%H:%M:%S")
        if today_time != today_last_time:
            today_last_time = today_time
            with canvas(device) as draw:
                now = datetime.datetime.now()
                today_date = now.strftime("%d %b %y")

                margin = 4

                cx = 30
                cy = min(device.height, 64) / 2

                left = cx - cy
                right = cx + cy

                hrs_angle = 270 + (30 * (now.hour + (now.minute / 60.0)))
                hrs = posn(hrs_angle, cy - margin - 7)

                min_angle = 270 + (6 * now.minute)
                mins = posn(min_angle, cy - margin - 2)

                sec_angle = 270 + (6 * now.second)
                secs = posn(sec_angle, cy - margin - 2)

                draw.ellipse((left + margin, margin, right - margin, min(device.height, 64) - margin), outline="white")
                draw.line((cx, cy, cx + hrs[0], cy + hrs[1]), fill="white")
                draw.line((cx, cy, cx + mins[0], cy + mins[1]), fill="white")
                draw.line((cx, cy, cx + secs[0], cy + secs[1]), fill="red")
                draw.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill="white", outline="white")
                draw.text((2 * (cx + margin), cy - 8), today_date, fill="yellow")
                draw.text((2 * (cx + margin), cy), today_time, fill="yellow")

        sleep(0.1)
        if GPIO.input(cn1) == 0:
            break


def show_dir_image(path, texts):
    while True:
        img = imread(path)
        putText(img, texts, (0, 13), FONT_HERSHEY_COMPLEX, 0.52, (0, 255, 0))
        imwrite('0.png', img)
        photo = Image.open('/home/pi/smart_glass-master/0.png')
        device.display(photo.convert(device.mode))
        sleep(2)


def show_dir_image_once(path, texts):
    img = imread(path)
    putText(img, texts, (0, 13), FONT_HERSHEY_COMPLEX, 0.52, (0, 255, 0))
    imwrite('0.png', img)
    photo = Image.open('/home/pi/smart_glass-master/0.png')
    device.display(photo.convert(device.mode))
    sleep(0.3)


def text_splitter(texter):
    virtual = viewport(device, width=device.width, height=768)
    lister_text = word_tokenize(texter)
    total_words = 0
    x = []
    blurb = ''
    for i in lister_text:
        number_words = len(i)
        total_words = number_words + total_words + 1
        if total_words <= 20:
            x.append(i)
        if total_words > 20:
            blurb = blurb + ' '.join(x) + ' ' + '\n'
            x = []
            total_words = 0 + number_words
            x.append(i)

    for _ in range(2):
        with canvas(virtual) as draw:
            for i, line in enumerate(blurb.split("\n")):
                draw.text((0, (i * 12)), text=line, fill="white")


def initiate_gif(img_path):
    regulator = framerate_regulator(fps=10)
    banana = Image.open(img_path)
    count = 0

    while count <= 10:
        for frame in ImageSequence.Iterator(banana):
            count += 2
            with regulator:
                background = Image.new("RGB", device.size, "white")
                background.paste(frame)
                device.display(background.convert(device.mode))
                print(count)


def weather_req():
    from firebase import firebase
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             'fonts', 'C&C Red Alert [INET].ttf'))
    font = ImageFont.truetype(font_path, 21)
    # Google Maps Ddirections API endpoin
    endpoint = 'http://api.openweathermap.org/data/2.5/forecast?'
    api_key = 'Your key'
    firebase = firebase.FirebaseApplication('https://smartglass-e01ec.firebaseio.com/', None)
    whole_direct = firebase.get('/directions', None)
    latt = whole_direct['latitude']
    long = whole_direct['longitude']
    # Asks the user to input Where they are and where they want to go.
    # Building the URL for the request
    nav_request = 'lat={}&lon={}&APPID={}'.format(latt, long, api_key)
    request = endpoint + nav_request
    # Sends the request and reads the response.
    response = urllib.request.urlopen(request).read().decode('utf-8')
    # Loads response as JSON
    weather = json.loads(response)
    current_temp = weather['list'][0]['main']['temp']
    temp_c = current_temp - 273.15
    temp_c_str = str(int(temp_c)) + '°C'
    descript_place = weather['list'][0]['weather'][0]['main']

    while True:
        with canvas(device) as draw:
            draw.text((40, 0), text=descript_place, font=font, fill="white")
            draw.text((49, 40), text=temp_c_str, font=font, fill="white")
        if GPIO.input(cn3) == 0:
            break


def show_image(img_path):
    photo = Image.open(img_path)

    # display on screen for a few seconds
    while True:
        device.display(photo.convert(device.mode))


        if GPIO.input(cn1) == 0:
            break
        if GPIO.input(cn2) == 0:
            global opener
            opener = True
            break


def camera_initiate():
    cameraResolution = (1024, 768)
    displayTime = 3

    # create the in-memory stream
    stream = io.BytesIO()

    with picamera.PiCamera() as camera:

        # set camera resolution
        camera.resolution = cameraResolution
        # print("Starting camera preview...")

        while True:

            camera.start_preview()
            if (GPIO.input(cn2) == 0):
                camera.capture(stream, format='jpeg', resize=device.size)
                camera.close()
                # "rewind" the stream to the beginning so we can read its content
                stream.seek(0)
                # print("Displaying photo for {0} seconds...".format(displayTime))
                # open photo
                photo = Image.open(stream)
                photo.save('home/' + str(rand.randint(0, 99999999)) + '.jpg')
                # display on screen for a few seconds
                device.display(photo.convert(device.mode))
                sleep(displayTime)
            if (GPIO.input(cn3) == 0):
                camera.close()
                break


def findwho_initiate():
    # Get a reference to the Raspberry Pi camera.
    # If this fails, make sure you have a camera connected to the RPi and that you
    # enabled your camera in raspi-config and rebooted first.
    camera = picamera.PiCamera()
    camera.resolution = (320, 240)
    output = np.empty((240, 320, 3), dtype=np.uint8)

    # Load a sample picture and learn how to recognize it.
    print("Loading known face image(s)")
    obama_image = face_recognition.load_image_file("obama_small.jpg")
    obama_face_encoding = face_recognition.face_encodings(obama_image)[0]
    shaaran = face_recognition.load_image_file("shaaran.jpg")
    shaaran_face_encoding = face_recognition.face_encodings(shaaran)[0]

    # Initialize some variables
    face_locations = []
    face_encodings = []

    while True:
        print("Capturing image.")
        # Grab a single frame of video from the RPi camera as a numpy array
        camera.capture(output, format="rgb")

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(output)
        print("Found {} faces in image.".format(len(face_locations)))
        face_encodings = face_recognition.face_encodings(output, face_locations)

        # Loop over each face found in the frame to see if it's someone we know.
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            match = face_recognition.compare_faces([obama_face_encoding, shaaran_face_encoding], face_encoding)
            name = "<Unknown Person>"

            if match[0]:
                name = "Barack Obama"

            if match[1]:
                name = "shaaran"

            virtual = viewport(device, width=device.width, height=768)

            for _ in range(2):
                with canvas(virtual) as draw:
                    draw.text((20, 12), name, fill="white")

            if (GPIO.input(cn3) == 0):
                break


def translate_text(target, text):
    # [START translate_translate_text]
    """Translates text into the target language.
    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    translate_client = translate.Client()

    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(
        text, target_language=target)

    #print(u'Text: {}'.format(result['input']))
    transer = result['translatedText']
    trans_text_returned = u'Translation: {}'.format(transer)
    return trans_text_returned

    #print(u'Detected source language: {}'.format(result['detectedSourceLanguage']))
    # [END translate_translate_text]

def detect_text(path):

    """Detects text in the file."""
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    print('Texts:')
    tog = texts[0].description
    received_translation = translate_text('en',tog)
    text_splitter(received_translation)

    while (GPIO.input(cn3) == 1):
        continue

def trans_initiate():
    cameraResolution = (1024, 768)
    displayTime = 3

    # create the in-memory stream
    stream = io.BytesIO()

    with picamera.PiCamera() as camera:

        # set camera resolution
        camera.resolution = cameraResolution
        # print("Starting camera preview...")

        while True:

            camera.start_preview()
            if (GPIO.input(cn2) == 0):
                camera.capture(stream, format='jpeg', resize=device.size)
                camera.close()
                # "rewind" the stream to the beginning so we can read its content
                stream.seek(0)
                # print("Displaying photo for {0} seconds...".format(displayTime))
                # open photo
                photo = Image.open(stream)
                photo.save('home/' + 'transy' + '.jpg')
                # display on screen for a few seconds
                device.display(photo.convert(device.mode))
                sleep(displayTime)
                detect_text('home/transy.jpg')

            if (GPIO.input(cn3) == 0):
                camera.close()
                break

def rec_initiate():
    virtual = viewport(device, width=device.width, height=768)

    for _ in range(2):
        with canvas(virtual) as draw:
            draw.text((0, 15), ' UNDER DEVOLOPMENT ', fill="white")

    if GPIO.input(cn3) == 1:
        while (GPIO.input(cn3) == 1):
            continue


def location_smart():
    from firebase import firebase
    # Google MapsDdirections API endpoint
    endpoint = 'https://maps.googleapis.com/maps/api/directions/json?'
    api_key = 'Your keys'
    firebase = firebase.FirebaseApplication('https://smartglass-e01ec.firebaseio.com/', None)
    virtual = viewport(device, width=device.width, height=768)

    for _ in range(2):
        with canvas(virtual) as draw:
            draw.text((0, 15), 'Are you sure you have ', fill="white")
            draw.text((0, 27), 'set the destination', fill="white")
            draw.text((0, 39), 'in the app?', fill="white")

    if GPIO.input(cn2) == 1:
        while (GPIO.input(cn2) == 1):
            continue

    while True:
        try:
            whole_direct = firebase.get('/directions', None)
            latt = whole_direct['latitude']
            long = whole_direct['longitude']
            latt_desti = whole_direct['desti_latitude']
            long_desti = whole_direct['desti_longitude']
            destination = (str(latt_desti) + ', ' + str(long_desti))
            start_destin = (str(latt) + ', ' + str(long))
            # Asks the user to input Where they are and where they want to go.
            origin = start_destin.replace(' ', '+')
            destination = (str(latt_desti) + ', ' + str(long_desti))
            destination = destination.replace(' ', '+')
            # Building the URL for the request
            nav_request = 'origin={}&destination={}&key={}'.format(origin, destination, api_key)
            request = endpoint + nav_request
            # Sends the request and reads the response.
            response = urllib.request.urlopen(request).read().decode('utf-8')
            # Loads response as JSON
            directions = json.loads(response)
            routes = directions['routes']
            legs = routes[0]['legs']
            # print(len(legs))
            first_step = legs[0]['steps']
            # print(len(first_step))
            instructions = first_step[0]['html_instructions']
            go_direction_1 = ''
            if len(first_step) > 1:
                instructions_1 = first_step[1]['html_instructions']
                soup_1 = BeautifulSoup(instructions_1, "html5lib")
                go_direction_1 = soup_1.get_text()

            distance = first_step[0]['distance']['text']
            soup = BeautifulSoup(instructions, "html5lib")
            go_direction = soup.get_text()
            conversion = distance.split(' ')
            org_distance = 0
            if conversion[1] == 'km':
                org_distance = float(conversion[0]) * 1000
            elif conversion[1] == 'm':
                org_distance = conversion[0]

            collector = word_tokenize(go_direction)
            # print(distance)
            # print(int(org_distance))

            main_way_list = go_direction.split('(')
            main_way = main_way_list[0]
            main_way_list1 = go_direction_1.split('(')
            main_way1 = main_way_list1[0]

            directions = ['north', 'northeast', 'northwest', 'straight', 'left', 'right']

            if int(org_distance) < 60:
                goway = []
                for d in main_way1:
                    for e in directions:
                        if d.lower() == e:
                            goway.append(d)

                if len(goway) == 0:
                    if len(first_step) > 1:

                        # text_splitter - param type
                        virtual = viewport(device, width=device.width, height=768)
                        lister_text = word_tokenize(go_direction_1)
                        total_words = 0
                        x = []
                        blurb = ''
                        for i in lister_text:
                            number_words = len(i)
                            total_words = number_words + total_words + 1
                            if total_words <= 20:
                                x.append(i)
                            if total_words > 20:
                                blurb = blurb + ' '.join(x) + ' ' + '\n'
                                x = []
                                total_words = 0 + number_words
                                x.append(i)

                        for _ in range(2):
                            with canvas(virtual) as draw:
                                draw.text((0, 0), 'turn in ' + str(org_distance) + ' m', fill="white")
                                for i, line in enumerate(blurb.split("\n")):
                                    draw.text((0, 12 + (i * 12)), text=line, fill="white")
                    else:

                        virtual = viewport(device, width=device.width, height=768)

                        for _ in range(2):
                            with canvas(virtual) as draw:
                                draw.text((0, 0), 'turn in ' + str(org_distance) + ' m', fill="white")
                                draw.text((0, 24), "Last leg hooray ! ", fill="white")


                else:
                    if len(first_step) > 1:
                        toggle_direction = goway[0]

                        if toggle_direction == 'north' or toggle_direction == 'straight':
                            show_dir_image_once('/home/pi/smart_glass-master/Images/straight_arrow.png',
                                                ('turn in ' + str(org_distance) + ' m'))
                        elif toggle_direction == 'northeast' or 'slight left' in go_direction_1 or 'slightly left' in go_direction_1 :
                            show_dir_image_once('/home/pi/smart_glass-master/Images/northeast_arrow.png',
                                                ('turn in ' + str(org_distance) + ' m'))
                        elif toggle_direction == 'northwest' or 'slight right' in go_direction_1 or 'slightly right' in go_direction_1:
                            show_dir_image_once('/home/pi/smart_glass-master/Images/northwest_arrow.png',
                                                ('turn in ' + str(org_distance) + ' m'))
                        elif toggle_direction == 'right':
                            show_dir_image_once('/home/pi/smart_glass-master/Images/right_arrow.png',
                                                ('turn in ' + str(org_distance) + ' m'))
                        elif toggle_direction == 'left':
                            show_dir_image_once('/home/pi/smart_glass-master/Images/left_arrow.png',
                                                ('turn in ' + str(org_distance) + ' m'))


                    else:

                        virtual = viewport(device, width=device.width, height=768)

                        for _ in range(2):
                            with canvas(virtual) as draw:
                                draw.text((0, 0), 'turn in ' + str(org_distance) + ' m', fill="white")
                                draw.text((0, 24), "Last leg hooray ! ", fill="white")


            else:

                show_dir_image_once('/home/pi/smart_glass-master/Images/straight_arrow.png',
                                    ('Go ' + str(org_distance) + ' m'))

            if GPIO.input(cn2) == 0:
                text_splitter(go_direction)

            if GPIO.input(cn3) == 0:
                break

        except Exception as e:
            print(e)


def main():
    global opener
    opener = False
    try:
        while True:
            # button_next = GPIO.input(cn1)
            # button_ok = GPIO.input(cn2)
            # button_back = GPIO.input(cn3)

            clocky()
            show_image('/home/pi/smart_glass-master/Images/transl.png')
            if opener == True:
                trans_initiate()
                opener = False
            else:
                initiate_gif('/home/pi/smart_glass-master/Images/transl2weather.gif')
            show_image('/home/pi/smart_glass-master/Images/weather.png')
            if opener == True:
                weather_req()
                opener = False
            else:
                initiate_gif('/home/pi/smart_glass-master/Images/weather2rec.gif')

            show_image('/home/pi/smart_glass-master/Images/recorder.png')
            if opener == True:
                rec_initiate()
                opener = False
            else:
                initiate_gif('/home/pi/smart_glass-master/Images/rec2cam.gif')

            show_image('/home/pi/smart_glass-master/Images/check_cam.png')
            if opener == True:
                camera_initiate()
                opener = False
            else:
                initiate_gif('/home/pi/smart_glass-master/Images/cam2findwho.gif')

            show_image('/home/pi/smart_glass-master/Images/find_who.png')
            if opener == True:
                findwho_initiate()
                opener = False
            else:
                initiate_gif('/home/pi/smart_glass-master/Images/findwho2loc.gif')

            show_image('/home/pi/smart_glass-master/Images/location.png')
            if opener == True:
                location_smart()
                opener = False

    except KeyboardInterrupt:
        GPIO.cleanup()


if __name__ == "__main__":
    try:
        device = get_device()
        main()
    except KeyboardInterrupt:
        pass

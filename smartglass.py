import os.path
from demo_opts import get_device
from PIL import Image, ImageSequence
from luma.core.sprite_system import framerate_regulator
import RPi.GPIO as GPIO
import picamera
import time
import random as rand
import io
import sys
import face_recognition
import numpy as np
from luma.core.virtual import viewport
from luma.core.render import canvas


cn1 = 7
cn2 = 8
cn3 = 10
GPIO.setmode(GPIO.BOARD)

# PIN 7 AND 3.3V
# normally 0 when connected 1
GPIO.setup(cn1, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(cn2, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(cn3, GPIO.IN, GPIO.PUD_DOWN)
opener = False



def initiate_gif(img_path):
    regulator = framerate_regulator(fps=10)
    banana = Image.open(img_path)
    size = [min(*device.size)] * 2
    posn = ((device.width - size[0]) // 2, device.height - size[1])
    count = 0

    while True:
        for frame in ImageSequence.Iterator(banana):
            count += 1
            with regulator:
                background = Image.new("RGB", device.size, "white")
                background.paste(frame.resize(size, resample=Image.LANCZOS), posn)
                device.display(background.convert(device.mode))
                time.sleep(1)
                print(count)

def show_image(img_path):
    photo = Image.open(img_path)

    # display on screen for a few seconds
    while True:
        device.display(photo.convert(device.mode))
        if GPIO.input(cn1) == 1:
            break
        if GPIO.input(cn2) == 1:
            opener = True
            break


def camera_inititate():

    cameraResolution = (1024, 768)
    displayTime = 3

    # create the in-memory stream
    stream = io.BytesIO()

    with picamera.PiCamera() as camera:

        # set camera resolution
        camera.resolution = cameraResolution
        #print("Starting camera preview...")

        while True:

            camera.start_preview()
            if (GPIO.input(cn2) == 1):
                camera.capture(stream, format='jpeg', resize=device.size)
                camera.close()
                # "rewind" the stream to the beginning so we can read its content
                stream.seek(0)
                #print("Displaying photo for {0} seconds...".format(displayTime))
                # open photo
                photo = Image.open(stream)
                photo.save('home/'+ str(rand.randint(0,99999999))+'.jpg')
                # display on screen for a few seconds
                device.display(photo.convert(device.mode))
                time.sleep(displayTime)
            if (GPIO.input(cn3) == 1):
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
            match = face_recognition.compare_faces([obama_face_encoding,shaaran_face_encoding], face_encoding)
            name = "<Unknown Person>"

            if match[0]:
                name = "Barack Obama"

            if match[1]:
                name = "shaaran"

            virtual = viewport(device, width=device.width, height=768)

            for _ in range(2):
                with canvas(virtual) as draw:
                    draw.text((20, 12), name , fill="white")

            if (GPIO.input(cn3) == 1):
                break


def main():
    try:
        while (True):
            button_next = GPIO.input(cn1)
            button_ok = GPIO.input(cn2)
            button_back = GPIO.input(cn3)
            initiate_gif('D:\Youtube\linkedin\smart glasses\\anim_gif\\camera_gif')
            show_image('D:\Youtube\linkedin\smart glasses\camera')
            if opener == True:
                camera_inititate()
                opener = False
            initiate_gif('D:\Youtube\linkedin\smart glasses\\anim_gif\\findwho_gif')
            show_image('D:\Youtube\linkedin\smart glasses\\findwho')
            if opener == True:
                findwho_initiate()
                opener = False

            #TODO bring in location and list







            time.sleep(1)
    except KeyboardInterrupt:
        GPIO.cleanup()

if __name__ == "__main__":
    try:
        device = get_device()
        main()
    except KeyboardInterrupt:
        pass
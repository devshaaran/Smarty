import cv2
import luma
import os
from demo_opts import get_device
from PIL import Image,ImageSequence


def main(path):
    while True:
        img = cv2.imread(path)
        texts = '52'
        cv2.putText(img,texts,(0,0),cv2.FONT_HERSHEY_COMPLEX,0.5,(0,255,0))
        cv2.imwrite('0.png',img)
        photo = Image.open('/home/pi/smart_glass-master/Images/0.png')
        device.display(photo.convert(device.mode))

if __name__ == '__main__':
    try:
        device = get_device()
        main()
    except KeyboardInterrupt :
        pass
    



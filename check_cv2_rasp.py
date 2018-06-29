from cv2 import imread , putText , imwrite , FONT_HERSHEY_COMPLEX
import luma
import os
from luma.core.sprite_system import framerate_regulator
from demo_opts import get_device
from PIL import Image,ImageSequence,ImageFont
import random
import time
from luma.core.render import canvas
from luma.core.virtual import viewport


def main(path):
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                            'fonts', 'C&C Red Alert [INET].ttf'))
    font = ImageFont.truetype(font_path, 16)
    while True:
        img = imread(path)
        texts = str(random.randint(0,3000))
        putText(img,texts,(0,13),FONT_HERSHEY_COMPLEX,0.52,(0,255,0))
        imwrite('0.png',img)
        photo = Image.open('/home/pi/smart_glass-master/0.png')
        device.display(photo.convert(device.mode))
        virtual = viewport(device, width=device.width, height=768)
        time.sleep(2)
        
        textss = """
take the first right
thyen take the seconf
in 15 ,mins and then
yusdjdh you can
enjoy the view
                """
        

        for _ in range(2):
            with canvas(virtual) as draw:
                for i, line in enumerate(textss.split("\n")):
                    draw.text((0,(i * 12)), text=line, fill="white")

        time.sleep(2)

        # update the viewport one position below, causing a refresh,
        # giving a rolling up scroll effect when done repeatedly
        
            
if __name__ == '__main__':
    try:
        device = get_device()
        main('/home/pi/smart_glass-master/Images/check_cam_000.png')
    except KeyboardInterrupt :
        pass

# Python OCR
# Usage: python ocr.py -i "path to image"
# Flags: "-i, --input" (location of input image to be OCR'd)
#        "-m, --method" (Type of preprocessing: thresh or blur. Default: thresh)
# Required: sudo apt-get install tesseract-ocr
#           pytesseract, opencv-python, pillow


from PIL import Image
import pytesseract
import argparse
import cv2
import os
import shortuuid
from pathlib import Path


cwd = Path.cwd()
staticpath = Path.joinpath(cwd, 'static')
imgs = Path.joinpath(staticpath, 'img')
processed = Path.joinpath(imgs, 'processed')
textpath = Path.joinpath(cwd, 'text')
#pytesseract.pytesseract.tesseract_cmd = """C:\\Users\\bilawal.riaz\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe"""
#ap = argparse.ArgumentParser()
#ap.add_argument("-i", "--image", required=True, help="Path to input image")
#ap.add_argument("-m", "--method", type=str, default="thresh", help="Type of preprocessing to be applied. Thresh or blur")
#args = vars(ap.parse_args())

def gettext(imagepath, arg, uuid):
    
    image = cv2.imread(imagepath) # read image file
    gray1 = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # create grayscale version
    
    if arg == "threshold":
        gray = cv2.threshold(gray1, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1] # preprocess using threshold

    elif arg == "blur":
        gray = cv2.medianBlur(gray1,3)

    filename = str(Path.joinpath(processed, "{}.png".format(uuid))) # our processed image filename
    cv2.imwrite(filename, gray) # write the grayscale version to disk

    text = pytesseract.image_to_string(Image.open(Path.joinpath(processed, filename))) # extract text from grayscale processed image
    #os.remove(filename) # remove processed image
    print("OCR'd text:")
    print("------ Start of OCR ------")
    print(text)
    print("------ End of OCR ------")
    txtname = str("{}.txt".format(uuid))
    with open(Path.joinpath(textpath, txtname), 'w') as textfile:
        textfile.write(text) # write OCR'd output to textfile
        textfile.close()

    print("Saved {}.txt to disk".format(uuid))
    return (text, uuid)

#cv2.imshow("Image", image)
#cv2.imshow("Output", gray)
#cv2.waitKey(0)
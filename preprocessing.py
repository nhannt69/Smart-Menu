"""
Input: image
Output: image preprocessed

Rotate -> Inverted image -> Grayscale (Binarization) -> Noise removal
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt


#displaying-different-images-with-actual-size-in-matplotlib-subplot
def display(im_data):
    dpi = 80
  
    height, width  = im_data.shape[:2]
    
    # What size does the figure need to be in inches to fit the image?
    figsize = width / float(dpi), height / float(dpi)

    # Create a figure of the right size with one axes that takes up the full figure
    fig = plt.figure(figsize=figsize)
    ax = fig.add_axes([0, 0, 1, 1])

    # Hide spines, ticks, etc.
    ax.axis('off')

    # Display the image.
    ax.imshow(im_data, cmap='gray')

    plt.show()

def getSkewAngle(cvImage) -> float:
    # Prep image, copy, convert to gray scale, blur, and threshold
    newImage = cvImage.copy()
    gray = cv2.cvtColor(newImage, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9, 9), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Apply dilate to merge text into meaningful lines/paragraphs.
    # Use larger kernel on X axis to merge characters into single line, cancelling out any spaces.
    # But use smaller kernel on Y axis to separate between different blocks of text
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
    dilate = cv2.dilate(thresh, kernel, iterations=2)

    # Find all contours
    contours, hierarchy = cv2.findContours(dilate, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key = cv2.contourArea, reverse = True)
    for c in contours:
        rect = cv2.boundingRect(c)
        x,y,w,h = rect
        cv2.rectangle(newImage,(x,y),(x+w,y+h),(0,255,0),2)

    # Find largest contour and surround in min area box
    largestContour = contours[0]
    print (len(contours))
    minAreaRect = cv2.minAreaRect(largestContour)
    cv2.imwrite("test/boxes.jpg", newImage)
    # Determine the angle. Convert it to the value that was originally used to obtain skewed image
    angle = minAreaRect[-1]
    if angle < -45:
        angle = 90 + angle
    return -1.0 * angle

# Rotate the image around its center
def rotateImage(cvImage, angle: float):
    newImage = cvImage.copy()
    (h, w) = newImage.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    newImage = cv2.warpAffine(newImage, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return newImage

def deskew(cvImage):
    angle = getSkewAngle(cvImage)
    return rotateImage(cvImage, -1.0 * angle)

def inverted_img(img):
    """
    inverted image
    """
    return cv2.bitwise_not(img)

def grayscale(img):
    """
    grayscale image
    """
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def binary_image(img):
    """threadhold for image"""
    img = cv2.medianBlur(img, (3 , 3))
    img = cv2.medianBlur(img, (52, 52))
    img = np.divide()
    return cv2.threshold(img, 150, 200, (cv2.THRESH_BINARY, cv2.THRESH_OTSU))

def noise_removal(image):
    """
    discrease noise into image
    """
    kernel = np.ones((1, 1), np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    kernel = np.ones((1, 1), np.uint8)
    image = cv2.erode(image, kernel, iterations=1)
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    image = cv2.medianBlur(image, 3)
    return (image)

def thin_font(image):
    """
    thin font text into image
    """
    image = cv2.bitwise_not(image)
    kernel = np.ones((2,2),np.uint8)
    image = cv2.erode(image, kernel, iterations=1)
    image = cv2.bitwise_not(image)
    return (image)
    
def thick_font(image):
    """
    thick font text into image
    """
    image = cv2.bitwise_not(image)
    kernel = np.ones((2,2),np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    image = cv2.bitwise_not(image)
    return (image) 

def remove_borders(image):
    """
    remove border image - test
    """
    contours, heiarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cntsSorted = sorted(contours, key=lambda x:cv2.contourArea(x))
    cnt = cntsSorted[-1]
    x, y, w, h = cv2.boundingRect(cnt)
    crop = image[y:y+h, x:x+w]
    return (crop)


def preprocessing_menu(image_path):
    path = "temp/img_processing.png"

    img = cv2.imread(image_path)

    # img_resize = cv2.resize(img.copy(), (960, 700)) #1654.1634615384614 and 1208.5

    img_grayscale = grayscale(img)

    # img_noise_remove = noise_removal(img_grayscale)

    cv2.imwrite(path, img_grayscale)

    return path

def preprocessing_image(img_path):

    img = cv2.imread(img_path)
    # img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)

    #convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # gray = cv2.multiply(gray, 1.5)
    
    #blur remove noise
    blured1 = cv2.medianBlur(gray,3)
    blured2 = cv2.medianBlur(gray,81)
    divided = np.ma.divide(blured1, blured2).data
    normed = np.uint8(255*divided/divided.max())   
    
    path = "temp/img_processing.png"
    #Threshold image
    th, threshold = cv2.threshold(normed, 100, 255, cv2.THRESH_OTSU )

    #test
    img_temp = threshold.copy()
    # img_thin_font = thick_font(img_temp)
    img_remove_noise = noise_removal(img_temp)

    cv2.imwrite(path, img_remove_noise)

    return path



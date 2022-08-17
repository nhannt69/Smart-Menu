from preprocessing import preprocessing_image, preprocessing_menu
import cv2

img_path = preprocessing_image("preprocessing_image/001.jpeg")
img = cv2.imread(img_path)
cv2.imshow('test', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
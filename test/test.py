import os

_, _, files = next(os.walk("preprocessing/preprocessing_image"))
file_count = len(files)

print(file_count)
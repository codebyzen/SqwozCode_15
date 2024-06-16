import cv2
import easyocr
import re

# выделяем текст с кадров
def process(frame):

	# загружаем изображение
	img = cv2.imread(frame)

	# распознаем текст
	reader = easyocr.Reader(['ru'], gpu=False)
	text = reader.readtext(img)

	# симтим от мусора
	cleaned_string = re.sub(r'[^\u0410-\u044F\s\da-zA-Z-]', '', ' '.join([t[1] for t in text]))

	return cleaned_string

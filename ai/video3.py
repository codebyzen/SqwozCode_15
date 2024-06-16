from transformers import BlipProcessor, BlipForConditionalGeneration
import time
import os

from ai import translate
from ai import video_describe
from ai import video_prepare
from ai import text_processing
from ai import structures
from ai import audio_assemble

# определяем процессор для выделения объектов на видео
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
# задаем модель
model_img = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")


def video_blip_large(tmp_path, user_uuid, filename):
	start_time = time.time()

	# генерим пути к файлам
	file_path = os.path.join(tmp_path, user_uuid, filename)
	work_path = os.path.join(tmp_path, user_uuid, "video", )

	if not os.path.isdir(work_path):
		os.makedirs(work_path, exist_ok=True)

	# выделяем кадры и длительность видео
	images, duration = video_prepare.process(file_path, work_path)

	# описываем объекты на кадрах в видео
	text = " ".join([video_describe.process(img_name, processor, model_img) for img_name in images])

	# строим объект с результатами
	result = structures.ResultObject(
		model="Blip large",
		time=0,
		text=text,
		text_ru=translate.trans_en_ru(text)[0],
		text_ocr=text_processing.process(images[0]),
		text_nouns=' '.join(audio_assemble.extract_proper_nouns(text))
	)

	result.time = time.time() - start_time

	return [result, duration]

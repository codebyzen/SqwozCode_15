from PIL import Image


# выделяем объекты с кадра
def process(frame, processor, model_img):
	
	# загружаем изображение
	raw_image = Image.open(frame).convert('RGB')

	# выделяем объекты
	inputs = processor(raw_image, return_tensors="pt")
	out = model_img.generate(**inputs, max_new_tokens=25)
	description = processor.decode(out[0], skip_special_tokens=True)
	return description

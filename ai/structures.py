
# структуры для данных обработки

class ResultObject:
	def __init__(self, model, time, text=None, text_ru=None, text_ocr=None, text_nouns=None):
		self.model = model
		self.time = time
		self.text = text  # видео - текст на англ., аудио - текст на языке оригинала
		self.text_ru = text_ru  # видео переведенный текст объектов с видео
		self.text_ocr = text_ocr  # видео - текст на языке оригинала
		self.text_nouns = text_nouns


class FullResult:
	def __init__(self, url, text, duration, audio, video):
		self.url = url
		self.text = text
		self.duration = duration
		self.audio = audio
		self.video = video


# Функция для сериализации объектов в JSON
def custom_serializer(obj):
	if isinstance(obj, ResultObject):
		return {
			'model': obj.model,
			'time': obj.time,
			'text': obj.text,
			'text_ru': obj.text_ru,
			'text_ocr': obj.text_ocr,
			'text_nouns': obj.text_nouns
		}
	elif isinstance(obj, FullResult):
		return {
			'url': obj.url,
			'text': obj.text,
			'duration': obj.duration,
			'audio': obj.audio,
			'video': obj.video
		}
	else:
		raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

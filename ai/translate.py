from transformers import MarianMTModel, MarianTokenizer  # OPUS

# переводчик
def trans_ru_en(text):
	# Загрузка токенизатора и модели
	model_name = 'Helsinki-NLP/opus-mt-ru-en'
	tokenizer = MarianTokenizer.from_pretrained(model_name)
	model = MarianMTModel.from_pretrained(model_name)

	# Токенизация текста
	inputs = tokenizer(text, return_tensors="pt", padding=True)

	# Генерация перевода
	translated = model.generate(**inputs)

	# Декодирование переведенного текста
	translated_text = [tokenizer.decode(t, skip_special_tokens=True) for t in translated]
	return translated_text

# переводчик
def trans_en_ru(text):
	# Загрузка токенизатора и модели
	model_name = 'Helsinki-NLP/opus-mt-en-ru'
	tokenizer = MarianTokenizer.from_pretrained(model_name)
	model = MarianMTModel.from_pretrained(model_name)

	# Токенизация текста
	inputs = tokenizer(text, return_tensors="pt", padding=True)

	# Генерация перевода
	translated = model.generate(**inputs)

	# Декодирование переведенного текста
	translated_text = [tokenizer.decode(t, skip_special_tokens=True) for t in translated]
	return translated_text

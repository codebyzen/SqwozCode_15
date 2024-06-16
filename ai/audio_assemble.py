from ai import translate
import re

import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag, ne_chunk

# проверяем загрузку моделей
def download_if_not_exists(resource):
	try:
		nltk.data.find(resource)
		print(f"{resource} уже загружен.")
	except LookupError:
		nltk.download(resource.split('/')[-1])
		print(f"{resource} был загружен.")


# Загрузка необходимых ресурсов
download_if_not_exists('punkt')
download_if_not_exists('averaged_perceptron_tagger')
download_if_not_exists('maxent_ne_chunker')
download_if_not_exists('words')

# выделяем имена собственные
def extract_proper_nouns(text):

	if len(text) == 0:
		return ""

	# Токенизация текста
	tokens = word_tokenize(text)

	# Разметка токенов
	tagged_tokens = pos_tag(tokens)

	# Выделение имен собственных с использованием Chunking
	named_entities = ne_chunk(tagged_tokens)

	a = []

	# Вывод имен собственных
	for subtree in named_entities:
		if isinstance(subtree, nltk.Tree) and subtree.label() in ['PERSON', 'NN', 'NNS', 'NNP', 'NNPS']:

			for token, pos in subtree.leaves():
				# убираем мусор
				cleaned_string = re.sub(r'[\u0400-\u04FF\u0500-\u052F]', '', token)
				if cleaned_string == "" or cleaned_string in a:
					continue
				else:
					a.append(cleaned_string)
					a.append(translate.trans_en_ru(cleaned_string)[0])

	return ' '.join(a)


from elasticsearch import Elasticsearch

# Подключение к Elasticsearch
es = Elasticsearch(["http://localhost:9200"], basic_auth=('elastic', 'our_password'))
index_name = "full_results"

# Функция для загрузки данных в Elasticsearch
def upload(obj):
	document = {
		"url": obj.url,
		"text": obj.text,
		"duration": obj.duration,
		"audio": {
			"model": obj.audio.model,
			"time": obj.audio.time,
			"text": obj.audio.text,
			"text_ru": obj.audio.text_ru,
			"text_nouns": obj.audio.text_nouns,
		},
		"video": {
			"model": obj.video.model,
			"time": obj.video.time,
			"text": obj.video.text,
			"text_ru": obj.video.text_ru,
			"text_ocr": obj.video.text_ocr,
			"text_nouns": obj.audio.text_nouns,
		}
	}
	es.index(index=index_name, body=document)



def search_url(url):
	query = {
		"query": {
			"multi_match": {
				"query": url,
				"fields": "url"
			}
		}
	}
	
	response = es.search(index=index_name, body=query)
	return response


def search_text(search_text, limit, offset):
	query = {
		"from": offset,
  		"size": limit,
		"query": {
			"multi_match": {
				"query": search_text,
				"fields": [
					"audio.text^3", 
					"audio.text_nouns^2", 
					"video.text^1", 
					"video.text_nouns^2", 
					"video.text_ocr^2", 
					"video.text_ru^3",
					"text^1"
				],
				"fuzziness": 1
			}
		},
		"highlight": {
			"fields": {
				"audio.text": {},
				"video.text_ru": {}
			}
		}
	}
	
	response = es.search(index=index_name, body=query)
	return response

def search_suggest(search_text):
	query = {
  		"size": 10,
		"query": {
			"multi_match": {
				"query": search_text,
				"fields": [
					"video.text_ru^3"
					"video.text_nouns^3", 
					"video.text^2", 
					"video.text_ocr^2", 
					"audio.text_nouns^1", 
					"audio.text^1", 
				],
				"fuzziness": 2,
				"type": "most_fields"
			}
		},
		"highlight": {
			"fields": {
				"audio.text": {},
				"video.text_ru": {}
			}
		}
	}
	
	response = es.search(index=index_name, body=query)
	return response


def refresh():
	es.indices.refresh(index=index_name)

# # Функция для загрузки данных в Elasticsearch
# def upload(obj):
# 	document = {
# 		"url": obj.url,
# 		"text": obj.text,
# 		"duration": obj.duration,
# 		"audio": {
# 			"model": obj.audio.model,
# 			"time": obj.audio.time,
# 			"text": obj.audio.text,
# 			"text_ru": obj.audio.text_ru,
# 			"text_nouns": obj.audio.text_nouns,
# 		},
# 		"video": {
# 			"model": obj.video.model,
# 			"time": obj.video.time,
# 			"text": obj.video.text,
# 			"text_ru": obj.video.text_ru,
# 			"text_ocr": obj.video.text_ocr,
# 			"text_nouns": obj.video.text_nouns,
# 		}
# 	}
# 	es.index(index=index_name, body=document)
# 	# es.indices.refresh(index=index_name)  # Выполнение refresh

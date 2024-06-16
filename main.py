import os
import uuid
import time

# OPEN API
from pydantic import BaseModel
from typing import List
from fastapi import HTTPException, Query

# fastapi
from typing import Annotated, Optional
from fastapi import FastAPI, Response, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# video download from url
from urllib.request import urlretrieve
import urllib.error

# own libraries
from ai import audio as ai_audio
from ai import audio3 as ai_audio3
from ai import video as ai_video
from ai import video3 as ai_video3
from ai import structures

from database import el

import shutil

# переменные окружения для закрытия варнингов от TensorFlow по GPU
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'

# создаем объект для сервера
app = FastAPI()
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# путь для статики (js,css)
app.mount("/static", StaticFiles(directory="static/static"), name="static")

# путь для статики (index.html)
@app.get("/", response_class=HTMLResponse)
async def root(response: Response):
	response.headers["Content-Type"] = "text/html; charset=utf-8"
	f = open("./static/index.html", "r")
	return f.read()

# обработка запросов с фронтенда (поиск по тексту, хелпер для рефреша страницы)
@app.get("/list", response_class=HTMLResponse)
async def root():
	f = open("./static/index.html", "r")
	return f.read()

# обработка запросов с фронтенда (поиск по тексту, добавление ссылок на видео)
@app.get("/api", response_class=JSONResponse)
async def root(
	url: Optional[str] = None, 
	description: Optional[str] = None,
	search: Optional[str] = None, 
	quality: Optional[int] = 2, 
	limit: Optional[int] = 10, 
	offset: Optional[int] = 0,
	suggest: Optional[str] = None
	):
	
	if url: # если получили ссылку
		res = el.search_url(url)
		if len(res["hits"]["hits"]) == 0:
			search_result = await pipe_main(quality, url, description)
			el.refresh()
			db_res = el.search_url(url)
			return db_res
		else:
			return res
	elif search: # если получили текст
		return el.search_text(search, limit, offset)


# ################################
# OPEN API start
# ################################

class Video(BaseModel):
	link: str
	description: str


class Text(BaseModel):
	text: str

@app.post(
	"/index",
	tags=["index"],
	summary="Добавляет новое видео в хранилище - индекс",
	description="Добавляет новое видео в хранилище - индекс",
	response_model=Video)
async def add_index(video: Video):
	"""
	Добавляет новое видео в хранилище - индекс
	"""
	try:

		res = el.search_url(video.link)
		if len(res["hits"]["hits"]) == 0:
			full_res = await pipe_main(2, video.link, video.description)
			el.refresh()
			res = el.search_url(full_res.url)

		video_item = res["hits"]["hits"][0]["_source"]
		# Логика добавления видео в хранилище

		swagger_result = Video(
			link=video_item["url"],
			# description=video_item["video"]["text_ru"]+" "+video_item["audio"]["text"]
			description=video.description
		)
		return swagger_result
	except ValueError:
		return {"error": f'Remote HTTP error occurred: {400} - Invalid input'}
	except Exception as e:
		return {"error": f'Remote HTTP error occurred: {422} - Validation exception: {str(e)}'}


@app.get(
	"/search",
	tags=["search"],
	summary="Ищет наиболее релевантные видео под запрос",
	description="Ищет наиболее релевантные видео под запрос",
	response_model=List[Video]
)
async def search_video(text: str = Query(..., description="Текст, по которому, осущесвляется запрос")):
	"""
	Ищет наиболее релевантные видео под запрос
	"""
	try:
		# Логика поиска видео по тексту Пример результата поиска
		results = el.search_text(text, 10, 0)
		swagger_result = []
		for video_item in results["hits"]["hits"]:
			v_item = Video(
				link=video_item["_source"]["url"], 
				# description=video_item["_source"]["video"]["text_ru"]+" "+video_item["_source"]["audio"]["text"]
				description=text
			)
			swagger_result.append(v_item)
		return swagger_result
	except ValueError:
		return {"error": f'Remote HTTP error occurred: {400} - Invalid status value'}


# ################################
# OPEN API end
# ################################

# основной путь обработки видеофайла
async def pipe_main(quality, url, description=""):

	# определяем задано ли качество
	if quality not in [1,2,3]:
		return {"error":"quality not set right"}

	# директория для временного хранения файлов
	temp_path = "./temp/"

	# создаем уникальный путь
	user_uuid = f"{uuid.uuid4()}"

	# определяем имя будущего файла
	filename = f"{int(time.time() * 1000)}.mp4"

	# проверяем есть ли директория, если нет - создадим
	if not os.path.isdir(temp_path):
		os.mkdir(temp_path)

	# проверяем есть ли директория, если нет - создадим
	if not os.path.isdir(temp_path + "/" + user_uuid):
		os.mkdir(temp_path + "/" + user_uuid)

	try:
		# загружаем видеофайл
		urlretrieve(url, temp_path + user_uuid + "/" + filename)
	except urllib.error.HTTPError as e:
		return {"error": f'Remote HTTP error occurred: {e.code} - {e.reason}'}
	except urllib.error.URLError as e:
		return {"error": f'Remote URL error occurred: {e.reason}'}
	except Exception as e:
		return {"error": f'Remote unexpected error occurred: {str(e)}'}

	# если файл по каким-то причинам не загрузился то отдаем ошибку
	if not os.path.isfile(temp_path + user_uuid + "/" + filename):
		return {"error":'Downloaded but video file not created'}

	# в зависимости от выбранного качества определяем тип обработки
	if quality == 1:
		results_video, results_duration = ai_video.video_blip(temp_path, user_uuid, filename)
		results_audio = ai_audio.audio_whisper_small(temp_path, user_uuid, filename)
	elif quality == 2:
		results_video, results_duration = ai_video3.video_blip_large(temp_path, user_uuid, filename)
		results_audio = ai_audio.audio_whisper_small(temp_path, user_uuid, filename)
	elif quality == 3:
		results_video, results_duration = ai_video3.video_blip_large(temp_path, user_uuid, filename)
		results_audio = ai_audio3.audio_whisper_medium(temp_path, user_uuid, filename)

	# удаляем директорию временного хранилища
	shutil.rmtree(os.path.join(temp_path, user_uuid))

	# формируем результат
	results = structures.FullResult(
		url=url,
		text=description,
		duration=results_duration,
		audio=results_audio,
		video=results_video,
	)

	# загружаем в индекс эластика
	el.upload(results)
	
	return results
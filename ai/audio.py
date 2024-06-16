import os
import torch

import time

from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

from ai import audio_prepare
from ai import audio_assemble

from ai import structures

# определение наличия GPU
device = torch.device('gpu' if torch.cuda.is_available() else 'cpu')

# обрабатываем звуковую дорожку
def audio_whisper_small(tmp_path, user_uuid, filename):
	start_time = time.time()

	# создаем объект для результатов
	result = structures.ResultObject(
		model="Whisper small",
		time=0,
		text=None,
		text_nouns=None
	)

	# выделяем звуковую дорожку
	work_file_path = audio_prepare.process(tmp_path, user_uuid, filename)
	if not os.path.exists(work_file_path):
		return result

	# необходимо при наличии GPU
	torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

	# определяем модель
	model_id = "openai/whisper-small"
	model = AutoModelForSpeechSeq2Seq.from_pretrained(
		model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
	)
	model.to(device)

	processor = AutoProcessor.from_pretrained(model_id)

	# пайплайн обработки
	pipel = pipeline(
		"automatic-speech-recognition",
		model=model,
		tokenizer=processor.tokenizer,
		feature_extractor=processor.feature_extractor,
		max_new_tokens=128,
		chunk_length_s=30,
		batch_size=16,
		return_timestamps=True,
		torch_dtype=torch_dtype,
		device=device,
	)

	# запускаем пайплайн
	text = pipel(work_file_path)["text"]

	# выводим результат
	result.text = text
	# выделяем имена собственные
	result.text_nouns = audio_assemble.extract_proper_nouns(text)
	result.time = time.time() - start_time

	return result

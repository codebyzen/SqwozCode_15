import subprocess
import os

# выделяем звуковую дорожку
def process(tmp_path, user_uuid, filename):
	file_path = os.path.join(tmp_path, user_uuid, filename)
	work_path = os.path.join(tmp_path, user_uuid, "audio", )
	work_file_path = os.path.join(str(work_path), "audio.wav")

	if not os.path.isdir(work_path):
		os.makedirs(work_path, exist_ok=True)

	ffmpeg_res = subprocess.Popen(
		["ffmpeg", "-i", file_path, work_file_path],
		stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT,
		universal_newlines=True
	)

	for _ in ffmpeg_res.stdout:
		continue

	return work_file_path

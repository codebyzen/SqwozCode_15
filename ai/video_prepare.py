import glob
import subprocess
import math

# выбираем общее количество кадров в видео
# необходимо для правильного выделения последнего кадра
def get_video_frames(filename):
	result = subprocess.run(
		[
			"ffprobe",
			"-v",
			"error",
			"-select_streams",
			"v:0",
			"-show_entries",
			"stream=nb_frames",
			"-of",
			"default=noprint_wrappers=1:nokey=1",
			filename,
		],
		stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT,
	)
	result_string = result.stdout.decode('utf-8').split()[0]
	return result_string

# узнаем фреймрейт видео
# необходимо для правильного извлечения кадров каждые 7 секунд
def get_video_frame_rate(filename):
	result = subprocess.run(
		[
			"ffprobe",
			"-v",
			"error",
			"-select_streams",
			"v",
			"-of",
			"default=noprint_wrappers=1:nokey=1",
			"-show_entries",
			"stream=r_frame_rate",
			filename,
		],
		stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT,
	)
	result_string = result.stdout.decode('utf-8').split()[0].split('/')
	fps = float(result_string[0])/float(result_string[1])
	return fps


# выделяем первый кадр, после чего кадры каждые 7 секунд и последний кадр
def process(file_path, work_path):

	video_fps = math.floor(float(get_video_frame_rate(file_path)))
	video_frames = int(get_video_frames(file_path))

	ffmpeg_res = subprocess.Popen(
		[
			"ffmpeg",
			"-i",
			file_path,
			"-vf",
			f"select='eq(n\,0)+not(mod(n\,{video_fps}*7))+eq(n\,{video_frames-1})',setpts='N/({video_fps}*TB)'",
			"-vsync",
			"vfr",
			work_path + "/output_frame_%04d.png"
		],
		stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT,
		universal_newlines=True
	)

	for _ in ffmpeg_res.stdout:
		continue

	# определяем длительность видео
	duration = video_frames/video_fps

	try:
		duration = float(duration)
	except ValueError:
		duration = 0

	img_names = sorted(glob.glob(work_path + "/*.png"))

	return [img_names, duration]


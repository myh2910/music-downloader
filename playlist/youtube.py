from __future__ import unicode_literals
import youtube_dl
from youtube_dl.utils import sanitize_filename
from youtube_dl.utils import ExtractorError, DownloadError
import glob
import os
from timeit import default_timer as timer
from .constants import *

def time_converter(seconds: float) -> str:
	minutes, seconds = divmod(int(seconds), 60)
	hours, minutes = divmod(minutes, 60)
	time_lst = [f"{NUMBER}{i}{RESET}{j}" for i, j in [(hours, "시간"), (minutes, "분"), (seconds, "초")]]
	if hours > 0:
		k = 0
	elif minutes > 0:
		k = 1
	else:
		k = 2
	return f"총 {' '.join(time_lst[k:])}가 걸렸습니다."

def download(
	url: str,
	codec: str = "mp3",
	start: int = None,
	end: int = None,
	playlist_name: str = None,
	write_playlist: bool = True,
	export_to_smpl: bool = False,
	home: str = HOME,
	folder: str = "",
	write_thumbnail: bool = True,
	retries: int = 3,
	fragment_retries: int = 3,
	auto: bool = False
) -> float:
	"""영상 및 음악 다운로드.

	옵션 설명:
	* `url`: 영상 및 플레이리스트 링크.
	* `codec`: 파일 확장자 (`"mp3"`, `"mp4"`).
	* `start`: 플레이리스트의 시작점을 나타내는 정수.
	* `end`: 플레이리스트의 종점을 나타내는 정수.
	* `playlist_name`: 플레이리스트 이름.
	* `write_playlist`: 플레이리스트 파일 생성 여부.
	* `export_to_smpl`: 삼성 플레이리스트 파일 생성 여부.
	* `home`: 플레이리스트를 다운로드 할 폴더 이름.
	* `write_thumbnail`: 썸네일 이미지를 파일에 추가.
	* `retries`: HTTP 오류 발생 시 다운로드를 반복할 최대 횟수.
	* `fragment_retries`: 오류 발생 시 영상 fragment 다운로드를 반복할 최대 횟수.
	* `auto`: 다운로드 자동화.
	"""
	elapsed_time = -timer()
	home += folder
	init()
	ydl_opts = {
		"writethumbnail": write_thumbnail,
		"fragment_retries": fragment_retries,
		"retries": fragment_retries,
		"cachedir": False
	}
	if codec == "mp3":
		ydl_opts["format"] = "bestaudio/best"
		ydl_opts["postprocessors"] = [
			{
				"key": "FFmpegExtractAudio",
				"preferredcodec": "mp3",
				"preferredquality": "320"
			},
			{"key": "FFmpegMetadata"},
			{"key": "EmbedThumbnail"}
		]
	elif codec in ["webm", "mp4"]:
		ydl_opts["format"] = "bestvideo+bestaudio/best"
		ydl_opts["merge_output_format"] = codec
		ydl_opts["postprocessors"] = [
			{"key": "FFmpegMetadata"},
			{"key": "EmbedThumbnail"}
		]
	else:
		print(f"{ERROR} 파일 확장자 {INPUT}\"{codec}\"{RESET}는 지원되지 않습니다.")
		return elapsed_time + timer()

	print(f"{DOWNLOAD} 웹페이지 정보 추출 중...")
	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		i = retries
		while True:
			try:
				playlist_dict = ydl.extract_info(url, False)
				break
			except (ExtractorError, DownloadError):
				return elapsed_time + timer()
			except:
				if i == 0:
					print(f"{ERROR} 웹페이지 추출이 불가능합니다.")
					return elapsed_time + timer()
				print(f"{WARNING} 에러 발생. 다시 시도 중...")
				ydl.cache.remove()
				i -= 1
		try:
			if playlist_name:
				playlist = playlist_name
			else:
				try:
					playlist = playlist_dict["title"]
				except:
					playlist = playlist_dict["webpage_url_basename"]
			entries = playlist_dict["entries"]
		except:
			if playlist_name:
				playlist = playlist_name
			else:
				playlist = "NA"
			entries = [playlist_dict]
		playlist = sanitize_filename(playlist)
		prop_lst = []
		total = 0
		for file in entries:
			prop_lst.append({
				"name": f"{playlist}/{sanitize_filename(file.get('title'))}-{file.get('id')}.{codec}",
				"url": file.get("webpage_url")
			})
			total += 1
		if not start:
			start = 1
		if not end:
			end = total
	elapsed_time += timer()

	if playlist != "NA" and write_playlist:
		playlist_file = f"{home}/{playlist}.m3u"
		message = f"플레이리스트 파일 {FILE}{playlist}.m3u{RESET}"
		if os.path.exists(playlist_file):
			if auto:
				print(f"{CREATE} {message} 업데이트 중...")
				confirm = "y"
			else:
				print(f"{UPDATE} {message}을 업데이트 하시겠습니까? {INPUT}(y/N){RESET}: ", end="")
				confirm = input()
		else:
			print(f"{CREATE} {message} 생성 중...")
			confirm = "y"
		if confirm.strip() in ["Y", "y"]:
			if not os.path.exists(home):
				os.mkdir(home)
			with open(playlist_file, "w", encoding="utf8") as m3u:
				m3u.write("\n".join(prop["name"] for prop in prop_lst))
		if export_to_smpl:
			playlist_file = f"{home}/{playlist}.smpl"
			message = f"플레이리스트 파일 {FILE}{playlist}.smpl{RESET}"
			if os.path.exists(playlist_file):
				if auto:
					print(f"{CREATE} {message} 업데이트 중...")
					confirm = "y"
				else:
					print(f"{UPDATE} {message}을 업데이트 하시겠습니까? {INPUT}(y/N){RESET}: ", end="")
					confirm = input()
			else:
				print(f"{CREATE} {message} 생성 중...")
				confirm = "y"
			if confirm.strip() in ["Y", "y"]:
				if not os.path.exists(home):
					os.mkdir(home)
				with open(playlist_file, "w", encoding = "utf8") as smpl:
					smpl.write("{\"members\": [")
					smpl.write(",".join("\n\t{\"info\": \"/storage/emulated/0/Music" + folder + "/" + prop["name"] + f"\", \"order\": {i + 1}, \"type\": 65537" + "}"
						for i, prop in enumerate(prop_lst)))
					smpl.write("\n], \"sortBy\": 4}")

	ydl_opts["outtmpl"] = f"{home}/{playlist}" + r"/%(title)s-%(id)s.%(ext)s"
	norm_lst = [os.path.normpath(f"{home}/{prop['name']}") for prop in prop_lst]
	downloaded = [os.path.normpath(file) for file in glob.glob(f"{home}/{playlist}/*")]

	add_lst = []
	del_lst = []
	tmp_lst = []

	elapsed_time -= timer()
	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		if playlist != "NA":
			print(f"{DOWNLOAD} 플레이리스트 {INPUT}{playlist}{RESET} 다운로드 중...")
		for i in range(start-1, end):
			file = norm_lst[i]
			running = True
			if file in downloaded:
				if len(glob.glob(f"{os.path.splitext(file)[0]}.*")) == 1:
					print(f"{DOWNLOAD} 파일 {FILE}{os.path.relpath(file, home)}{RESET}이 이미 존재합니다. {INDEX}({i+1}/{total}){RESET}")
					running = False
			if running:
				print(f"{DOWNLOAD} 파일 {FILE}{os.path.relpath(file, home)}{RESET} 다운로드 중... {INDEX}({i+1}/{total}){RESET}")
				add_lst.append(file)
				j = retries
				while True:
					try:
						ydl.download([prop_lst[i]["url"]])
						break
					except:
						if j == 0:
							print(f"{ERROR} 파일을 다운로드할 수 없습니다.")
							for k in glob.glob(f"{os.path.splitext(file)[0]}.*"):
								os.remove(k)
							add_lst.pop()
							tmp_lst.append(file)
							break
						print(f"{WARNING} 에러 발생. 다시 다운로드 중...")
						ydl.cache.remove()
						for k in glob.glob(f"{os.path.splitext(file)[0]}.*"):
							os.remove(k)
						j -= 1
	elapsed_time += timer()

	if playlist != "NA":
		for file in glob.glob(f"{home}/{playlist}/*"):
			if not os.path.normpath(file) in norm_lst:
				if auto:
					print(f"{WARNING} 파일 {FILE}{os.path.relpath(file, home)}{RESET} 삭제 중...")
					confirm = "y"
				else:
					print(f"{WARNING} 파일 {FILE}{os.path.relpath(file, home)}{RESET}을 플레이리스트에서 찾을 수 없습니다. 지우겠습니까? {INPUT}(y/N){RESET}: ", end="")
					confirm = input()
				if confirm.strip() in ["Y", "y"]:
					os.remove(file)
					del_lst.append(file)

	print(f"{FINISHED} 다운로드가 완료되었습니다. {time_converter(elapsed_time)}")
	with open(f"{home}/{playlist}.diff", "w", encoding="utf8") as diff_file:
		for file in add_lst:
			diff_file.write(f"+ {os.path.relpath(file, home)}\n")
		for file in del_lst:
			diff_file.write(f"- {os.path.relpath(file, home)}\n")
		for file in tmp_lst:
			diff_file.write(f"! {os.path.relpath(file, home)}\n")
	return elapsed_time

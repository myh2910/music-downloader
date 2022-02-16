"""
Useful functions for other modules.

"""
import glob
import os
import random

import colorama
from colorama import Fore

from .config import CONFIG


def colored(text, key):
	"""
	Print colored text.

	Parameters
	----------
	text : str or int
		Text to print.
	key : str
		Text type.
	"""
	match key:
		case "file":
			color = Fore.LIGHTCYAN_EX
		case "num":
			color = Fore.LIGHTGREEN_EX
		case "input":
			color = Fore.LIGHTMAGENTA_EX
		case _:
			color = ""
	return f"{color}{text}{Fore.RESET}"

def print_time(seconds):
	"""
	Print elapsed time.

	Parameters
	----------
	seconds : float
		Time in seconds.

	Returns
	-------
	str
		Converted time in hours, minutes and seconds.
	"""
	minutes, seconds = divmod(int(seconds), 60)
	hours, minutes = divmod(minutes, 60)

	time_lst = []
	for cnt, name in ((hours, "시간"), (minutes, "분"), (seconds, "초")):
		time_lst.append(f'{colored(cnt, "num")}{name}')

	if hours > 0:
		idx = 0
	elif minutes > 0:
		idx = 1
	else:
		idx = 2

	print(f":: 다운로드가 완료되었습니다. 총 {' '.join(time_lst[idx:])}가 걸렸습니다.")

def sort_lines(lines, method):
	"""
	Sort lines.

	Parameters
	----------
	lines : list of str
		List of lines to sort.
	sort_method : str
		Sorting method ("suffle", "name", "artist").

	Returns
	-------
	lines : list of str
		The sorted lines.
	"""
	match method:
		case "suffle":
			random.shuffle(lines)
		case "name":
			lines = sorted(lines)
		case "artist":
			# TODO: artist 순대로 정렬
			pass
		case _:
			_method = colored(f'"{method}"', "input")
			print(f" [ERROR] 옵션 {_method}이 존재하지 않습니다.")
			return False
	return lines

def create_playlist(playlist, out="m3u", method="name"):
	"""
	Generate a playlist file.

	Parameters
	----------
	playlist : str
		Playlist name.
	out : str, optional
		Playlist file extension ("m3u", "smpl").
	method : str, optional
		Playlist sorting method.
	"""
	colorama.init()
	print(":: 플레이리스트 생성 중...")

	m3u_path = f"{CONFIG['home']}/{playlist}.m3u"
	smpl_path = f"{CONFIG['home']}/{playlist}.smpl"
	_playlist = colored(playlist, "file")

	if out == "m3u":
		if not os.path.exists(f"{CONFIG['home']}/{playlist}"):
			print(f" [ERROR] 플레이리스트 폴더 {_playlist}를 찾을 수 없습니다.")
			return

		lines = []
		for ext in ["mp3", "mp4"]:
			lines.extend(glob.glob(f"{CONFIG['home']}/{playlist}/*.{ext}"))

		if not lines:
			print(f" [ERROR] 플레이리스트 폴더 {_playlist}가 비어 있습니다.")
			return

		with open(m3u_path, "w", encoding="utf8") as m3u:
			for file in sort_lines(lines, method):
				m3u.write(f"{os.path.relpath(file, CONFIG['home'])}\n")
	elif out == "smpl":
		with open(m3u_path, "r", encoding = "utf8") as m3u:
			music = m3u.readlines()
			with open(smpl_path, "w", encoding = "utf8") as smpl:
				smpl.write('{"members": [')
				for idx, mp3 in enumerate(music):
					smpl.write(f"""
\t{{"info": "/storage/emulated/0/{CONFIG['home']}/{mp3}", "order": {idx + 1}, \
"type": 65537}},"""
					)
				smpl.write('\n], "sortBy": 4}')

	print(":: 플레이리스트 생성이 완료되었습니다.")

def sort_playlist(playlist, method="suffle"):
	"""
	Sort a playlist file.

	Parameters
	----------
	playlist : str
		Playlist name.
	method : str, optional
		Playlist sorting method.
	"""
	colorama.init()
	print(":: 플레이리스트 정렬 중...")

	path = os.path.join(CONFIG['home'], f"{playlist}.m3u")

	if not os.path.exists(path):
		print(f' [ERROR] 플레이리스트 파일 {colored(f"{playlist}.m3u", "file")}을 \
찾을 수 없습니다.')
		return

	with open(path, "r+", encoding="utf8") as file:
		lines = sort_lines([line.strip() for line in file.readlines()], method)

		if not lines:
			print(" [ERROR] 플레이리스트가 비어 있습니다.")
			return

		file.seek(0)
		file.writelines("\n".join(i for i in lines if i != ""))
		file.truncate()

		print(":: 플레이리스트 정렬이 완료되었습니다.")

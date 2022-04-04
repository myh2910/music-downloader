"""
Get YouTube videos and playlist data.

"""
from __future__ import unicode_literals

import glob
import os
from datetime import datetime

import youtube_dl
from youtube_dl.utils import DownloadError, ExtractorError, sanitize_filename

from .config import CONFIG
from .utils import colored

tmp = {}

def get_ydl_opts(ext):
	"""
	Get YoutubeDL options.

	Parameters
	----------
	ext : str
		File extension.

	Returns
	-------
	bool
	"""
	tmp['ydl_opts'] = CONFIG['ydl_opts']

	if ext == "mp3":
		tmp['ydl_opts']['format'] = "bestaudio/best"
		tmp['ydl_opts']['postprocessors'] = [
			{
				'key': "FFmpegExtractAudio",
				'preferredcodec': "mp3",
				'preferredquality': "320"
			},
			{'key': "FFmpegMetadata"},
			{'key': "EmbedThumbnail"}
		]
	elif ext in ["webm", "mp4"]:
		tmp['ydl_opts']['format'] = "bestvideo+bestaudio/best"
		tmp['ydl_opts']['merge_output_format'] = ext
		tmp['ydl_opts']['postprocessors'] = [
			{'key': "FFmpegMetadata"},
			{'key': "EmbedThumbnail"}
		]
	else:
		_ext = colored(f'"{ext}"', "input")
		print(f"[ERROR] 파일 확장자 {_ext}는 지원되지 않습니다.")
		return False

	return True

def extract_info(url, ext, playlist):
	"""
	Extract video information.

	Parameters
	----------
	url : str
		YouTube URL.
	ext : str
		File extension.
	playlist : str or None
		Playlist name.

	Returns
	-------
	str or None
		Valid playlist name.
	"""
	if not get_ydl_opts(ext):
		return None

	print(":: 웹페이지 정보 추출 중...")
	with youtube_dl.YoutubeDL(tmp['ydl_opts']) as ydl:
		retries = CONFIG['num_retries']
		while True:
			try:
				playlist_dict = ydl.extract_info(url, False)
				break
			except (ExtractorError, DownloadError):
				return None
			except:
				if retries == 0:
					print(" [ERROR] 웹페이지 추출이 불가능합니다.")
					return None
				print(" [ERROR] 에러 발생. 다시 시도 중...")
				ydl.cache.remove()
				retries -= 1

	if 'entries' in playlist_dict:
		if not playlist:
			if 'title' in playlist_dict:
				playlist = playlist_dict['title']
			else:
				playlist = playlist_dict['webpage_url_basename']
		tmp['entries'] = playlist_dict['entries']
	else:
		if not playlist:
			playlist = "NA"
		tmp['entries'] = [playlist_dict]

	tmp['playlist'] = sanitize_filename(playlist)
	tmp['total'] = len(tmp['entries'])

	return tmp['playlist']

def __init__(ext, start, end):
	"""
	Initialize module.

	Parameters
	----------
	ext : str
		File extension.
	start : int
		Download playlist starting from this index.
	end : int or None
		Download playlist ending at this index.
	"""
	tmp['start'] = start

	if end:
		tmp['end'] = end
	else:
		tmp['end'] = tmp['total']

	tmp['name'], tmp['url'], tmp['norm'] = [], [], []

	for file in tmp['entries']:
		title = sanitize_filename(file.get('title'))
		name = f"{tmp['playlist']}/{title}-{file.get('id')}.{ext}"

		tmp['name'].append(name)
		tmp['url'].append(file.get('webpage_url'))
		tmp['norm'].append(os.path.normpath(os.path.join(CONFIG['home'], name)))

def download_video():
	"""
	Download YouTube video.
	"""
	path = f"{CONFIG['home']}/{tmp['playlist']}/*"
	downloaded = [os.path.normpath(file) for file in glob.glob(path)]

	tmp['add'], tmp['pop'] = [], []
	tmp['ydl_opts']['outtmpl'] = f"{CONFIG['home']}/{tmp['playlist']}/\
%(title)s-%(id)s.%(ext)s"

	with youtube_dl.YoutubeDL(tmp['ydl_opts']) as ydl:
		if tmp['playlist'] != "NA":
			_playlist = colored(tmp['playlist'], 'input')
			print(f":: 플레이리스트 {_playlist} 다운로드 중...")

		for idx in range(tmp['start'], tmp['end']):
			file = tmp['norm'][idx]
			path = colored(os.path.relpath(file, CONFIG['home']), "file")

			if file in downloaded:
				if len(glob.glob(f"{os.path.splitext(file)[0]}.*")) == 1:
					print(f":: 파일 {path}이 이미 존재합니다. ({idx + 1}/{tmp['total']})")
					continue

			print(f":: 파일 {path} 다운로드 중... ({idx + 1}/{tmp['total']})")
			tmp['add'].append(file)
			retries = CONFIG['num_retries']

			while True:
				try:
					ydl.download([tmp['url'][idx]])
					break
				except:
					if retries == 0:
						print(" [ERROR] 파일을 다운로드할 수 없습니다.")
						for ext in glob.glob(f"{os.path.splitext(file)[0]}.*"):
							os.remove(ext)

						tmp['add'].pop()
						tmp['pop'].append(file)
						break

					print(" [ERROR] 에러 발생. 다시 다운로드 중...")
					ydl.cache.remove()

					for ext in glob.glob(f"{os.path.splitext(file)[0]}.*"):
						os.remove(ext)
					retries -= 1

def export_to_m3u():
	"""
	Export to M3U playlist.
	"""
	filename = f"{tmp['playlist']}.m3u"
	path = os.path.join(CONFIG['home'], filename)
	_file = f'플레이리스트 파일 {colored(filename, "file")}'

	if os.path.exists(path):
		if CONFIG['auto']:
			print(f":: {_file} 업데이트 중...")
			confirm = "y"
		else:
			confirm = input(f":: {_file}을 업데이트 하시겠습니까? [y/N] ").strip()
	else:
		print(f":: {_file} 생성 중...")
		confirm = "y"

	if confirm in ["Y", "y"]:
		if not os.path.exists(CONFIG['home']):
			os.mkdir(CONFIG['home'])
		with open(path, "w", encoding="utf8") as file:
			file.write("\n".join(tmp['name']))

def export_to_smpl():
	"""
	Export to Samsung playlist.

	Save the generated playlist file in Phone -> Playlists and then go to Samsung
	Music settings -> Manage playlists -> Import playlists and select your
	playlist file.
	"""
	filename = f"{tmp['playlist']}.smpl"
	path = os.path.join(CONFIG['home'], filename)
	_file = f'플레이리스트 파일 {colored(filename, "file")}'

	if os.path.exists(path):
		if CONFIG['auto']:
			print(f":: {_file} 업데이트 중...")
			confirm = "y"
		else:
			confirm = input(f":: {_file}을 업데이트 하시겠습니까? [y/N] ").strip()
	else:
		print(f":: {_file} 생성 중...")
		confirm = "y"

	if confirm in ["Y", "y"]:
		if not os.path.exists(CONFIG['home']):
			os.mkdir(CONFIG['home'])

		with open(path, "w", encoding = "utf8") as file:
			file.write('{"members": [')
			file.write(",".join(
				f"""\n\t{{"info": "/storage/emulated/0/{CONFIG['home']}/{name}", \
"order": {idx + 1}, "type": 65537}}""" for idx, name in enumerate(tmp['name'])
			))
			file.write('\n], "sortBy": 4}')

def write_diff():
	"""
	Write diff file.
	"""
	tmp['del'] = []

	if tmp['playlist'] != "NA":
		for file in glob.glob(f"{CONFIG['home']}/{tmp['playlist']}/*"):
			if os.path.normpath(file) in tmp['norm']:
				continue

			path = colored(os.path.relpath(file, CONFIG['home']), 'file')
			if CONFIG['auto']:
				print(f":: 파일 {path} 삭제 중...")
				confirm = "y"
			else:
				confirm = input(f":: 파일 {path}을 플레이리스트에서 찾을 수 없습니다. \
지우겠습니까? [y/N] ").strip()

			if confirm in ["Y", "y"]:
				os.remove(file)
				tmp['del'].append(file)

	if tmp['add'] or tmp['del'] or tmp['pop']:
		path = os.path.join(CONFIG['home'], f"{tmp['playlist']}.diff")
		with open(path, "a", encoding="utf8") as diff:
			curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			diff.write(f"@ {curr_time} (+{len(tmp['add'])} -{len(tmp['del'])} \
!{len(tmp['pop'])})\n")
			for file in tmp['add']:
				diff.write(f"+ {os.path.relpath(file, CONFIG['home'])}\n")
			for file in tmp['del']:
				diff.write(f"- {os.path.relpath(file, CONFIG['home'])}\n")
			for file in tmp['pop']:
				diff.write(f"! {os.path.relpath(file, CONFIG['home'])}\n")

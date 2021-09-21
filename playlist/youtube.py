from __future__ import unicode_literals
import youtube_dl
from youtube_dl.utils import sanitize_filename
from colorama import init
import glob
import os
from timeit import default_timer as timer
from .constants import *

def download(
		url: str,
		codec: str = 'mp3',
		start: int = None,
		end: int = None,
		writethumbnail: bool = True,
		retries: int = 2,
		fragment_retries: int = 5
	) -> None:
	"""유튜브 영상 & 음악 다운로드.

	옵션 설명:
	* `url`: 유튜브 영상 링크.
	* `codec`: 파일 확장자 (`'mp3'`, `'mp4'`).
	* `start`: 플레이리스트의 `start`번부터 다운로드.
	* `end`: 플레이리스트의 `end`번까지 다운로드."""

	ydl_opts = {
		'outtmpl': HOME + r'/%(playlist)s/%(title)s-%(id)s.%(ext)s',
		'writethumbnail': writethumbnail,
		'fragment_retries': fragment_retries
	}
	if codec == 'mp3':
		ydl_opts['format'] = 'bestaudio/best'
		# TODO: https://www.youtube.com/watch?v=Wi5Rrbp9nGY 유튜브 썸네일이 mp3 파일에 embed 안됨.
		ydl_opts['postprocessors'] = [
			{
				'key': 'FFmpegExtractAudio',
				'preferredcodec': 'mp3',
				'preferredquality': '320'
			},
			{'key': 'FFmpegMetadata'},
			{'key': 'EmbedThumbnail'}
		]
	elif codec in ['webm', 'mp4']:
		ydl_opts['format'] = 'bestvideo+bestaudio/best'
		ydl_opts['merge_output_format'] = codec
		ydl_opts['postprocessors'] = [
			{'key': 'FFmpegMetadata'},
			{'key': 'EmbedThumbnail'}
		]

	init()
	print(f'{CYAN}웹페이지 정보 추출 중...{RESET}')
	elapsed_time = -timer()
	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		try:
			playlist_dict = ydl.extract_info(url, False)
		except:
			print(f'{CYAN}에러 발견. 다시 추출 중...{RESET}')
			ydl.cache.remove()
			playlist_dict = ydl.extract_info(url, False)
		try:
			playlist = playlist_dict['title']
			entries = playlist_dict['entries']
		except:
			playlist = 'NA'
			entries = [playlist_dict]
		file_lst = []
		for file in entries:
			title, id = sanitize_filename(file.get('title')), file.get('id')
			file_lst.append(f'{playlist}/{title}-{id}.{codec}')
	elapsed_time += timer()

	if playlist != 'NA':
		playlist_file = f'{HOME}/{playlist}.m3u'
		if os.path.exists(playlist_file):
			print(f'{CYAN}플레이리스트 파일을 업데이트 하시겠습니까? {MAGENTA}(y/N){CYAN}: {RESET}', end='')
			confirm = input()
		else:
			print(f'{CYAN}플레이리스트 파일 생성 중...{RESET}')
			confirm = 'y'
		if confirm in ['Y', 'y']:
			with open(playlist_file, 'w', encoding='utf8') as m3u:
				m3u.write('\n'.join(file_lst))
		total = len(file_lst)
		if not start:
			start = 1
		if not end:
			end = total
	else:
		total, start, end = 1, 1, 1

	ydl_opts['outtmpl'] = f'{HOME}/{playlist}' + r'/%(title)s-%(id)s.%(ext)s'
	norm_lst = [os.path.normpath(f'{HOME}/{file}') for file in file_lst]
	downloaded = glob.glob(f'{HOME}/{playlist}/*')

	elapsed_time -= timer()
	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		for i in range(start-1, end):
			file = norm_lst[i]
			filename = os.path.split(file)[1]
			print(f'{CYAN}파일 {YELLOW}{filename}{CYAN} 다운로드 중... {MAGENTA}({i+1}/{total}){RESET}')
			running = True
			if file in downloaded:
				if len(glob.glob(f'{os.path.splitext(file)[0]}.*')) == 1:
					running = False
			if running:
				id = os.path.splitext(file)[0][-11:]
				while True:
					if retries == 0:
						print(f'{CYAN}파일을 다운로드할 수가 없습니다.{RESET}')
						break
					try:
						ydl.download([id])
						break
					except:
						print(f'{CYAN}에러 발견. 다시 다운로드 중...{RESET}')
						ydl.cache.remove()
						retries -= 1
	elapsed_time += timer()

	if playlist != 'NA':
		for file in downloaded:
			if not file in norm_lst:
				print(f'{CYAN}파일 {YELLOW}{os.path.split(file)[1]}{CYAN}을 플레이리스트에서 찾을 수 없습니다. 지우겠습니까? {MAGENTA}(y/N){CYAN}: {RESET}', end='')
				confirm = input()
				if confirm in ['Y', 'y']:
					os.remove(file)

	print(f'{CYAN}다운로드 완료. 걸린 시간: {YELLOW}{elapsed_time}{CYAN}초.{RESET}')

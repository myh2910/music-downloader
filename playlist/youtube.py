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
	home: str = HOME,
	writethumbnail: bool = True,
	retries: int = 2,
	fragment_retries: int = 5
):
	"""유튜브 영상 & 음악 다운로드.

	옵션 설명:
	* `url`: 유튜브 링크.
	* `codec`: 파일 확장자 (`'mp3'`, `'mp4'`).
	* `start`: 플레이리스트의 시작점을 나타내는 정수.
	* `end`: 플레이리스트의 종점을 나타내는 정수.
	* `home`: 플레이리스트를 다운로드 할 폴더 이름.
	* `writethumbnail`: 썸네일 이미지를 파일에 추가.
	* `retries`: 오류 발생 시 다운로드를 반복할 최대 횟수.
	* `fragment_retries`: 오류 발생 시 영상 fragment 다운로드를 반복할 최대 횟수.
	"""
	ydl_opts = {
		'outtmpl': home + r'/%(playlist)s/%(title)s-%(id)s.%(ext)s',
		'writethumbnail': writethumbnail,
		'fragment_retries': fragment_retries
	}
	if codec == 'mp3':
		ydl_opts['format'] = 'bestaudio/best'
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
	else:
		print(f"{ERROR} 파일을 {INPUT}'{codec}'{RESET} 확장자로 다운로드할 수 없습니다.")
		return False

	init()
	print(f'{DOWNLOAD} 웹페이지 정보 추출 중...')
	elapsed_time = -timer()
	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		i = retries
		while True:
			if i == 0:
				print(f'{ERROR} 웹페이지 추출이 불가능합니다.')
				return False
			try:
				playlist_dict = ydl.extract_info(url, False)
				break
			except:
				print(f'{WARNING} 에러 발견. 다시 시도 중...')
				ydl.cache.remove()
				i -= 1
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
		playlist_file = f'{home}/{playlist}.m3u'
		if os.path.exists(playlist_file):
			print(f'{UPDATE} 플레이리스트 파일 {FILE}{playlist}.m3u{RESET}을 업데이트 하시겠습니까? {INPUT}(y/N){RESET}: ', end='')
			confirm = input()
		else:
			print(f'{CREATE} 플레이리스트 파일 {FILE}{playlist}.m3u{RESET} 생성 중...')
			confirm = 'y'
		if confirm in ['Y', 'y']:
			if not os.path.exists(home):
				os.mkdir(home)
			with open(playlist_file, 'w', encoding='utf8') as m3u:
				m3u.write('\n'.join(file_lst))
	total = len(file_lst)
	if not start:
		start = 1
	if not end:
		end = total

	ydl_opts['outtmpl'] = f'{home}/{playlist}' + r'/%(title)s-%(id)s.%(ext)s'
	norm_lst = [os.path.normpath(f'{home}/{file}') for file in file_lst]
	downloaded = [os.path.normpath(file) for file in glob.glob(f'{home}/{playlist}/*')]

	elapsed_time -= timer()
	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		if playlist != 'NA':
			print(f'{DOWNLOAD} 플레이리스트 {INPUT}{playlist}{RESET} 다운로드 중...')
		for i in range(start-1, end):
			file = norm_lst[i]
			print(f'{DOWNLOAD} 파일 {FILE}{os.path.relpath(file, home)}{RESET} 다운로드 중... {INDEX}({i+1}/{total}){RESET}')
			running = True
			if file in downloaded:
				if len(glob.glob(f'{os.path.splitext(file)[0]}.*')) == 1:
					running = False
			if running:
				id = os.path.splitext(file)[0][-11:]
				j = retries
				while True:
					if j == 0:
						print(f'{ERROR} 파일을 다운로드할 수 없습니다.')
						break
					try:
						ydl.download([id])
						break
					except:
						print(f'{WARNING} 에러 발견. 다시 다운로드 중...')
						ydl.cache.remove()
						j -= 1
	elapsed_time += timer()

	if playlist != 'NA':
		for file in glob.glob(f'{home}/{playlist}/*'):
			if not os.path.normpath(file) in norm_lst:
				print(f'{WARNING} 파일 {FILE}{os.path.relpath(file, home)}{RESET}을 플레이리스트에서 찾을 수 없습니다. 지우겠습니까? {INPUT}(y/N){RESET}: ', end='')
				confirm = input()
				if confirm in ['Y', 'y']:
					os.remove(file)

	print(f'{FINISHED} 다운로드가 완료되었습니다. 총 {NUMBER}{elapsed_time}{RESET}초가 걸렸습니다.')

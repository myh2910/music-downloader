from __future__ import unicode_literals
import youtube_dl
from youtube_dl.utils import sanitize_filename
import glob
import os
from timeit import default_timer as timer
from .constants import *

def download(
	url: str,
	codec: str = 'mp3',
	start: int = None,
	end: int = None,
	playlist_name: str = None,
	home: str = HOME,
	writethumbnail: bool = True,
	retries: int = 2,
	fragment_retries: int = 3
):
	"""영상 및 음악 다운로드.

	옵션 설명:
	* `url`: 영상 및 플레이리스트 링크.
	* `codec`: 파일 확장자 (`'mp3'`, `'mp4'`).
	* `start`: 플레이리스트의 시작점을 나타내는 정수.
	* `end`: 플레이리스트의 종점을 나타내는 정수.
	* `playlist_name`: 플레이리스트 이름.
	* `home`: 플레이리스트를 다운로드 할 폴더 이름.
	* `writethumbnail`: 썸네일 이미지를 파일에 추가.
	* `retries`: HTTP 오류 발생 시 다운로드를 반복할 최대 횟수.
	* `fragment_retries`: 오류 발생 시 영상 fragment 다운로드를 반복할 최대 횟수.
	"""
	init()
	ydl_opts = {
		'outtmpl': home + r'/%(playlist)s/%(title)s-%(id)s.%(ext)s',
		'writethumbnail': writethumbnail,
		'fragment_retries': fragment_retries,
		'retries': fragment_retries,
		'cachedir': False
	}
	if playlist_name:
		ydl_opts['outtmpl'] = f'{home}/{playlist_name}' + r'/%(title)s-%(id)s.%(ext)s'
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
		print(f"{ERROR} 파일 확장자 {INPUT}'{codec}'{RESET}는 지원되지 않습니다.")
		return False

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
				i -= 1
		try:
			if playlist_name:
				playlist = playlist_name
			else:
				playlist = playlist_dict['title']
			entries = playlist_dict['entries']
		except:
			if playlist_name:
				playlist = playlist_name
			else:
				playlist = 'NA'
			entries = [playlist_dict]
		prop_lst = []
		total = 0
		for file in entries:
			prop_lst.append({
				'name': f"{playlist}/{sanitize_filename(file.get('title'))}-{file.get('id')}.{codec}",
				'url': file.get('webpage_url')
			})
			total += 1
		if not start:
			start = 1
		if not end:
			end = total
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
				m3u.write('\n'.join(prop['name'] for prop in prop_lst))

	ydl_opts['outtmpl'] = f'{home}/{playlist}' + r'/%(title)s-%(id)s.%(ext)s'
	norm_lst = [os.path.normpath(f"{home}/{prop['name']}") for prop in prop_lst]
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
				j = retries
				while True:
					if j == 0:
						print(f'{ERROR} 파일을 다운로드할 수 없습니다.')
						for k in glob.glob(f'{os.path.splitext(file)[0]}.*'):
							os.remove(k)
						break
					try:
						ydl.download([prop_lst[i]['url']])
						break
					except:
						print(f'{WARNING} 에러 발견. 다시 다운로드 중...')
						for k in glob.glob(f'{os.path.splitext(file)[0]}.*'):
							os.remove(k)
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

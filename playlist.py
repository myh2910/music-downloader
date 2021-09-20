from __future__ import unicode_literals
import youtube_dl
import glob
import os
from colorama import init, Fore
from timeit import default_timer as timer
import random

CYAN = Fore.LIGHTCYAN_EX
YELLOW = Fore.LIGHTYELLOW_EX
MAGENTA = Fore.LIGHTMAGENTA_EX
RESET = Fore.RESET

def get_name(file: str) -> str:
	return os.path.splitext(file)[0]

def download(url: str, codec: str = 'mp3', start: int = None, end: int = None) -> None:
	"""유튜브 영상 & 음악 다운로드.

	옵션 설명:
	* `url`: 유튜브 영상 링크.
	* `start`: 플레이리스트의 `start`번째 부터 다운로드.
	* `end`: 플레이리스트의 `end`번째 까지 다운로드."""

	ydl_opts = {
		'outtmpl': r'%(playlist)s/%(title)s-%(id)s.%(ext)s',
		'writethumbnail': True
	}
	if codec == 'mp3':
		ydl_opts['format'] = 'bestaudio/best'
		ydl_opts['postprocessors'] = [
			{
				'key': 'FFmpegExtractAudio',
				'preferredcodec': 'mp3',
				'preferredquality': '320'
			},
			{'key': 'EmbedThumbnail'},
			{'key': 'FFmpegMetadata'}
		]
	elif codec in ['webm', 'mp4']:
		ydl_opts['format'] = 'bestvideo+bestaudio/best'
		ydl_opts['merge_output_format'] = codec
		ydl_opts['postprocessors'] = [
			{'key': 'EmbedThumbnail'},
			{'key': 'FFmpegMetadata'}
		]

	init()
	print(f'{CYAN}웹페이지 정보 추출 중...{RESET}')
	elapsed_time = -timer()
	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		playlist_dict = ydl.extract_info(url, False)
		try:
			playlist = playlist_dict['title']
			entries = playlist_dict['entries']
		except:
			playlist = 'NA'
			entries = [playlist_dict]
		file_lst = []
		for file in entries:
			title, id = file.get('title'), file.get('id')
			title = ''.join(i if i not in '[]\/:*?"<>|' else '_' for i in title)
			file_lst.append(f'{playlist}/{title}-{id}.{codec}')
	elapsed_time += timer()

	if playlist != 'NA':
		confirm = 'y'
		playlist_file = f'{playlist}.m3u'
		if os.path.exists(playlist_file):
			print(f'{CYAN}플레이리스트 파일을 업데이트 하시겠습니까? {MAGENTA}(y/N){CYAN}: {RESET}', end='')
			confirm = input()
		if confirm in ['Y', 'y']:
			with open(playlist_file, 'w', encoding='utf8') as m3u:
				m3u.write('\n'.join(file_lst))
			start, end = None, None
		total = len(file_lst)
		if not start:
			start = 1
		if not end:
			end = total
	else:
		total, start, end = 1, 1, 1

	ydl_opts['outtmpl'] = playlist + r'/%(title)s-%(id)s.%(ext)s'
	downloaded = glob.glob(f'{playlist}/*.{codec}')
	print(downloaded)

	elapsed_time -= timer()
	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		for i in range(start-1, end):
			file = file_lst[i]
			print(f'{CYAN}파일 {YELLOW}{file}{CYAN} 다운로드 중... {MAGENTA}({i+1}/{total}){RESET}')
			running = True
			print(file)
			if file in downloaded:
				if glob.glob(f'{get_name(file)}.*') == [file]:
					running = False
			if running:
				try:
					ydl.download([get_name(file)[-11:]])
				except:
					ydl.cache.remove()
					ydl.download([get_name(file)[-11:]])
	elapsed_time += timer()

	if playlist != 'NA':
		for file in downloaded:
			if not file in file_lst:
				print(f'{YELLOW}{file}{CYAN}을 플레이리스트에서 찾을 수 없습니다. 지우겠습니까? {MAGENTA}(y/N){CYAN}: {RESET}', end='')
				confirm = input()
				if confirm in ['Y', 'y']:
					os.remove(file)

	print(f'{CYAN}걸린 시간: {YELLOW}{elapsed_time}{CYAN}초.{RESET}')

def lst_create(playlist: str) -> None:
	"""`download` 함수로 플레이리스트 폴더가 이미 생성되었다면,
	이 함수가 실행되는 순간 플레이리스트 `playlist`.m3u 파일이 생성됨."""

	lst = glob.glob(f'{playlist}/*')
	if lst != []:
		with open(f'{playlist}.m3u', 'w', encoding='utf8') as m3u:
			for file in lst:
				m3u.write(file + '\n')

def lst_order(playlist: str, method: str = 'suffle') -> None:
	"""플레이리스트 정렬 기능.

	옵션 설명:
	- `method`: 정렬 기준. (`suffle`, `name`, `author`)
		- `suffle`: 셔플 기능. (기본)
		- `name`: 이름 순대로 정렬.
		- `author`: 아티스트 기준.
	"""

	with open(f'{playlist}.m3u', 'r+', encoding='utf8') as m3u:
		lines = [line.strip() for line in m3u.readlines()]
		if method == 'suffle':
			random.shuffle(lines)
		elif method == 'name':
			lines = sorted(lines)
		# TODO author 순대로 정렬
		elif method == 'author':
			pass
		m3u.seek(0)
		m3u.writelines('\n'.join(i for i in lines if i != ''))
		m3u.truncate()

if __name__ == '__main__':
	download('https://www.youtube.com/playlist?list=PLL1k3JLqzzPQjXlpuevJFMswY0NjRWdxf')
	download('https://www.youtube.com/playlist?list=PLL1k3JLqzzPTiU3zihcdIlMSZrgCCwtw2')
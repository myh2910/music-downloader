import os
import glob
import random
from .constants import *

def lst_method(lines: list[str], method: str):
	"""리스트 정렬.

	옵션 설명:
	* `lines`: 정렬할 리스트.
	- `method`: 정렬 기준.
		- `'suffle'`: 셔플 기능.
		- `'name'`: 이름 순대로 정렬.
		- `'artist'`: 아티스트 기준으로 정렬.
	"""
	if method == 'suffle':
		random.shuffle(lines)
	elif method == 'name':
		lines = sorted(lines)
	# TODO: artist 순대로 정렬
	elif method == 'artist':
		pass
	else:
		print(f"{ERROR} 옵션 {INPUT}'{method}'{RESET}이 존재하지 않습니다.")
		return False
	return lines

def lst_create(playlist: str, method: str = 'name', exts: list = ['mp3', 'mp4'], home: str = HOME):
	"""플레이리스트 파일 `playlist`.m3u 생성.

	옵션 설명:
	* `playlist`:  플레이리스트 이름.
	* `method`: 정렬 기준.
	* `exts`: 파일 확장자들을 포함한 리스트.
	* `home`: 플레이리스트를 포함하고 있는 폴더 이름.
	"""
	init()
	if os.path.exists(f'{home}/{playlist}'):
		lst = []
		for ext in exts:
			lst.extend(glob.glob(f'{home}/{playlist}/*.{ext}'))
		lst = lst_method(lst, method)
		if lst:
			if lst == []:
				print(f'{ERROR} 플레이리스트 폴더 {FILE}{playlist}{RESET}가 비어 있습니다.')
			else:
				with open(f'{home}/{playlist}.m3u', 'w', encoding='utf8') as m3u:
					for file in lst:
						m3u.write(os.path.relpath(file, home) + '\n')
				print(f'{FINISHED} 플레이리스트 생성이 완료되었습니다.')
	else:
		print(f'{ERROR} 플레이리스트 폴더 {FILE}{playlist}{RESET}를 찾을 수 없습니다.')

def lst_order(playlist: str, method: str = 'suffle', home: str = HOME):
	"""플레이리스트 정렬 기능.

	옵션 설명:
	* `playlist`:  플레이리스트 이름.
	* `method`: 정렬 기준.
	* `home`: 플레이리스트를 포함하고 있는 폴더 이름.
	"""
	init()
	if os.path.exists(f'{home}/{playlist}.m3u'):
		with open(f'{home}/{playlist}.m3u', 'r+', encoding='utf8') as m3u:
			lines = lst_method([line.strip() for line in m3u.readlines()], method)
			if lines:
				m3u.seek(0)
				m3u.writelines('\n'.join(i for i in lines if i != ''))
				m3u.truncate()
				print(f'{FINISHED} 플레이리스트 정렬이 완료되었습니다.')
	else:
		print(f'{ERROR} 플레이리스트 파일 {FILE}{playlist}.m3u{RESET}을 찾을 수 없습니다.')

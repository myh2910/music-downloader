import glob
import random
from .constants import *

def lst_create(playlist: str, home: str = HOME):
	"""`download` 함수로 플레이리스트 폴더가 이미 생성되었다면,
	이 함수가 실행되는 순간 플레이리스트 `playlist`.m3u 파일이 생성됨.

	옵션 설명:
	* `playlist`:  플레이리스트 이름.
	"""
	if os.path.exists(f'{home}/{playlist}'):
		lst = glob.glob(f'{home}/{playlist}/*')
		if lst == []:
			print(f'{RED}[ERROR] {CYAN}플레이리스트 폴더가 비어 있습니다.{RESET}')
		else:
			with open(f'{home}/{playlist}.m3u', 'w', encoding='utf8') as m3u:
				for file in lst:
					m3u.write(file + '\n')
	else:
		print(f'{RED}[ERROR] {CYAN}플레이리스트 폴더를 찾을 수 없습니다.{RESET}')

def lst_order(playlist: str, method: str = 'suffle', home: str = HOME):
	"""플레이리스트 정렬 기능.

	옵션 설명:
	- `playlist`: 플레이리스트 이름.
	- `method`: 정렬 기준. (`suffle`, `name`, `author`)
		- `suffle`: 셔플 기능. (기본)
		- `name`: 이름 순대로 정렬.
		- `author`: 아티스트 기준.
	"""
	with open(f'{home}/{playlist}.m3u', 'r+', encoding='utf8') as m3u:
		lines = [line.strip() for line in m3u.readlines()]
		if method == 'suffle':
			random.shuffle(lines)
		elif method == 'name':
			lines = sorted(lines)
		# TODO: author 순대로 정렬
		elif method == 'author':
			pass
		else:
			print(f'{RED}[ERROR] {CYAN}존재하지 않는 {MAGENTA}method{CYAN}입니다.{RESET}')
			return False
		m3u.seek(0)
		m3u.writelines('\n'.join(i for i in lines if i != ''))
		m3u.truncate()

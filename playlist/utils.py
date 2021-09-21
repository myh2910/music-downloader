import glob
import random
from .constants import *

def lst_create(playlist: str) -> None:
	"""`download` 함수로 플레이리스트 폴더가 이미 생성되었다면,
	이 함수가 실행되는 순간 플레이리스트 `playlist`.m3u 파일이 생성됨.

	옵션 설명:
	* `playlist`:  플레이리스트 이름."""

	lst = glob.glob(f'{HOME}/{playlist}/*')
	if lst != []:
		with open(f'{HOME}/{playlist}.m3u', 'w', encoding='utf8') as m3u:
			for file in lst:
				m3u.write(file + '\n')

def lst_order(playlist: str, method: str = 'suffle') -> None:
	"""플레이리스트 정렬 기능.

	옵션 설명:
	- `playlist`: 플레이리스트 이름.
	- `method`: 정렬 기준. (`suffle`, `name`, `author`)
		- `suffle`: 셔플 기능. (기본)
		- `name`: 이름 순대로 정렬.
		- `author`: 아티스트 기준."""

	with open(f'{HOME}/{playlist}.m3u', 'r+', encoding='utf8') as m3u:
		lines = [line.strip() for line in m3u.readlines()]
		if method == 'suffle':
			random.shuffle(lines)
		elif method == 'name':
			lines = sorted(lines)
		# TODO: author 순대로 정렬
		elif method == 'author':
			pass
		m3u.seek(0)
		m3u.writelines('\n'.join(i for i in lines if i != ''))
		m3u.truncate()

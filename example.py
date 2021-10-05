from playlist import *

elapsed_time = 0
for url in [
	# 내가 좋아하는 노래
	'https://www.youtube.com/playlist?list=PLL1k3JLqzzPQjXlpuevJFMswY0NjRWdxf',
	# 잔잔한 노래
	'https://www.youtube.com/playlist?list=PLL1k3JLqzzPTiU3zihcdIlMSZrgCCwtw2',
	# 클래식 음악
	'https://www.youtube.com/playlist?list=PL4kYDj2_jcU0FkYiLWFi9_0vfajBFgyPy'
]:
	elapsed_time += download(url, auto=True)

print(f'{FINISHED} 모든 다운로드가 완료되었습니다. 총 {NUMBER}{elapsed_time}{RESET}초가 걸렸습니다.')

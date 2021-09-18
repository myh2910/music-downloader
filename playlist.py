from __future__ import unicode_literals
import youtube_dl
import sys
import glob
import os
from colorama import Fore
import random

CYAN, YELLOW, RESET = Fore.LIGHTCYAN_EX, Fore.LIGHTYELLOW_EX, Fore.RESET

def music_download(url: str, playlist: str = '다운로드', start: int = None, end: int = None, ydl_opts: dict = {}) -> None:
    """
    옵션 설명
    --------
    * `url`: 유튜브 영상 링크.
    * `playlist`: 플레이리스트 이름.

    플레이리스트를 다운로드 하려는 경우
    * `start`: `start`번째 부터 다운로드.
    * `end`: `end`번째 까지 다운로드."""

    replace_chars = False
    if sys.platform == 'win32':
        replace_chars = True

    music_lst = []
    mp3_lst = glob.glob(f'{playlist}/*.mp3')
    webm_lst = glob.glob(f'{playlist}/*.webm')

    playlist_file = f'{playlist}.m3u'
    log_file = f'{playlist}.log'

    with open(log_file, 'w', encoding='utf8') as log:
        for music in mp3_lst:
            if music not in webm_lst:
                log.write(f'youtube {music[-15:-4]}\n')

    ydl_opts = {
        **{
            'format': 'bestaudio/best',
            'outtmpl': playlist + r'/%(title)s-%(id)s.%(ext)s',
            'writethumbnail': True,
            'nooverwrites': True,
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                },
                {'key': 'EmbedThumbnail'},
                {'key': 'FFmpegMetadata'},
            ]
        },
        **ydl_opts
    }

    if playlist != '다운로드':  
        confirm = 'y'
        if os.path.exists(playlist_file):
            confirm = input(f'{CYAN}플레이리스트 파일을 업데이트 하시겠습니까? {YELLOW}(y/N){CYAN}: {RESET}')
        if confirm in 'Yy':
            print(f'{CYAN}플레이리스트에 대한 정보 추출 중...{RESET}')
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                playlist_dict = ydl.extract_info(url, False)
                for video in playlist_dict['entries']:
                    title, id = video.get('title'), video.get('id')
                    if replace_chars:
                        title = ''.join(i if i not in '[]\/:*?"<>|' else '_' for i in title)
                    music_lst.append(f'{playlist}/{title}-{id}.mp3')

            with open(playlist_file, 'w', encoding='utf8') as m3u:
                m3u.write('\n'.join(music_lst))

            start, end = None, None
    if start:
        ydl_opts['playliststart'] = start
    if end:
        ydl_opts['playlistend'] = end
    ydl_opts['download_archive'] = log_file
    print(f'{CYAN}플레이리스트 업데이트 중...{RESET}')
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def lst_create(playlist: str) -> None:
    """`download` 함수로 플레이리스트 폴더가 이미 생성되었다면 (즉, 옵션 `playlist = True`였다면),
    이 함수가 실행되는 순간 플레이리스트 `playlist`.m3u 파일이 생성됨.
    
    VLC media player로 플레이 하는 걸 추천."""

    lst = []
    for ext in ('*.mp3', '*.flac', '*.aac'):
        lst.extend(glob.glob(f'{playlist}/{ext}'))
    if lst != []:
        with open(f'{playlist}.m3u', 'w', encoding='utf8') as m3u:
            for music in lst:
                m3u.write(music + '\n')

def write_lines(file, lines: list[str]) -> None:
    """`file`에 `lines`를 저장."""
    file.writelines('\n'.join(i for i in lines if i != ''))
    file.truncate()

def lst_suffle(playlist: str) -> None:
    """플레이리스트 셔플 기능. 파일 `playlist`.m3u에 있는 음악들을 랜덤으로 셔플."""

    with open(f'{playlist}.m3u', 'r+', encoding='utf8') as m3u:
        lines = [line.strip() for line in m3u.readlines()]
        m3u.seek(0)
        random.shuffle(lines)
        write_lines(m3u, lines)

# TODO author 순대로 정렬
def lst_order(playlist: str, method: str = 'author') -> None:
    """플레이리스트 정렬 기능."""

    with open(f'{playlist}.m3u', 'r+', encoding='utf8') as m3u:
        lines = [line.strip() for line in m3u.readlines()]
        if method == 'author':
            lines = sorted(lines)
        m3u.seek(0)
        write_lines(m3u, lines)

if __name__ == '__main__':
    music_download('https://www.youtube.com/playlist?list=PLL1k3JLqzzPQjXlpuevJFMswY0NjRWdxf', '내가 좋아하는 노래')
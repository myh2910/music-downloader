from __future__ import unicode_literals
import youtube_dl
import sys
import glob
import os
from colorama import init, Fore
from timeit import default_timer as timer
import random

CYAN = Fore.LIGHTCYAN_EX
YELLOW = Fore.LIGHTYELLOW_EX
MAGENTA = Fore.LIGHTMAGENTA_EX
RESET = Fore.RESET

def code(mp3: str) -> str:
    return mp3[-15:-4]
    
def youtube_music(url: str, start: int = None, end: int = None, ydl_opts: dict = {}) -> None:
    """
    옵션 설명
    --------
    * `url`: 유튜브 영상 링크.

    플레이리스트를 다운로드 하려는 경우
    * `start`: `start`번째 부터 다운로드.
    * `end`: `end`번째 까지 다운로드."""

    replace_chars = False
    if sys.platform == 'win32':
        replace_chars = True

    ydl_opts = {
        **{
            'format': 'bestaudio/best',
            'outtmpl': r'%(playlist)s/%(title)s-%(id)s.%(ext)s',
            'writethumbnail': True,
            'quiet': True,
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

    init()
    print(f'{CYAN}플레이리스트에 대한 정보 추출 중...{RESET}')
    start_time = timer()
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        playlist_dict = ydl.extract_info(url, False)
        playlist = playlist_dict['title']
        music_lst = []
        for video in playlist_dict['entries']:
            title, id = video.get('title'), video.get('id')
            if replace_chars:
                title = ''.join(i if i not in '[]\/:*?"<>|' else '_' for i in title)
            music_lst.append(f'{playlist}\\{title}-{id}.mp3')
    end_time = timer()
    print(f'{CYAN}걸린 시간: {YELLOW}{end_time - start_time}{CYAN}초.{RESET}')
 
    if playlist != 'NA':
        confirm = 'y'
        playlist_file = f'{playlist}.m3u'
        if os.path.exists(playlist_file):
            print(f'{CYAN}플레이리스트 파일을 업데이트 하시겠습니까? {MAGENTA}(y/N){CYAN}: {RESET}', end='')
            confirm = input()
        if confirm in ['Y', 'y']:
            with open(playlist_file, 'w', encoding='utf8') as m3u:
                m3u.write('\n'.join(music_lst))
            start, end = None, None
    total = len(music_lst)
    if not start:
        start = 1
    if not end:
        end = total
        
    ydl_opts['outtmpl'] = playlist + r'/%(title)s-%(id)s.%(ext)s'

    mp3_lst = glob.glob(f'{playlist}/*.mp3')
    webp_lst = glob.glob(f'{playlist}/*.webp')

    print(f'{CYAN}플레이리스트 업데이트 중...{RESET}')
    start_time = timer()
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        for i in range(start-1, end):
            music = music_lst[i]
            print(f'{YELLOW}{music}{CYAN} 다운로드 중... {MAGENTA}({i+1}/{total}){RESET}')
            download = True
            if music in mp3_lst:
                if f'{music[:-4]}.webp' not in webp_lst:
                    download = False
            if download:
                try:
                    ydl.download([code(music)])
                except:
                    ydl.cache.remove()
                    ydl.download([code(music)])
    end_time = timer()
    print(f'{CYAN}걸린 시간: {YELLOW}{end_time - start_time}{CYAN}초.{RESET}')

    for music in mp3_lst:
        if not music in music_lst:
            print(f'{YELLOW}{music}{CYAN}을 플레이리스트에서 찾을 수 없습니다. 지우겠습니까? {MAGENTA}(y/N){CYAN}: {RESET}', end='')
            confirm = input()
            if confirm in ['Y', 'y']:
                os.remove(music)

def lst_create(playlist: str) -> None:
    """`download` 함수로 플레이리스트 폴더가 이미 생성되었다면,
    이 함수가 실행되는 순간 플레이리스트 `playlist`.m3u 파일이 생성됨."""

    lst = []
    for ext in ('*.mp3', '*.flac', '*.aac'):
        lst.extend(glob.glob(f'{playlist}/{ext}'))
    if lst != []:
        with open(f'{playlist}.m3u', 'w', encoding='utf8') as m3u:
            for music in lst:
                m3u.write(music + '\n')

def lst_save(file, lines: list[str]) -> None:
    """`file`에 `lines`를 저장."""
    file.writelines('\n'.join(i for i in lines if i != ''))
    file.truncate()

def lst_suffle(playlist: str) -> None:
    """플레이리스트 셔플 기능. 파일 `playlist`.m3u에 있는 음악들을 랜덤으로 셔플."""

    with open(f'{playlist}.m3u', 'r+', encoding='utf8') as m3u:
        lines = [line.strip() for line in m3u.readlines()]
        m3u.seek(0)
        random.shuffle(lines)
        lst_save(m3u, lines)

def lst_order(playlist: str, method: str = 'name') -> None:
    """플레이리스트 정렬 기능."""

    with open(f'{playlist}.m3u', 'r+', encoding='utf8') as m3u:
        lines = [line.strip() for line in m3u.readlines()]
        if method == 'name':
            lines = sorted(lines)
        # TODO author 순대로 정렬
        if method == 'author':
            pass
        m3u.seek(0)
        lst_save(m3u, lines)

if __name__ == '__main__':
    #youtube_music('https://www.youtube.com/playlist?list=PLL1k3JLqzzPQjXlpuevJFMswY0NjRWdxf')
    youtube_music('https://www.youtube.com/playlist?list=PLL1k3JLqzzPTiU3zihcdIlMSZrgCCwtw2')
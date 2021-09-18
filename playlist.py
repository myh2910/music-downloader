from __future__ import unicode_literals
import youtube_dl
from colorama import Fore
import glob
import random

def mp3_download(url: str, start: int = None, end: int = None) -> None:
    """유튜브 영상 .mp3 음악 다운로드. https://github.com/ytdl-org/youtube-dl

    요구사항
    -------
    윈도우즈의 경우
    * `ffmpeg`: 링크 https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z 에서 .7z 파일을 다운로드 한 뒤,
    압축을 푼 상태에서 bin 폴더에 있는 3개의 파일들을 이 파일이 있는 폴더에 저장.
    * `youtube-dl`: 터미널에서 다음 코드를 실행. `pip install youtube-dl`

    옵션 설명
    --------
    * `url`: 유튜브 영상 링크.

    플레이리스트를 다운로드 하려는 경우
    * `start`: `url` 플레이리스트의 `start`번째 부터 시작.
    * `end`: `url` 플레이리스트의 `end`번째 까지 다운로드."""

    ydl_opts = {
        'format': 'bestaudio/best',
        'writethumbnail': True,
        'outtmpl': r'%(playlist)s/%(title)s [%(id)s].%(ext)s',
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            },
            {'key': 'EmbedThumbnail'},
            {'key': 'FFmpegMetadata'},
        ],
        'downloader': [{'continuedl', 'retries'}]
    }
    if start:
        ydl_opts['playliststart'] = start
    if end:
        ydl_opts['playlistend'] = end

    music_lst = []
    playlist = None
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        playlist_dict = ydl.extract_info(url, False)
        for video in playlist_dict['entries']:
            if not playlist:
                playlist = video.get('playlist')
            music_lst.append((video.get('title'), video.get('id')))

    ydl_opts['outtmpl'] = playlist + r'/%(title)s [%(id)s].%(ext)s'
    mp3 = glob.glob(f'{playlist}/*.mp3')
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        for title, id in music_lst:
            if f'{playlist}/{title} [{id}].mp3' not in mp3:
                ydl.download([id])

    if playlist != 'NA':
        yes_or_no = input(f'{Fore.YELLOW}플레이리스트 파일 {Fore.CYAN}{playlist}.m3u{Fore.YELLOW} 을 생성하시겠습니까? (y/n):{Fore.RESET} ')
        if yes_or_no in ['', 'Y', 'y']:
            with open(f'{playlist}.m3u', 'w', encoding='utf8') as m3u:
                m3u.write('\n'.join([f'{playlist}/{title} [{id}].mp3' for title, id in music_lst]))

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

def lst_suffle(playlist: str) -> None:
    """플레이리스트 셔플 기능. 파일 `playlist`.m3u에 있는 음악들을 랜덤으로 셔플."""

    with open(f'{playlist}.m3u', 'r+', encoding='utf8') as m3u:
        lines = m3u.readlines()
        m3u.seek(0)
        random.shuffle(lines)
        m3u.writelines(lines)
        m3u.truncate()

def lst_order(playlist: str) -> None:
    """플레이리스트 정렬 기능. 파일 `playlist`.m3u에 있는 음악들을 알파벳 순으로 정렬."""

    pass

if __name__ == '__main__':
    mp3_download('https://www.youtube.com/playlist?list=PLL1k3JLqzzPQjXlpuevJFMswY0NjRWdxf')
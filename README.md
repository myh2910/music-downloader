# 개요

파이썬 (`youtube-dl`)[https://github.com/ytdl-org/youtube-dl] 패키지를 이용한 유튜브 영상 & 음악 다운로드 프로그램.

# 요구사항

파이썬에서 `youtube-dl`와 `colorama` 패키지들을 설치.

* `pip install youtube-dl colorama`

그리고 아래와 같이 ffmpeg, AtomicParsley, VLC media player을 설치.

## Windows

* https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z 에서 ffmpeg-git-full.7z 파일을 다운로드 한 뒤, 압축을 푼 상태에서 bin 폴더에 있는 .exe 파일들을 playlist.py와 같은 폴더에 저장.
* https://github.com/wez/atomicparsley/releases/latest 에서 AtomicParsleyWindows.zip 파일을 다운로드 한 뒤, 압축을 푼 상태에서 AtomicParsley.exe 파일을 playlist.py와 같은 폴더에 저장.
* https://www.videolan.org/vlc/download-windows.html 에서 VLC media player를 설치.

## Arch Linux

* `sudo pacman -S ffmpeg atomicparsley vlc`

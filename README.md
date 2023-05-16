# music-downloader

Simple music and video downloader based on
[yt-dlp](https://github.com/yt-dlp/yt-dlp). Visit
[here](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md) to see
all the supported websites.

## Requirements

- `pip install -r requirements.txt`
- Install [FFmpeg](https://ffmpeg.org/download.html) and
  [AtomicParsley](https://github.com/wez/atomicparsley).

### Windows

- Unzip `ffmpeg-git-full.7z` from
  <https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z> and move the files
  `ffmpeg.exe` and `ffprobe.exe` from `bin` folder to this repository.
- Unzip `AtomicParsleyWindows.zip` from
  <https://github.com/wez/atomicparsley/releases/latest> and move the file
  `AtomicParsley.exe` to this repository.

### Arch Linux

- `sudo pacman -S ffmpeg atomicparsley`

## Usage

```python
from music_downloader import download

# Download playlist and export to M3U and SMPL
download("https://www.youtube.com/playlist?list=PLOHoVaTp8R7dfrJW5pumS0iD_dhlXKv17", export_to=["m3u", "smpl"])

# Download video in MP4 format
download("https://www.youtube.com/watch?v=DPJL488cfRw", ext="mp4")

# Download playlists in a same directory and export to SMPL
for url in [
    "https://www.youtube.com/playlist?list=OLAK5uy_nK7I5PC-l1wBk51voQI0cXgU1nFRp89gI",
    "https://www.youtube.com/playlist?list=OLAK5uy_mJQgJg3fqotcUcRs5AijgBLfderDqIEwE"
]:
    download(url, outdir="Music/Classical", smpl_outdir="/storage/emulated/0/Music/Classical", export_to=["smpl"])
```

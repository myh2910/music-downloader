"""
music-downloader
================

Download music and video from YouTube and more.

"""
from . import main
from .config import CONFIG

__author__ = "Yohan Min"
__version__ = "1.2.1"

def download(
	url,
	ext="mp3",
	playlist_start=0,
	playlist_end=None,
	playlist_name=None,
	**kwargs
):
	"""
	Download YouTube videos and music.

	Parameters
	----------
	url : str
		YouTube URL.
	ext : str, optional
		Extension of the files to be downloaded.
	playlist_start : int, optional
		Download playlist starting from this index.
	playlist_end : int or None, optional
		Download playlist ending at this index.
	playlist_name : str or None, optional
		Playlist name.

	Returns
	-------
	bool
	"""
	for key, value in kwargs.items():
		CONFIG[key] = value

	timer = main.Timer()

	timer.start()
	extraction_status = main.extract_info(url, ext, playlist_name)
	timer.pause()

	if extraction_status == False:
		return False

	main.init(ext, playlist_start, playlist_end)

	if extraction_status:
		main.export_playlist(CONFIG['export_to'])

	timer.start()
	download_status = main.download_video()
	timer.pause()

	if extraction_status and CONFIG['write_diff']:
		main.write_diff()

	if download_status == False:
		return False
	else:
		timer.end()
		return True

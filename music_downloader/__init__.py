"""
music-downloader
========

Download music and video from YouTube and more.

"""
from . import get
from .config import CONFIG
from .utils import Timer

__author__ = "Yohan Min"
__version__ = "1.2.0"

def download(url, ext="mp3", playlist_start=0, playlist_end=None, playlist_name=None, **kwargs):
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

	timer = Timer()

	timer.start()
	extraction_status = get.extract_info(url, ext, playlist_name)
	timer.pause()

	if extraction_status == False:
		return False

	get.init(ext, playlist_start, playlist_end)

	if extraction_status:
		if CONFIG['write_m3u']:
			get.export_to_m3u()
		if CONFIG['write_smpl']:
			get.export_to_smpl()

	timer.start()
	download_status = get.download_video()
	timer.pause()

	if extraction_status and CONFIG['write_diff']:
		get.write_diff()

	if download_status == False:
		return False
	else:
		timer.end()
		return True

"""
playlist
========

Download YouTube videos and music.

"""
from timeit import default_timer

import colorama

from . import get
from .config import CONFIG
from .utils import print_time


def download(url, ext="mp3", start=0, end=None, playlist=None, **kwargs):
	"""
	Download YouTube videos and music.

	Parameters
	----------
	url : str
		YouTube URL.
	ext : str, optional
		File extension ("mp3", "mp4") of the exported file.
	start : int, optional
		Download playlist starting from this index.
	end : int or None, optional
		Download playlist ending at this index.
	playlist : str or None, optional
		Playlist name.

	Returns
	-------
	bool
	"""
	for key, value in kwargs.items():
		CONFIG[key] = value

	colorama.init()

	elapsed_time = -default_timer()
	playlist = get.extract_info(url, ext, playlist)
	elapsed_time += default_timer()

	if not playlist:
		return False

	get.__init__(ext, start, end)

	if playlist != "NA":
		if CONFIG['export_to_m3u']:
			get.export_to_m3u()
		if CONFIG['export_to_smpl']:
			get.export_to_smpl()

	elapsed_time -= default_timer()
	get.download_video()
	elapsed_time += default_timer()

	get.write_diff()

	print_time(elapsed_time)
	return True

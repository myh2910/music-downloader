"""
Download data from URL and export to playlist files.

"""
from __future__ import unicode_literals

import glob
import os
from datetime import datetime
from timeit import default_timer

import yt_dlp
from yt_dlp.utils import MEDIA_EXTENSIONS, DownloadError, ExtractorError, sanitize_filename

from .config import COLOR, CONFIG, LANG

TEXT = LANG[CONFIG['lang']]
tmp = {}

class Timer:
	def __init__(self):
		self.elapsed_time = 0
		self.end_text = TEXT['download_completed'] % COLOR['num']

	def start(self):
		self.elapsed_time += -default_timer()

	def pause(self):
		self.elapsed_time += default_timer()

	def end(self):
		minutes, seconds = divmod(round(self.elapsed_time), 60)
		hours, minutes = divmod(minutes, 60)

		time_list = [
			TEXT['hours'] % hours,
			TEXT['minutes'] % minutes,
			TEXT['seconds'] % seconds
		]

		if hours > 0:
			idx = 0
		elif minutes > 0:
			idx = 1
		else:
			idx = 2

		print(self.end_text % ' '.join(time_list[idx:]))

def get_ydl_opts(ext):
	"""
	Get YoutubeDL options.

	Parameters
	----------
	ext : str
		File extension.

	Returns
	-------
	bool
	"""
	tmp['ydl_opts'] = CONFIG['ydl_opts']

	if ext in MEDIA_EXTENSIONS.audio:
		tmp['ydl_opts'].update(CONFIG['audio_opts'])
		tmp['ydl_opts']['postprocessors'][0]['preferredcodec'] = ext
		return True

	if ext in MEDIA_EXTENSIONS.video:
		tmp['ydl_opts'].update(CONFIG['video_opts'])
		tmp['ydl_opts']['merge_output_format'] = ext
		return True

	print(COLOR['err'] % TEXT['invalid_extension_error'] % COLOR['name'] % f'"{ext}"')
	return False

def extract_info(url, ext, playlist):
	"""
	Extract video information.

	Parameters
	----------
	url : str
		YouTube URL.
	ext : str
		File extension.
	playlist : str or None
		Playlist name.

	Returns
	-------
	str or False or None
		Extraction status.
	"""
	if not get_ydl_opts(ext):
		return False

	print(TEXT['extracting_data'])

	with yt_dlp.YoutubeDL(tmp['ydl_opts']) as ydl:
		retries = CONFIG['retries']
		while True:
			try:
				playlist_dict = ydl.extract_info(url, False)
				break

			except (KeyboardInterrupt, ExtractorError, DownloadError):
				return False

			except:
				if retries == 0:
					print(COLOR['err'] % TEXT['data_extraction_error'])
					return False
				print(COLOR['err'] % TEXT['retrying_after_error'])
				ydl.cache.remove()
				retries -= 1

	is_playlist = True

	if 'entries' in playlist_dict:
		if not playlist:
			if 'title' in playlist_dict:
				playlist = playlist_dict['title']
			else:
				playlist = playlist_dict['webpage_url_basename']
		tmp['entries'] = playlist_dict['entries']
	else:
		if not playlist:
			is_playlist = False
		tmp['entries'] = [playlist_dict]

	tmp['total'] = len(tmp['entries'])

	if is_playlist:
		tmp['playlist'] = sanitize_filename(playlist)
	else:
		tmp['playlist'] = None

	return tmp['playlist']

def init(ext, start, end):
	"""
	Initialize module.

	Parameters
	----------
	ext : str
		File extension.
	start : int
		Download playlist starting from this index.
	end : int or None
		Download playlist ending at this index.
	"""
	tmp['start'] = start

	if end:
		tmp['end'] = end
	else:
		tmp['end'] = tmp['total']

	tmp['name'], tmp['url'], tmp['norm'] = [], [], []

	for file in tmp['entries']:
		title = sanitize_filename(file.get('title'))
		if tmp['playlist']:
			name = f"{tmp['playlist']}/{title}-{file.get('id')}.{ext}"
		else:
			name = f"{title}-{file.get('id')}.{ext}"

		tmp['name'].append(name)
		tmp['url'].append(file.get('webpage_url'))
		tmp['norm'].append(os.path.normpath(os.path.join(CONFIG['outdir'], name)))

def download_video():
	"""
	Download video.

	Returns
	-------
	False or None
	"""
	if tmp['playlist']:
		path = f"{CONFIG['outdir']}/{tmp['playlist']}/*"
		tmp['ydl_opts']['outtmpl'] = f"{CONFIG['outdir']}/{tmp['playlist']}/\
%(title)s-%(id)s.%(ext)s"
	else:
		path = f"{CONFIG['outdir']}/*"
		tmp['ydl_opts']['outtmpl'] = f"{CONFIG['outdir']}/\
%(title)s-%(id)s.%(ext)s"

	downloaded = [os.path.normpath(file) for file in glob.glob(path)]
	tmp['add'], tmp['pop'] = [], []

	with yt_dlp.YoutubeDL(tmp['ydl_opts']) as ydl:
		if tmp['playlist']:
			print(TEXT['downloading_playlist'] % COLOR['name'] % tmp['playlist'])

		for idx in range(tmp['start'], tmp['end']):
			file = tmp['norm'][idx]
			path = COLOR['file'] % os.path.relpath(file, CONFIG['outdir'])

			if file in downloaded:
				if len(glob.glob(f"{os.path.splitext(file)[0]}.*")) == 1:
					print(TEXT['file_already_exists'] % (path, idx + 1, tmp['total']))
					continue

			print(TEXT['downloading_file'] % (path, idx + 1, tmp['total']))
			tmp['add'].append(file)

			retries = CONFIG['retries']

			while True:
				try:
					ydl.download([tmp['url'][idx]])
					break

				except KeyboardInterrupt:
					for ext in glob.glob(f"{os.path.splitext(file)[0]}.*"):
						os.remove(ext)

					tmp['add'].pop()
					tmp['pop'].append(file)
					return False

				except:
					if retries == 0:
						print(COLOR['err'] % TEXT['file_download_error'])
						for ext in glob.glob(f"{os.path.splitext(file)[0]}.*"):
							os.remove(ext)

						tmp['add'].pop()
						tmp['pop'].append(file)
						break

					print(COLOR['err'] % TEXT['retrying_after_error'])
					ydl.cache.remove()

					for ext in glob.glob(f"{os.path.splitext(file)[0]}.*"):
						os.remove(ext)
					retries -= 1

def export_playlist(exts):
	"""
	Export to playlist files.

	Parameters
	----------
	exts : list of str
		List of playlist formats to export. Currently M3U and SMPL are supported
		only.

		In case of Samsung Music playlist (SMPL), save the generated playlist file
		in Phone -> Playlists, go to Samsung Music settings -> Manage playlists ->
		Import playlists and select your playlist file.
	"""
	for ext in exts:
		file_content = ""

		match ext:
			case "m3u":
				file_content = "\n".join(tmp['name'])
			case "smpl":
				file_content = '{"members": ['
				file_content += ",".join(
					f"""\n\t{{"info": "{CONFIG['smpl_outdir']}/{name}", \
"order": {idx + 1}, "type": 65537}}""" for idx, name in enumerate(tmp['name'])
				)
				file_content += '\n], "sortBy": 4}'
			case _:
				continue

		filename = f"{tmp['playlist']}.{ext}"
		path = os.path.join(CONFIG['outdir'], filename)
		playlist_file = COLOR['file'] % filename

		if os.path.exists(path):
			if CONFIG['auto']:
				print(TEXT['updating_file'] % playlist_file)
				confirm = "y"
			else:
				confirm = input(TEXT['confirm_file_update'] % playlist_file).strip()
		else:
			print(TEXT['generating_file'] % playlist_file)
			confirm = "y"

		if confirm in ["Y", "y"]:
			with open(path, "w", encoding="utf8") as file:
				file.write(file_content)

def write_diff():
	"""
	Write diff file.
	"""
	tmp['del'] = []

	for file in glob.glob(f"{CONFIG['outdir']}/{tmp['playlist']}/*"):
		if os.path.normpath(file) in tmp['norm']:
			continue

		path = COLOR['file'] % os.path.relpath(file, CONFIG['outdir'])
		if CONFIG['auto']:
			print(TEXT['deleting_file'] % path)
			confirm = "y"
		else:
			confirm = input(TEXT['confirm_file_removal'] % path).strip()

		if confirm in ["Y", "y"]:
			os.remove(file)
			tmp['del'].append(file)

	if tmp['add'] or tmp['del'] or tmp['pop']:
		path = os.path.join(CONFIG['outdir'], f"{tmp['playlist']}.diff")
		with open(path, "a", encoding="utf8") as diff:
			curr_time = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
			if curr_time.endswith("00"):
				curr_time = curr_time[:-2]
			else:
				curr_time = "%s:%s" % (curr_time[:-2], curr_time[-2:])

			diff.write(f"@ {curr_time} (+{len(tmp['add'])} -{len(tmp['del'])} \
!{len(tmp['pop'])})\n")
			for file in tmp['add']:
				diff.write(f"+ {os.path.relpath(file, CONFIG['outdir'])}\n")
			for file in tmp['del']:
				diff.write(f"- {os.path.relpath(file, CONFIG['outdir'])}\n")
			for file in tmp['pop']:
				diff.write(f"! {os.path.relpath(file, CONFIG['outdir'])}\n")

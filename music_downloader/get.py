"""
Get YouTube videos and playlist data.

"""
from __future__ import unicode_literals

import glob
import os
from datetime import datetime

import yt_dlp
from yt_dlp.utils import MEDIA_EXTENSIONS, DownloadError, ExtractorError, sanitize_filename

from .config import COLOR, CONFIG, LOCALE

TEXT = LOCALE[CONFIG['locale']]
tmp = {}

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

	print(COLOR['err'] % TEXT['unsupported_extension_error'] % COLOR['name'] % f'"{ext}"')
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

			except KeyboardInterrupt:
				return False

			except (ExtractorError, DownloadError):
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

def __init__(ext, start, end):
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
		tmp['norm'].append(os.path.normpath(os.path.join(CONFIG['output'], name)))

def download_video():
	"""
	Download video.

	Returns
	-------
	False or None
	"""
	if tmp['playlist']:
		path = f"{CONFIG['output']}/{tmp['playlist']}/*"
		tmp['ydl_opts']['outtmpl'] = f"{CONFIG['output']}/{tmp['playlist']}/\
%(title)s-%(id)s.%(ext)s"
	else:
		path = f"{CONFIG['output']}/*"
		tmp['ydl_opts']['outtmpl'] = f"{CONFIG['output']}/\
%(title)s-%(id)s.%(ext)s"

	downloaded = [os.path.normpath(file) for file in glob.glob(path)]
	tmp['add'], tmp['pop'] = [], []

	with yt_dlp.YoutubeDL(tmp['ydl_opts']) as ydl:
		if tmp['playlist']:
			print(TEXT['downloading_playlist'] % COLOR['name'] % tmp['playlist'])

		for idx in range(tmp['start'], tmp['end']):
			file = tmp['norm'][idx]
			path = COLOR['file'] % os.path.relpath(file, CONFIG['output'])

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

def export_to_m3u():
	"""
	Export to M3U playlist.
	"""
	filename = f"{tmp['playlist']}.m3u"
	path = os.path.join(CONFIG['output'], filename)
	playlist_file = COLOR['file'] % filename

	if os.path.exists(path):
		if CONFIG['auto']:
			print(TEXT['updating_file'] % playlist_file)
			confirm = "y"
		else:
			confirm = input(TEXT['file_update_confirmation'] % playlist_file).strip()
	else:
		print(TEXT['generating_file'] % playlist_file)
		confirm = "y"

	if confirm in ["Y", "y"]:
		if not os.path.exists(CONFIG['output']):
			os.mkdir(CONFIG['output'])
		with open(path, "w", encoding="utf8") as file:
			file.write("\n".join(tmp['name']))

def export_to_smpl():
	"""
	Export to Samsung (SMPL) playlist.

	Save the generated playlist file in Phone -> Playlists and then go to Samsung
	Music settings -> Manage playlists -> Import playlists and select your
	playlist file.
	"""
	filename = f"{tmp['playlist']}.smpl"
	path = os.path.join(CONFIG['output'], filename)
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
		if not os.path.exists(CONFIG['output']):
			os.mkdir(CONFIG['output'])

		with open(path, "w", encoding = "utf8") as file:
			file.write('{"members": [')
			file.write(",".join(
				f"""\n\t{{"info": "/storage/emulated/0/{CONFIG['output']}/{name}", \
"order": {idx + 1}, "type": 65537}}""" for idx, name in enumerate(tmp['name'])
			))
			file.write('\n], "sortBy": 4}')

def write_diff():
	"""
	Write diff file.
	"""
	tmp['del'] = []

	for file in glob.glob(f"{CONFIG['output']}/{tmp['playlist']}/*"):
		if os.path.normpath(file) in tmp['norm']:
			continue

		path = COLOR['file'] % os.path.relpath(file, CONFIG['output'])
		if CONFIG['auto']:
			print(TEXT['deleting_file'] % path)
			confirm = "y"
		else:
			confirm = input(TEXT['confirm_file_removal'] % path).strip()

		if confirm in ["Y", "y"]:
			os.remove(file)
			tmp['del'].append(file)

	if tmp['add'] or tmp['del'] or tmp['pop']:
		path = os.path.join(CONFIG['output'], f"{tmp['playlist']}.diff")
		with open(path, "a", encoding="utf8") as diff:
			curr_time = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")

			diff.write(f"@ {curr_time} (+{len(tmp['add'])} -{len(tmp['del'])} \
!{len(tmp['pop'])})\n")
			for file in tmp['add']:
				diff.write(f"+ {os.path.relpath(file, CONFIG['output'])}\n")
			for file in tmp['del']:
				diff.write(f"- {os.path.relpath(file, CONFIG['output'])}\n")
			for file in tmp['pop']:
				diff.write(f"! {os.path.relpath(file, CONFIG['output'])}\n")

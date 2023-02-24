"""
Useful functions for other modules.

"""
import os
import random
from timeit import default_timer

from .config import COLOR, CONFIG, LOCALE

TEXT = LOCALE[CONFIG['locale']]

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

def sort_lines(lines, method):
	"""
	Sort lines.

	Parameters
	----------
	lines : list of str
		List of lines to sort.
	method : str
		Sorting method ("suffle", "name", "artist").

	Returns
	-------
	lines : list of str
		The sorted lines.
	"""
	match method:
		case "suffle":
			random.shuffle(lines)
		case "name":
			lines = sorted(lines)
		case _:
			print(COLOR['err'] % TEXT['no_sort_method_error'] % COLOR['name'] % f'"{method}"')
			return False
	return lines

def sort_playlist(playlist, method="suffle"):
	"""
	Sort a playlist file.

	Parameters
	----------
	playlist : str
		Playlist name.
	method : str, optional
		Playlist sorting method.
	"""
	print(TEXT['sorting_playlist'])

	path = os.path.join(CONFIG['output'], f"{playlist}.m3u")

	if not os.path.exists(path):
		print(COLOR['err'] % TEXT['no_playlist_file_error'] % COLOR['file'] % f"{playlist}.m3u")
		return

	with open(path, "r+", encoding="utf8") as file:
		lines = sort_lines([line.strip() for line in file.readlines()], method)

		if not lines:
			print(COLOR['err'] % TEXT['empty_playlist_error'])
			return

		file.seek(0)
		file.writelines("\n".join(i for i in lines if i != ""))
		file.truncate()

		print(TEXT['sorting_completed'])

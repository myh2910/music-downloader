"""
The configuration file.

Options
-------
ydl_opts : dict
	Options for the downloader.
audio_opts : dict
	Audio options.
video_opts : dict
	Video options.
auto : bool
	Whether to skip user confirmation and automate all processes.
write_m3u : bool
	Whether to export playlist to an .m3u file.
write_smpl : bool
	Whether to export playlist to an .smpl file.
write_diff : bool
	Whether to write a log file.
retries : int
	The number of retries.
output : str
	The directory in which files will be downloaded.
lang : str
	Currently supports English and Korean only.

"""
import colorama
from colorama import Fore

colorama.init()

COLOR = {
	'file': "{}%s{}".format(Fore.LIGHTCYAN_EX, Fore.RESET),
	'num': "{}%s{}".format(Fore.LIGHTGREEN_EX, Fore.RESET),
	'name': "{}%s{}".format(Fore.LIGHTMAGENTA_EX, Fore.RESET),
	'err': "{}[ERROR]{} %s".format(Fore.LIGHTRED_EX, Fore.RESET)
}

CONFIG = {
	'ydl_opts': {
		'ignore_no_formats_error': True,
		'writethumbnail': True,
		'allow_playlist_files': False,
		'cachedir': False,
		'retries': 3,
		'fragment_retries': 3,
		'extractor_args': {
			'youtube': {'lang': ["ko"]}
		}
	},
	'audio_opts': {
		'format': "bestaudio/best",
		'postprocessors': [
			{
				'key': "FFmpegExtractAudio",
				'preferredcodec': "mp3",
				'preferredquality': "320"
			},
			{'key': "FFmpegMetadata"},
			{'key': "EmbedThumbnail"}
		]
	},
	'video_opts': {
		'format': "bestvideo+bestaudio/best",
		'merge_output_format': "mp4",
		'postprocessors': [
			{'key': "FFmpegMetadata"},
			{'key': "EmbedThumbnail"}
		]
	},
	'auto': True,
	'write_m3u': True,
	'write_smpl': False,
	'write_diff': True,
	'retries': 2,
	'output': "Music",
	'lang': "ko"
}

LANG = {
	'en': {
		'hours': "%dh",
		'minutes': "%dm",
		'seconds': "%ds",
		'extracting_data': ":: Extracting URL data...",
		'downloading_playlist': ":: Downloading playlist %s...",
		'downloading_file': ":: Downloading file %s... (%d/%d)",
		'updating_file': ":: Updating playlist file %s...",
		'generating_file': ":: Generating playlist file %s...",
		'deleting_file': ":: Deleting file %s...",
		'sorting_playlist': ":: Sorting playlist...",
		'confirm_file_update': ":: Update playlist file %s? [y/N] ",
		'confirm_file_removal': ":: Cannot find file %s from playlist. Delete? [y/N] ",
		'file_already_exists': ":: File %s already exists. (%d/%d)",
		'download_completed': ":: Download completed. Elapsed time: %s.",
		'sorting_completed': ":: Playlist sorting completed.",
		'unsupported_extension_error': "File extension %s is not supported.",
		'data_extraction_error': "Unable to extract URL data.",
		'retrying_after_error': "Error occurred. Retrying...",
		'file_download_error': "Unable to download file.",
		'no_sort_method_error': "Option %s does not exist.",
		'no_playlist_file_error': "Cannot find playlist file %s.",
		'empty_playlist_error': "Playlist is empty."
	},
	'ko': {
		'hours': "%d시간",
		'minutes': "%d분",
		'seconds': "%d초",
		'extracting_data': ":: URL 정보 추출 중...",
		'downloading_playlist': ":: 플레이리스트 %s 다운로드 중...",
		'downloading_file': ":: 파일 %s 다운로드 중... (%d/%d)",
		'updating_file': ":: 플레이리스트 파일 %s 업데이트 중...",
		'generating_file': ":: 플레이리스트 파일 %s 생성 중...",
		'deleting_file': ":: 파일 %s 삭제 중...",
		'sorting_playlist': ":: 플레이리스트 정렬 중...",
		'confirm_file_update': ":: 플레이리스트 파일 %s을 업데이트 하시겠습니까? [y/N] ",
		'confirm_file_removal': ":: 파일 %s을 플레이리스트에서 찾을 수 없습니다. 지우겠습니까? [y/N] ",
		'file_already_exists': ":: 파일 %s이 이미 존재합니다. (%d/%d)",
		'download_completed': ":: 다운로드가 완료되었습니다. 총 %s가 걸렸습니다.",
		'sorting_completed': ":: 플레이리스트 정렬이 완료되었습니다.",
		'unsupported_extension_error': "파일 확장자 %s는 지원되지 않습니다.",
		'data_extraction_error': "URL 정보 추출이 불가능합니다.",
		'retrying_after_error': "에러 발생. 다시 시도 중...",
		'file_download_error': "파일을 다운로드할 수 없습니다.",
		'no_sort_method_error': "옵션 %s이 존재하지 않습니다.",
		'no_playlist_file_error': "플레이리스트 파일 %s을 찾을 수 없습니다.",
		'empty_playlist_error': "플레이리스트가 비어 있습니다."
	}
}

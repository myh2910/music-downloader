from playlist import *

# 내가 좋아하는 노래
download('https://www.youtube.com/playlist?list=PLL1k3JLqzzPQjXlpuevJFMswY0NjRWdxf')
# 잔잔한 노래
download('https://www.youtube.com/playlist?list=PLL1k3JLqzzPTiU3zihcdIlMSZrgCCwtw2')
# SAT Short & Sweet (6-15)
for id in [
	#06 'JVHaHwT1nb0', 'JOPK-fmdV5o', 'pPXt-NWUwUA', '-NRMORh0tRA',
	#07 'mjwSRd686bI', 'uIzaL3ZHvPg', 'QU5z3lZBb9w', 'JTNPQMXKeWE',
	#08 '4bmMBk1qpDA', 'IPzkkqogeXo', 'Z3uj6blw8kQ', 'amrLGxiT-7E',
	#09 'shPLLQ4YFUw', 'k-yOFAjrwGI', 'NamzPa2SbAg', 'ZiY7CDu0KWQ',
	#10 'LNMR8swHENk', '78UCbVvEZlg', 'j9vOZnPrTWY', 'YGU6E-GBtvY',
	#11 'qW2aCxZ5w2k', 'fMMoJEMP3Fw', '45CHOc-4l8w', 'T7XXXe__vxA',
	#12 '9EUpreoT2SY', 'ZNGlafycDiY', 'MesrN1Ui_uw', '1hYUdQMfv60',
	#13 '_gsm6CuRxtc', 'c_Yz2MYfvHU', '03H7ktD2sPc',
	#14 '8dlkqXP5vKU', 'B3gJVLt5CG4', 'h4UXuwHD4xs', '81qnCthyw7s',
	#15 'DS3VkE6Fozw', 'sUydSb-HuRg', '13_-yKJbQlg', 'jvV-oNJ9k-k'
]:
	download(id, 'mp4')

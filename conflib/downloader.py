#!/usr/bin/env python3

import imp
import os
import sys
import urllib.request

from conflib import ByteSize

try:
	#from bs4 import BeautifulSoup
	import requests
	from requests import Response
	import tqdm
except Exception as e:
	print(e)
	sys.exit(1)


def get_terminal_width() -> int:
	try:
		width = int(os.get_terminal_size()[0])
	except:
		width = 80
	return width

def clean_line():
	"""Limpar a linha do console"""
	print(' ' * get_terminal_width(), end='\r')


def download(url: str, output_file: str, verbose: bool=True) -> bool:
	if os.path.isfile(output_file):
		print(f'[PULANDO] ... {output_file}')
		return True

	if len(output_file) > 20:
		show_filename = f'{output_file}[0:20]...'
	else:
		show_filename = output_file

	req: Response = requests.get(url, stream=True)
	#req = requests.get(url, stream=True)
	
	try:
		file_size = int(req.headers['Content-Length'])
	except:
		file_size = int(0)


	chunk = 1
	chunk_size = 1024
	num_bars = int(file_size / chunk_size)
	clean_line()
	# unit='KB'

	try:
		with open(output_file, 'wb') as fp:
			for chunk in tqdm.tqdm(
				req.iter_content(chunk_size=chunk_size), total=num_bars, unit='KB', desc=show_filename,leave=True # progressbar stays
				):
				fp.write(chunk)

	except Exception as e:
		print(e)
		return False
	else:
		return True

    

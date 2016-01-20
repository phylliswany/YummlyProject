import sys
from downloader import Downloader
from parser import Parser
import time
from random import random

if __name__=="__main__":
	buffer = [sys.argv[1]]
	while len(buffer) > 0:
		url = buffer.pop()
		d = Downloader()
		html = d.download(url)
		
		if html is not None:	
			p = Parser()
			urls = p.parse(html)
			p.save()
			if len(buffer) < 100000:
				buffer = buffer + urls
			time.sleep(3*random())

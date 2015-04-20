#!/usr/bin/python
# CS51 Final Project 2015 
# Nathaniel Burbank 
#   

### External Librarys 
from bs4 import BeautifulSoup 
import urllib2
import re
import codecs
import pickle
import sys 

### Basic file functions ### 

def write_file_utf(data, filename):
	print "Writing data to", filename, "...",   
	writefile = codecs.open(filename, 'w', 'utf-8')
	writefile.write(data)
	writefile.close()
	print ".",
	print "done" 

def append_file_utf(data, filename):
	print "appending data to", filename, "...",
	try: 
		writefile = codecs.open(filename, 'a', 'utf-8')
		writefile.write(data)
		writefile.close()
		print "done"
		
	except IOError as e:
		print "Unable to find file", filename
		raise NameError('File does not exist...') 


def pickle_data(data, filename):
	print "Pickleing data to", filename, "...",
	file = open(filename, 'wb')
	pickle.dump(data, file)
	file.close()
	print "done" 

def load_pickle(filename):
	print "Unpickling data from file", filename, "...", 
	file = open(filename, 'rb')
	data = pickle.load(file)
	file.close()
	print "done" 
	return data

### Main functions 

def download_webpage(url): 
	print "Downloading webpage source for", url, "...", 
	page = urllib2.urlopen(url)
	pagedata = page.read()
	print "done"
	return pagedata
	
	
def page_pre_processer (pagedata):
	return pagedata 
	
def tokenizer (pagedata):
	soup = BeautifulSoup(pagedata)
	token_list = soup.find_all('div')  
	print str(len(token_list)) + " tokens identified"
	return token_list

def local_classifiers (token_list):
	score_list = []
	for token in token_list:
		plain_text = token.get_text()
		score_list.append(len(plain_text))
	return score_list
		  

def global_optimizer (score_list):
	div_id = score_list.index(max(score_list))
	print div_id
	return div_id

def token_selector (score_list_max, div_list):
	return div_list[score_list_max]
	
def article_post_processer(div):
	return div.get_text()


def training (urllist):
	return urllist 
	

if __name__ == '__main__':

	raw_html = download_webpage(sys.argv[1])
	processed_webpage = page_pre_processer(raw_html)
	token_list = tokenizer (processed_webpage) 
	score_list = local_classifiers(token_list)
	score_list_max = global_optimizer(score_list)
	article_processed = article_post_processer(token_list[score_list_max])
	print article_processed
	
	
		
	
	
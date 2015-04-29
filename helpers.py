#!/usr/bin/python

import urlparse
import codecs
import pickle
import sys 

debug = False


### URL functions 

def is_url(string): 
	parts = urlparse.urlsplit(string)  
	if not parts.scheme or not parts.netloc:  
		return False 
	else: 
		return True 

def filename_from_url(url):
	# Extracts final part of a url 
	# ...nyregion/etan-patz-trial-jury.html ->  "etan-patz-trial-jury.html"
	if url[-1] == "/": url = url[:-1]
	filename = url.split('/')[-1].split('#')[0].split('?')[0]
	if not (filename.endswith('html') or filename.endswith('htm')): 
		filename += ".html"
	return filename 

def clean_url(url):
	# Removes extraneous query  strings from urls 
	# ...nyregion/etan-patz-trial-jury.html?hp&action=click -> nyregion/etan-patz-trial-jury.html 
	url_lst = url.split('/')
	url_lst[-1] = url.split('/')[-1].split('#')[0].split('?')[0]
	clean_url = '/'.join(url_lst)
	return clean_url
	
def get_title_from_url(url):
	# Converts urls into a title like this: 
	# "...nyregion/etan-patz-trial-jury.html ->  "Etan Patz Trial Jury"
	if url[-1] == "/": url = url[:-1]
	base = url.split('/')[-1].split('#')[0].split('?')[0].split('.')[0]
	title = re.sub(r"([-_])", r" ", base) 
	return title.title()
	

### Basic file functions ### 

def write_file_utf(data, filename):
	if (debug):  print "Writing data to", filename, "...",   
	writefile = codecs.open(filename, 'w', 'utf-8')
	writefile.write(data)
	writefile.close()
	if (debug): print ".",
	if (debug): print "done" 

def read_file_utf(filename):
	if (debug):  print "Reading data from", filename, "...",   
	readfile = codecs.open(filename, 'r', 'utf-8')
	data = readfile.read()
	readfile.close()
	if (debug):  print ".",
	if (debug): print "done" 
	return data


def append_file_utf(data, filename):
	if (debug):  print "appending data to", filename, "...",
	try: 
		writefile = codecs.open(filename, 'a', 'utf-8')
		writefile.write(data)
		writefile.close()
		print "done"
		
	except IOError as e:
		print "Unable to find file", filename
		raise NameError('File does not exist...') 


def pickle_data(data, filename):
	if (debug): print "Pickleing data to", filename, "...",
	file = open(filename, 'wb')
	pickle.dump(data, file)
	file.close()
	if (debug): print "done" 

def load_pickle(filename):
	print "Unpickling data from file", filename, "...", 
	file = open(filename, 'rb')
	data = pickle.load(file)
	file.close()
	print "done" 
	return data

	


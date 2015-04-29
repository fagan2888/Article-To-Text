#!/usr/bin/python

import urlparse
import codecs
import pickle
import sys 

debug = True

### Basic file functions ### 
def write_file_utf(data, filename):
	if (debug):  print "Writing data to", filename, "...",   
	writefile = codecs.open(filename, 'w', 'utf-8')
	writefile.write(data)
	writefile.close()
	if (debug): print ".",
	if (debug): print "done" 


def is_url(string): 
	parts = urlparse.urlsplit(string)  
	if not parts.scheme or not parts.netloc:  
		return False 
	else: 
		return True 


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

	


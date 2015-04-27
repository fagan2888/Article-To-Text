#!/usr/bin/python

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

def save_article_links_dict(article_links_redirects_dict, year):
    article_data_filename = './studyhacks_article_links_redirects_dict_' + year + '.data'
    try:
        pickle_data(article_links_redirects_dict, article_data_filename)
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise 

def load_article_links_dict(year):
    article_data_filename = './studyhacks_article_links_redirects_dict_' + year + '.data'
    try:
        print "Loading article data from", article_data_filename, "..."
        article_links_redirects_dict = load_pickle(article_data_filename)
        print "Done" 
    except IOError:
        article_links_redirects_dict = {}
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise 
    
    return article_links_redirects_dict
    

    
#!/usr/bin/python

import urlparse
import codecs
import pickle
import sys 
import re 

debug = False

def clear_screen(): 
	print(chr(27) + "[2J")  

def unique (token_list):
	# Returns list with unique values only 
	unique_tokens = []
	[unique_tokens.append(item) for item in token_list if item not in unique_tokens]
	return unique_tokens 
		

def stem(word):
# Super simple word stemmer, that removes common English suffixes. 
# Obviously not perfect and could be (vastly!) improved, but that is out scope for now. 
	for suffix in ['ing','ly','ed','ious','ies','ive','es',"'s",'ment']:
		if word.endswith(suffix):
			return word[:-len(suffix)]
	
	return word 

def tokenize_string (text):
	"""
	Very rudimentary tokenizer. Converts a sentence such as this:
	Hey!! You can't use those. Those are Jack's  bowling balls! 
	Into a list of unique, stemmed words like this: 
	['hey', '!', 'you', "can't", 'use', 'those', '.', 'are', 'jack', 'bowl', 'balls']

	Unlike many stemming functions, I decided to explicitly include punctuation, 
	as I think it may have meaning in this context. 

	"""

	text_with_punc = re.sub(r"([.!,;?])", r" \1 ", text) 
	#Add spaces to certain puncuation so that it's preserverd in the next step

	words = re.sub("[^\w.!,;?']", " ", text_with_punc).lower().split()
	# Normalize spaces, lowercase everything, then convert string to list of words 
	
	stemmed_words = []
	[stemmed_words.append(stem(word)) for word in words]
	
	return unique(stemmed_words)


def print_div (article_div):

	t = len(article_div)
	i = 1 
			
	for child in article_div.contents:
		if isinstance(child, NavigableString):
			print "####"
			print "%d of %d" % (i,t) 
			print len(child.string)
			print child.string
		else:
			print "####"
			print "%d of %d" % (i,t) 
			print child
		i += 1 


def training_invariants_met(lst,list_len,clean_article_div,token_dic,valid_categories):

	if (debug): print "Num of children: " + str(len(clean_article_div))
	if (debug): print "Expected number of classifcations" + str(list_len)
	if (debug): print "Number of classifcations " + str(len(lst)) 
	if (debug): print "Number of keys " + str(len(token_dic.keys()))  

	invariants_met = True 
	for tag in lst:
		if tag.lower() not in valid_categories.keys(): 
			invariants_met = False 

	if len(lst) != list_len or len(clean_article_div) != len(lst):
		invariants_met = False 

	return invariants_met


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
	if (debug): print "Unpickling data from file", filename, "...", 
	file = open(filename, 'rb')
	data = pickle.load(file)
	file.close()
	if (debug): print "done" 
	return data

	


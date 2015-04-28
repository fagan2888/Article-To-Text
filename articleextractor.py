#!/usr/bin/python
# CS51 Final Project 2015 
# Nathaniel Burbank 
#   

### External Librarys 
from bs4 import BeautifulSoup, NavigableString
import urllib2
import html2text
import sys 
import codecs
import pickle
import sys 
import re 


## Other sections of the project 
import Helpers
import NaiveBayes 
import PreProcessor

debug = True


### Helper functions

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
	Simple tokenizer. Converts a sentence such as this:
	"Hey!! You can't use those. \n Those are Jack's  bowling balls!" 
	into a list of unique words like this: 
	['hey', '!', 'you', "can't", 'use', 'those', '.', 'are', 'jack', 'bowl', 'balls']

	"""
	text_with_punc = re.sub(r"([.!,;?])", r" \1 ", text) 
	#Add spaces to certain puncuation so that it's preserverd in the next step
	words = re.sub("[^\w.!,;?']", " ", text_with_punc).lower().split()
	# Normalize spaces, lowercase everything, then convert string to list of words 
	stemmed_words = []
	[stemmed_words.append(stem(word)) for word in words]
	return unique(stemmed_words)


### Main functions 

def download_webpage(url): 
	if (debug): print "Downloading webpage source for", url, "...", 
		
	#make an url opener that can handle cookies so this works with NYtimes... 
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
	
	#read in the site
	response = opener.open(url)
	html = response.read()
	
	if (debug): print "done"
	return html
	

def page_pre_processer (pagedata):
	processed = re.sub(r"<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>","",pagedata, re.M )
	# Removes Javascript from page # 
	
	soup = BeautifulSoup(pagedata)
	token_list = PreProcessor.tokenizer (soup) 
	score_list = PreProcessor.classifier(token_list, soup)
	
	score_list_max = score_list[0][0]
	article_processed = token_list[score_list_max]
	
	return article_processed

def tokenizer (article_div):


	# Remove tags that contain no content 
	empty_tags = article_div.findAll(lambda tag: tag.is_empty_element or not tag.contents and (tag.string is None or not tag.string.strip()))
	[empty_tag.extract() for empty_tag in empty_tags]

	# Remove empty navigable strings 
	for child in article_div.children:
		if isinstance(child, NavigableString):
			if (len(child.string) <= 1): child.extract() 


	# Remove attibutes from html tags 
	for tag in article_div():
		tag.attrs = None

	i = 0 
	tokeninzed = {}

	for child in article_div.children:
		child_tokeninzed = []
		if not isinstance(child, NavigableString):
			#print child.prettify()
			#print "**output***"
			parrent_tag = "<" + str(child.name) + ">"
			child_tokeninzed.append(parrent_tag)
			for tag in child.find_all(True):
				tag = "<" + str(tag.name) + ">"
				child_tokeninzed.append(parrent_tag) 


			content = child.get_text().strip().lower()
			child_tokeninzed += tokenize_string(content)

			#for string in child.stripped_strings:
			#	text = text + " " + string.lower() 

			
		else: # is NavigableString 
			string = tokenize_string(child.string)
			child_tokeninzed = ["<NS>"] + string

		tokeninzed[i] = unique(child_tokeninzed)
		i += 1


	return tokeninzed


def bayes_processer (tokenized_dic, b_dic):
	scores = {}
	for key in tokenized_dic.keys():
		scores[key] = NaiveBayes.guess(tokenized_dic[key],b_dic)
	return scores 


def article_extractor (scores, article_div, headline):


	i = 0 
	for child in article_div:
		guess = NaiveBayes.extract_Winner(scores[i]) 
		print str(i) + " " + guess 
		# print child.get_text()
		if guess == "headline":
			headline = child.get_text
		elif guess != "article":
			child.extract()
		i += 1 

	return article_div

def token_selector (score_list_max, div_list):
	return div_list[score_list_max]
	
def article_post_processer(article_div):
	# Still todo
	
	VALID_TAGS = ['strong', 'em', 'p', 'ul', 'li', 'br', 'b', 'a', 'i'] 

	for tag in article_div.findAll(True):
		if tag.name not in VALID_TAGS:
			tag.hidden = True

	print "final"
	print len(article_div)
	return html2text.html2text(article_div.prettify()) 
	

def training (article_div, tokeninzed_dic, b_dic):
	i = 0 
	for child in article_div.children:
		if not isinstance(child, NavigableString):
			b_dic = training_loop(child.get_text(),tokeninzed_dic[i], b_dic)
		else:
			b_dic = training_loop(child.string,tokeninzed_dic[i], b_dic)
		i += 1 

	print b_dic
	return b_dic 



def training_loop(article_sub, tokens, b_dic):

	cmd = ""
	print(chr(27) + "[2J")
	print article_sub
	print "###########################"
	print tokens 


	valid_categories = {'h': 'headline', 'a': 'article', 'd': 'dateline', 'b':'byline', 's':'skip', 'o':'spam'} 

	while cmd != "s":

		cmd = raw_input ("\n Enter h for headline, a for article, d for date, b for byline, o for anything else, s to skip:")

		cmd = cmd.lower() 

		if cmd == "s": break ##first check to see if q was entered
		
		elif cmd in valid_categories.keys():
				b_dic = NaiveBayes.train(tokens,valid_categories[cmd], b_dic)
				data = "\nb_dic = NaiveBayes.train(" + str(tokens) + ",'" + valid_categories[cmd] + "',b_dic)"
				Helpers.append_file_utf(data, "training.py")
				break 
		
		else: print cmd, " is an invalid command. Please try again, or enter s to skip this section ."

	return b_dic



	

if __name__ == '__main__':

	if len(sys.argv) < 2: 
		print "No url specified" 

	elif len(sys.argv) == 2:
		raw_html = download_webpage(sys.argv[1]) 
		#raw_html = Helpers.read_file_utf(sys.argv[1])
		article_div = page_pre_processer(raw_html)
		tokenized_dic = tokenizer(article_div)
		b_dic = Helpers.load_pickle('bdic.data')
		scores = bayes_processer(tokenized_dic, b_dic)
		article_div_processed = article_extractor (scores, article_div, 'test headline')
		print article_post_processer(article_div)

	elif len(sys.argv) == 3:
		raw_html = download_webpage(sys.argv[1]) 
		article_div = page_pre_processer(raw_html)
		tokenized_dic = tokenizer(article_div)
		try:
			b_dic = Helpers.load_pickle('bdic.data')
		except: 
			b_dic = {}
		b_dic = training (article_div, tokenized_dic, b_dic)
		Helpers.pickle_data(b_dic, 'bdic.data') 

	 

	



	






	



		
	
		
	

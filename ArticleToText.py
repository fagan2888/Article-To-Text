#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Article To Text
# CS51 Final Project 2015 
# Nathaniel Burbank 
# 

# Standard Libraries 
import urllib2
import sys 
import codecs
import sys 
import re 

# External Libraries 
from bs4 import BeautifulSoup, NavigableString, Comment
import html2text

# Other modules of the project 
import Training
import Helpers
import NaiveBayes 
import DivExtractor

# Global variables 

help_message = \
"""
ArticleToText 
Harvard CS51 Final Project 2015 
Nathaniel Burbank 

Usage: ./ArticleToText.py url [options] 

Options:
  -f, --file 	Save output to .txt file in working directory.  
  -h, --help    Show this help message and exit.
  -d, --debug	Print debugging information while running.
  -r, --rebuild	Rebuild the Bayes data structure based on the webpages 
  				in the training directory and training.tsv file.
  -t, --train	Run supervised trainer on submitted url. Save results to 
  				training directory and Bayes data structure.  
  -u, --unit	Run unit tests and exit.
  
"""

debug = False

valid_categories = \
{'h': 'headline', 'a': 'article', 'd': 'dateline', 'b':'byline', 's':'spam'}
bdic_file = "bdic.data" 

### Main functions ### 

def download_webpage(url): 
	'''
	Downloades webpage using urllib2 and returns unprocessed html.  
	''' 
		
	if (debug): print "Downloading webpage source for", url, "...", 
		
	#make an url opener that can handle cookies so this works with NYtimes... 
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
	opener.addheaders = [('User-agent', 'Mozilla/5.0')]
	
	#read in the site
	response = opener.open(url)
	raw_html = response.read()
	
	if (debug): print "done"
	return raw_html
	
def soupify(raw_html):     
	"""     
	Parses raw html into BeautifulSoup data structure. Also removes html 
	comments, and javascript and style tags.
	"""     
	
	soup = BeautifulSoup(raw_html)

	# just delete javascript and style tags 
	for tag in soup.findAll(['script','style']):
		tag.decompose()

	# Remove html comments as well 
	for element in soup(text=lambda text: isinstance(text, Comment)):
		element.extract()

	return soup 

def make_article_dic(soup, url):
	"""
	Returns a dictionary object with metadata about the article. For now, just
	contains the url and page title, but plan to extend further with date and
	other attributes if I have time. 
	"""

	article_dic = {}
	article_dic[url] = url 
	
	try:
		article_dic['headline'] = soup.title.string
	except:
		article_dic['headline'] = Helpers.get_title_from_url(url)

	return article_dic 

def article_div_extractor(soup):
	"""
	Returns a pointer to the div that (likely) contains the article text within
	the BeautifulSoup data structure. Guess is based on a set of text density 
	heuristics hard-coded within the DivExtractor module.  
	"""

	# Generate a list of potential article divs
	div_list = DivExtractor.tokenizer(soup) 

	# Return the div with the highest "article likeness score"
	article_div_id = DivExtractor.article_selector(div_list, soup)
	
	# Extract out the article div elements from within the Beautifulsoup data
	# structure, and discard the rest of the web page
	return div_list[article_div_id].extract()


def article_div_pre_processer(article_div):
	'''
	Removes tags that contain no text, and extraneous white space within the 
	article div. Note, changes are made destructively on beautifulsoup’s data 
	structure, and the article_div variable is just (effectively) a pointer. 
	''' 

	# Remove tags that contain no content 
	empty = lambda tag: tag.is_empty_element or \
	not tag.contents and (tag.string is None or not tag.string.strip())
	
	empty_tags = article_div.findAll(empty)
	[empty_tag.decompose() for empty_tag in empty_tags]

	# Remove empty navigable strings 

	for x in range(0,3):
		for child in article_div:
			if isinstance(child, NavigableString):
				if (len(child.string.strip()) <= 1):
					child.extract()
	
	# The x in range loop bit above is a bit of a hack. I'm not sure why I
	# need to do multiple iterations over the list of children to find all of
	# the empty navigable strings, but if I don't, some are left behind and it
	# causes problems further below. Might be a bug in BeautifulSoup.

	return article_div 

def article_tokenizer(clean_article_div):
	"""
	Tokenizes each html object one level below the article div in the html tree. 
	Token list includes steamed words, tag names, and html class attributes 
	(if any.)  This function returns a dictionary of token lists keyed off 
	of the beautiful soup child objects.
	""" 

	def get_classes(tag):
		classes = []
		if 'class' in tag.attrs: 
			for c in tag.attrs['class']:
				classes.append("[" + c + "]")
		return classes 
	
	token_dic = {}
	for child in clean_article_div.contents:
		child_tokens = []
		#is NavigableString  
		if isinstance(child, NavigableString): 
			string = Helpers.tokenize_string(child.string)
			child_tokens = ["<NS>"] + string

		else: #Child is tag, and can have it's own children 
			
			# Build list of html tags in the child, including the parrent tag 
			child_tags = [("<" + str(child.name) + ">")]  
			child_classes = get_classes(child)
			
			#Recursively iterate though child tags  
			for tag in child.find_all(True):
				tag_name = "<" + str(tag.name) + ">"
				child_tags.append(tag_name) 
				child_classes += get_classes(tag)

			child_text = child.get_text().strip()
			child_tokens += Helpers.unique(child_tags) + \
			Helpers.unique(child_classes) + Helpers.tokenize_string(child_text)

		token_dic[child] = child_tokens

	return token_dic

def get_bayes_scores(token_dic, b_dic):
	scores = {}
	for child in token_dic.keys():
		scores[child] = NaiveBayes.guess(token_dic[child],b_dic)

	return scores 

def filter_article_div(score_dic, article_div, article_dic):

	for x in range(0,3):
		for child in article_div.contents: 
			rankings = score_dic[child]
			guess = NaiveBayes.extract_Winner(rankings) 
			if guess != "article":
				child.extract()
		
	return article_div

def article_post_processer(article_div,article_dic):

	headline = article_dic['headline']
	hl = BeautifulSoup("<h1>" + headline + "</h1>")
	article_div.insert(0,hl)
		
	valid_tags = ['strong', 'em', 'p', 'ul', 'li', 'br', 'b', 'a', 'i'] 

	# Remove all attibutes from html tags 
	for tag in article_div():
		tag.attrs = None

	for tag in article_div.findAll(True):
		if tag.name not in valid_tags:
			tag.hidden = True

	return html2text.html2text(article_div.prettify())
	#return article_div.prettify()

def get_article_text(soup, url):
	
	article_dic = make_article_dic(soup,url)
	article_div = article_div_extractor(soup)
	clean_article_div = article_div_pre_processer (article_div)
	token_dic = article_tokenizer(clean_article_div) 
	b_scores = get_bayes_scores(token_dic, b_dic)
	article_div_processed = filter_article_div \
		(b_scores, clean_article_div, article_dic)				
	#Helpers.clear_screen() 
	return article_post_processer(article_div_processed,article_dic)


if __name__ == '__main__':
	'''
	Main program loop. Determines which flags were submitted, checks that 
	url is valid and a number of other invariants before kicking off 
	either training or article printing logic. 
	''' 

	# Default usage options 
	rebuild = False 
	train = False 
	need_help = False 
	unit_tests = False 
	save_to_file = False

	url = False 


	# First, identify which flags were included 
	for arg in sys.argv[1:]:
		if Helpers.is_url(Helpers.clean_url(arg)): 
			url = Helpers.clean_url(arg)

		elif arg.lower() in ['-r','--rebuild']: rebuild = True 

		elif arg.lower() in ['-t','--train']: train = True 

		elif arg.lower() in ['-d','--debug']: debug = True

		elif arg.lower() in ['-h','--help', 'help']: need_help = True

		elif arg.lower() in ['-f','--file']: save_to_file = True

	while(True):
		if len(sys.argv) <= 1: 
			print "Error: No aurguments provided"
			print "Usage: ./ArticleToText.py url [options]" 
			break  		
		
	# Next, act on the optional flags, as needed. 
		if need_help:
			print help_message
			break 

		if rebuild:
			b_dic = Training.rebuild_t_dic() 
		else: 
			try:
				b_dic = Helpers.load_pickle(bdic_file)
			except: 
				print "\nError: could not load bayes dictionary."
				b_dic = Training.rebuild_t_dic() 

		
		# Rebuild can be submitted with or without a url, necessitating this
		# tricky bit of logic
		if not url and not rebuild: 
			print "Error: must include a valid url"
		elif not url:
			break 

		try: 
			raw_html = download_webpage(url)
		except:
			print "Error: unable to download " + url 
			break

		try: 
			soup = soupify(raw_html)
		except:
			"Error: unable to parse " + url + " with BeautifulSoup"
			break 

		if train:
			b_dic = Training.t_on_article(url, soup, b_dic)
			Helpers.pickle_data(b_dic, bdic_file)
			break 
		else: 
			# Before we start extracting, need to confirm invariants with the
			# underlying Bayes data structure. If they’re not met, we try to
			# recreate it and check again.
			if not NaiveBayes.can_make_guesses(b_dic):
				b_dic = Training.rebuild_t_dic()
			elif not NaiveBayes.can_make_guesses(b_dic):
				print "Error: not enough data or malformed bayes dictionary."
				break 
		
		# Finally we do the actual processing and text extraction 
		article_text = get_article_text(soup, url)

		if save_to_file:
			filename = Helpers.txt_filename_from_url(url)
			try:
				Helpers.write_file_utf(article_text,filename)
			except:
				print "Unable to write " + filename + " to working directory."
			break 
		else: 
			print article_text
			break 
			

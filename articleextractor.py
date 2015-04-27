#!/usr/bin/python
# CS51 Final Project 2015 
# Nathaniel Burbank 
#   

### External Librarys 
from bs4 import BeautifulSoup, NavigableString
import urllib2
import html2text
import re
import codecs
import pickle
import sys 
from tabulate import tabulate

## Other sections of the project 
import helpers
import NaiveBayes 
import PreProcessor

debug = True

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
	
	score_list.sort(key=lambda x: (x[5],x[1]),reverse=True)
	if (debug): print tabulate(score_list,headers=["Token ID","Sens", "Ps", "S-to-L","TextDensity","Overall Score"])

	score_list_max = score_list[0][0]
	article_processed = token_list[score_list_max]
	
	return article_processed

def Tokenizer (article_div):

	def unique (token_list):
		unique_tokens = []
		for token in token_list:
			if token not in unique_tokens:
				unique_tokens.append(token)
	
		return unique_tokens 

	def default_tokenize (text):
		textl = text.lower()
		textl1 = re.sub(r"\W. "," ",textl) 
		textl2 = re.sub(r"s+, "," ",textl1) 
		textl3 = re.split(' ', textl2.strip())
		textl4 = unique(textl3)
		return textl4

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
			child_tokeninzed += default_tokenize(content)

			#for string in child.stripped_strings:
			#	text = text + " " + string.lower() 

			
		else: # is NavigableString 
			string = default_tokenize(child.string)
			child_tokeninzed = ["<NS>"] + string

		tokeninzed[i] = (child_tokeninzed)	
		i += 1



	#print tokeninzed

	for key in tokeninzed.keys():
		print key 

	print tokeninzed
	return tokeninzed


def bayes_processer (pagedata):
	#Still need to implement! 
	return pagedate

def global_optimizer (score_list):
	div_id = score_list[0][0]
	if (debug): print div_id
	return div_id

def token_selector (score_list_max, div_list):
	return div_list[score_list_max]
	
def article_post_processer(div):
	# Still todo
	# return html2text.html2text(div.prettify())

	return div

	# l = (div.find_all())
	# l2 = []
	# for tag in l:
	# 	l2.append(tag.contents)
	# return l2 
	

def training (urllist):
	# Still todo
	return urllist 
	

if __name__ == '__main__':

	#raw_html = download_webpage(sys.argv[1]) 
	raw_html = helpers.read_file_utf(sys.argv[1])
	article_div = page_pre_processer(raw_html)
	Tokenizer(article_div)


	



	# VALID_TAGS = ['strong', 'em', 'p', 'ul', 'li', 'br', 'b', 'a', 'i']

	# for tag in new_soup.findAll(True):
	# 	if tag.name not in VALID_TAGS:
	# 		tag.hidden = True

	#print new_soup.prettify()
		
	
		
	
	
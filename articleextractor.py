#!/usr/bin/python
# CS51 Final Project 2015 
# Nathaniel Burbank 
#   

### External Librarys 
from bs4 import BeautifulSoup 
import urllib2
import html2text
import re
import codecs
import pickle
import sys 
from tabulate import tabulate
import helpers

### Main functions 

def download_webpage(url): 
	print "Downloading webpage source for", url, "...", 
	page = urllib2.urlopen(url)
	pagedata = page.read()
	print "done"
	return pagedata
	
	
def page_pre_processer (pagedata):
	processed = re.sub(r"<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>","",pagedata, re.M )
	# Removes Javascript from page # 
	
	return processed
	
def tokenizer (pagedata):
	soup = BeautifulSoup(pagedata)

	for js in soup.findAll(['script','style']):
		js.extract()
	# More clensing Javascript from page # 
	
	token_list = soup.find_all(['div','article'])
	return token_list


def local_classifiers (token_list):
	i = 0 
	output = [] 
	
	for token in token_list:
		token_l = [i] 
		
		#Number of paragraph tags 
		pars = token.find_all('p')
		token_l.append(len(pars))
		
		#Ratio of sentences to link tags 
		plain_text = token.get_text()
		sentence_num = (len(re.split(r'[.!?]+', plain_text)) ) 
		links = len(token.find_all('a')) + 1 
		ratio = sentence_num / float(links)
		token_l.append(ratio)
		
		#Ratio of text to html 
		text_density= len(plain_text)/float(len(token.prettify()))
		token_l.append(text_density)
		
		#Number of commas 
#		words = len(re.split(r'[\w]+', plain_text))
		commas = len(re.findall(',',plain_text))  
#		ratio = words/float(commas)
		token_l.append(commas)
		
		#Ratio of text to tags 
		text = len(token.get_text())
		tags = len(token.find_all()) + 1 
		ratio = text / float(tags)
		token_l.append(ratio)
		
		output.append(token_l)
		i = i + 1 
		
	return output
		  

def global_optimizer (score_list):
	div_id = score_list[0][0]
	print div_id
	return div_id

def token_selector (score_list_max, div_list):
	return div_list[score_list_max]
	
def article_post_processer(div):
#	for elem in div.findAll(['script', 'style']):
#		print elem 
#		elem.extract()
#	return div.prettify()
#	new_text = ""
#	for p in div.findAll('p'):
#		new_text = new_text + p.get_text() + "\n"
#	return div.prettify()
#	return div.get_text()
	return html2text.html2text(div.prettify())
	

def training (urllist):
	return urllist 
	

if __name__ == '__main__':

	raw_html = download_webpage(sys.argv[1])
	processed_webpage = page_pre_processer(raw_html)
	token_list = tokenizer (processed_webpage) 
	score_list = local_classifiers(token_list)
	
	score_list.sort(key=lambda x: x[2],reverse=True)
	print tabulate(score_list,headers=["Token", "Pars", "S-to-L","Text Density","W-to-C","T-to-Tag"])

	score_list_max = global_optimizer(score_list)
	article_processed = article_post_processer(token_list[score_list_max])
	print article_processed
	
	
		
	
	
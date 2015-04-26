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
	return html2text.html2text(div.prettify())
	# l = (div.find_all())
	# l2 = []
	# for tag in l:
	# 	l2.append(tag.contents)
	# return l2 
	

def training (urllist):
	# Still todo
	return urllist 
	

if __name__ == '__main__':

	raw_html = download_webpage(sys.argv[1]) 
	processed_webpage = page_pre_processer(raw_html)

	print article_post_processer(processed_webpage)
		
	
		
	
	
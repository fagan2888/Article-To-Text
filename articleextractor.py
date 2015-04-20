#!/usr/bin/python

from bs4 import BeautifulSoup 
import urllib2

def download_webpage(url): -> pagedata 
	print "Downloading webpage source for", url, "...", 
	page = urllib2.urlopen(url)
	pagedata = page.read()
	print "done"
	return pagedata
	
	
def page_pre_processer (pagedata)
	return pagedata 
	
def tokenizer (pagedata) 
	soup = BeautifulSoup(pagedate)
	return soup.find_all('div') 

def Local_classifiers (div_list)
	return [(false,29),(false,55),(true,76),(false,55)] 

def global_optimizer (div_score_list)
	return (article_likeness_score_list)

def token_selector (div_score_list)
	max_score  = 0 
	for score in article_likeness_score_list 
		if (score > max_score) max_score = score 
	
def article_post_processer(div)
	return div.plaintext 


def training 
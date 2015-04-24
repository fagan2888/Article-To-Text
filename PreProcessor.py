#!/usr/bin/python

from bs4 import BeautifulSoup 
import re
import codecs

def classifier (token_list):
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
		ratio = (len(pars)/10) * (sentence_num / float(links))
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
		text = len(re.split(r'[\w]+', plain_text))
		tags = len(token.find_all()) 
		s = text + (tags * -3.25)
		token_l.append(s)
		
		output.append(token_l)
		i = i + 1 
		
	return output
			  

def tokenizer (pagedata):
	soup = BeautifulSoup(pagedata)

	for js in soup.findAll(['script','style']):
		js.extract()
	# More clensing Javascript from page # 
	
	token_list = soup.find_all(['div','article','nav'])
	return token_list	


#!/usr/bin/python

from bs4 import BeautifulSoup 
import re
import codecs
from tabulate import tabulate

debug = False


def tokenizer (soup):
	token_list = soup.find_all(['div','article','nav'])
	return token_list	

def div_selector (token_list, soup):
	
	i = 0 
	output = [] 

	# Generate stats for the whole page 

	# Total number of sentences
	page_text = soup.get_text()
	page_num_of_sens = (len(re.split(r'[.!?]+', page_text))) + 1 

	#Number of paragraph tags 
	page_num_of_pars = len(soup.find_all('p')) + 1 

	
	for token in token_list:

		# Number of sentences within given token 
		plain_text = token.get_text()
		sentence_num = (len(re.split(r'[.!?]+', plain_text)) ) 

		if (sentence_num > 1): #just skip any token that does not have at least two sentences in it.

			#Token ID
			token_stats = [i] 
			sentence_num_adjusted = sentence_num /float(page_num_of_sens)

			# % of sentences 
			token_stats.append(sentence_num_adjusted)
			
			# % of paragraph tags 
			pars = len(token.find_all('p', recursive=False))/float(page_num_of_pars)
			token_stats.append(pars)

			# Becuase the paragraph is a factor in  the following two statistics, this puts in a floor 
			pars_a = max(.1,pars)

			#Ratio of sentences to link tags, weighted by paragraph tags 
			links = len(token.find_all('a')) + 1 
			StoLP = (sentence_num / float(links)) * pars_a
			token_stats.append(StoLP)
			
			#Ratio of text to html, weighted by paragraph tags  
			text_density= (len(plain_text)/float(len(token.prettify()))) * pars_a
			token_stats.append(text_density)

			#Weighted score metric, based on a regression analysis of small set of sample data. 
			score = -.0079908 + (.0225799 * sentence_num_adjusted) + (1.319708  * pars) + ( -.0017439  *  StoLP) + (.55502 * text_density)
			token_stats.append(score)
			

			output.append(token_stats)

		i = i + 1 

	output.sort(key=lambda x: (x[5],x[1]),reverse=True)
	if (debug): print tabulate(output,headers=["Token ID","Sens", "Ps", "S-to-L","TextDensity","Overall Score"])
	
	return output
			  




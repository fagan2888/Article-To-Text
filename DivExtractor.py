#!/usr/bin/python

from bs4 import BeautifulSoup
import re
import codecs

debug = False


def tokenizer (soup):
	'''
	Returns an iterator containing all div, article and nav elements that exist
	within the soup. Elements may (and frequently are) overlapping with one another.
	'''
	token_list = soup.find_all(['div','article','nav'])
	return token_list

def article_selector (token_list, soup):
	"""
	Returns a pointer to the div that (likely) contains the article text within
	the Beautiful Soup data structure. Guess is based on a set of heuristics
	hard-coded below.
	"""

	i = 0
	output = []

	# Generate stats for the whole page

	# Total number of sentences
	page_text = soup.get_text()
	page_num_of_sens = (len(re.split(r'[.!?]+', page_text))) + 1

	# Total number of paragraph tags
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

			# Becuase the paragraph is a factor in the following two statistics,
			# this puts in a floor
			pars_a = max(.1,pars)

			#Ratio of sentences to link tags, weighted by paragraph tags
			links = len(token.find_all('a')) + 1
			StoLP = (sentence_num / float(links)) * pars_a
			token_stats.append(StoLP)

			#Ratio of text to html, weighted by paragraph tags
			text_density= (len(plain_text)/float(len(token.prettify()))) * pars_a
			token_stats.append(text_density)

			#Weighted score metric, based on a regression analysis of small set of sample data.
			article_likeliness_score = -.0079908 + (.0225799 * sentence_num_adjusted) + \
			(1.319708  * pars) + ( -.0017439  *  StoLP) + (.55502 * text_density)
			token_stats.append(article_likeliness_score)

			output.append(token_stats)

		i = i + 1

	# Sort by score, and then return the div ID at the top
	output.sort(key=lambda x: (x[5],x[1]),reverse=True)
	article_div_id = output[0][0]

	return article_div_id





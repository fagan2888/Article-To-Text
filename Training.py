#!/usr/bin/python
# -*- coding: utf-8 -*-
# CS51 Final Project 2015 
# Nathaniel Burbank 
#   

from bs4 import BeautifulSoup, NavigableString, Comment
from ArticleToText import valid_categories, article_div_extractor, \
article_div_pre_processer, article_tokenizer, soupify

import re
import Helpers
import NaiveBayes 


# Global variables

training_dir = "trainingdata/"
training_tsv = training_dir + "training.tsv"

def rebuild_t_dic ():

	print "\n Rebuilding bayes dic. . .",	
	b_dic = {} 

	training_data = Helpers.read_file_utf(training_tsv)

	i = 0 
	for line in training_data.split("\n"):
		if line[0] not in ["#"]: 
			lst = line.split(",")
			filename = training_dir + lst.pop(0) #Both returns first elm and deletes it 

			if (debug): print "loading " + filename 
			if not (debug): print ".", 
			list_len = int(lst.pop(0))
			try: 
				raw_html = Helpers.read_file_utf(filename)
			except:
				print "Error: unable to read " + filename
				continue 

			soup = BeautifulSoup(raw_html)
			article_div = article_div_extractor(soup)
			clean_article_div = article_div_pre_processer (article_div)
			token_dic = article_tokenizer(clean_article_div)

			#Confirm invariants
			if not Helpers.training_invariants_met(lst,list_len,
				clean_article_div,token_dic,valid_categories):
				if (debug): print "Error: Skipping " + filename 
				continue

			c = 0 
			for child in clean_article_div.children:
				b_dic = NaiveBayes.train(token_dic[child],valid_categories[lst[c]], b_dic)
				c += 1 

			i +=1 

	
	Helpers.pickle_data(b_dic, bdic_file)
	print "Done.\n"
	print "Loaded ", str(i), " documents into b_dic. Training complete."

	return b_dic 


def t_on_article (url, soup, b_dic):
	'''
	Train on article 
	''' 

	try:
		training_data = Helpers.read_file_utf(training_tsv)
	except:
		print "Error: unable to read training data file."

	
	html = unicode(soup)
	filecount = len(training_data.split("\n")) 
	# Preprend a filecount before name to prevent namespace problems 

	filename = str(filecount) + "_" + Helpers.filename_from_url(url) 

	try:
		Helpers.write_file_utf(html, training_dir + filename)
	except:
		print "Error: unable save " + filename + " to disc."
		print "Training data for this article will not be retained."

	reheated_soup = soupify(html)
	article_div = article_div_extractor(reheated_soup)
	clean_article_div = article_div_pre_processer (article_div)
	token_dic = article_tokenizer(clean_article_div) 

	# Make new line in training file 
	t = len(clean_article_div) 
	data = "\n" + filename + "," + str(t)
	Helpers.append_file_utf(data, training_tsv)

	i = 1 
	for child in clean_article_div.children:
		if isinstance(child, NavigableString):
			b_dic = training_loop(i,t,child.string,token_dic[child], b_dic)
		else:
			b_dic = training_loop(i,t,child.get_text("\n", strip=True),token_dic[child], b_dic)
		i += 1 

	return b_dic 


def training_loop(i,t, section_text, tokens, b_dic):

	cmd = ""
	Helpers.clear_screen() 
	print "%d of %d" % (i,t)  
	can_make_guesses = NaiveBayes.can_make_guesses(b_dic) 
	
	if can_make_guesses: 

		guess = NaiveBayes.extract_Winner(NaiveBayes.guess(tokens,b_dic))
		print "\nGuess is " + guess 

		guess_key = ""
		for key in valid_categories.keys():
			if guess == valid_categories[key]: guess_key = key 

		assert guess_key != "" 

	print section_text
	print "###########################"
	print tokens 


	while cmd != "q":

		input_msg = "Enter A for article, H for headline, S for spam or junk content, D for date, B for byline:\n" 
		if can_make_guesses: input_msg = "Hit enter to confirm guess or " + input_msg 

		cmd = raw_input(input_msg)

		if cmd == "q": 
			break ##first check to see if a q was entered
		
		if not cmd and can_make_guesses: 
			cmd = guess_key
		else: 
			cmd = cmd.lower() 

		if cmd in valid_categories.keys():
			b_dic = NaiveBayes.train(tokens,valid_categories[cmd], b_dic)
 
			Helpers.append_file_utf(("," + cmd ), training_tsv) 
			break 
		
		else: 
			print "Error ", cmd, " is an invalid command. Please try again, or enter q quit."

	return b_dic
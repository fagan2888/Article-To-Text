#!/usr/bin/python
# -*- coding: utf-8 -*-
# CS51 Final Project 2015 
# Nathaniel Burbank 
#   

import re
import math 

debug = False 

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


def inc_token(token,label,b_dic):
	assert label in b_dic.keys() 
	
	token_dic = b_dic[label]["Token_counts"]
	if token in token_dic.keys():
		token_dic[token] += 1 
	else:
		token_dic [token] = 1

	return b_dic

def inc_Doc_Count(label,b_dic):
	assert label in b_dic.keys() 

	if b_dic[label]["Doc_count"] > 0:
		b_dic[label]["Doc_count"] += 1 
	else:
		b_dic[label]["Doc_count"] = 1 

	return b_dic

def total_doc_count(b_dic):
	#Total number of docs that have been saved
	total = 0 
	for key in b_dic.keys():
		total += b_dic[key]["Doc_count"]
	return total 

def doc_count_for_label(label, b_dic):
	return b_dic[label]["Doc_count"]

def inverse_Doc_Count (label,b_dic): 
	#Total number of docs that have been saved, except for the given label 
	total_docs = total_doc_count(b_dic)
	return (total_docs - doc_count_for_label(label, b_dic))

def register_Label (label, b_dic):
	if label not in b_dic.keys():
		label_dic = {"Doc_count": 0, "Token_counts":{} } 
		b_dic[label] = label_dic 

	return b_dic

def labels (b_dic):
	#returns a list of the current label names in the b_dic data structure
	return b_dic.keys()

def token_Label_Count(token, label, b_dic):
	# Returns how many times the given token occurs for the given label 
	token_dic = b_dic[label]["Token_counts"]
	count = 0 
	if token in token_dic.keys():
		count = token_dic[token]
	return count 
	
def token_Inverse_Label_Count (token, l, b_dic):
	#Returns how many times the given token occurs for lables other than the given label 
	count = 0
	for label in labels(b_dic):
		if (label != l): 
			count += token_Label_Count(token,label,b_dic) 
	return count

def total_token_count (token, b_dic):
	#Returns the number of times we've seen the given token in any document during training 
	count = 0
	for label in labels(b_dic):
		count += token_Label_Count(token, label, b_dic) 

	return count

def can_make_guesses(b_dic):
	has_docs = total_doc_count(b_dic) > 10
	has_labels = len(labels(b_dic)) >= 2 

	if has_docs and has_labels: return True 
	else: return False 


#Main functions 

def train_With_list(lst,tokenize_f,b_dic):
	for item in lst:
		text, label = item 
		tokens = tokenize_f(text)
		b_dic = train(tokens,label,b_dic)

	return b_dic

def train (tokens, label, b_dic):

	if label not in labels(b_dic):
		b_dic = register_Label(label,b_dic)
	
	for token in tokens:
		b_dic = inc_token(token,label,b_dic)
		
	b_dic = inc_Doc_Count(label, b_dic)

	return b_dic

	
def guess(tokens, b_dic):

	assert (total_doc_count(b_dic)) > 0 
	
	scores = {}
	labelProbability = {}
			
	for label in labels(b_dic):
		
		logSum = 0.00 
		labelProbability[label] = doc_count_for_label(label, b_dic) / float(total_doc_count(b_dic))
	
		for token in tokens: 

			tokenicity = 0.01
			total_Tokins = total_token_count(token,b_dic)
			
			if (total_Tokins == 0):
				if (debug): print "Skipping " + token 
				continue
				# If the token is not assocated with any of the labels, skip it 
			else:
				if (debug): print "Starting " + token 
				
				tokenProbability = (token_Label_Count(token, label, b_dic) /  float(doc_count_for_label(label, b_dic))) * labelProbability[label]
				if (debug): print "Probability:" + str(token_Label_Count(token, label, b_dic)) + "/" + str(doc_count_for_label(label, b_dic)) + " * " + str(labelProbability[label]) + " = " + str(tokenProbability) 
				# What's the probility that a given token appears in documents of this label? 

				tokenInverseProbability = (token_Inverse_Label_Count(token, label, b_dic) / float(inverse_Doc_Count(label, b_dic))) * (1 - labelProbability[label])
				if (debug): print "InverseProbability:" + str(token_Inverse_Label_Count(token, label, b_dic)) + "/" + str(inverse_Doc_Count(label, b_dic)) +  " * " + str((1 - labelProbability[label])) + " = " + str(tokenInverseProbability)
				# The probability that the token shows up in any *other* category than the one we're considering.

				tokenicity = tokenProbability / float(tokenProbability + tokenInverseProbability)
				if (debug): print "tokenicity: " + str(tokenProbability) + "/(" + str(tokenProbability) + "+" +  str(tokenInverseProbability) + ") = " + str(tokenicity)
				#  Given the token is present, tokenicity is probability that the document is in the category we're considering. 

				tokenicity = ( (1 * 0.5) + (total_Tokins * tokenicity) ) / ( 1 + total_Tokins )
				
				if (tokenicity == 0):
					tokenicity = 0.01
				elif (tokenicity == 1):
					tokenicity = 0.99
		   
			logSum = logSum + (math.log(1 - tokenicity) - math.log(tokenicity))
			if (debug): print label + "icity of " + token + ": " + str(tokenicity)
			
		scores[label] = 1 / ( 1 + math.exp(logSum))		
	return scores


def extract_Winner (scores):
	bestScore = 0
	bestLabel = ""
	for label in scores.keys(): 
		if (debug): print label + ": " + str(scores[label])
		if (scores[label] > bestScore):
			bestScore = scores[label]
			bestLabel = label
		
	return bestLabel




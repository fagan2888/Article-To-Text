#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import math 

debug = False

def empty_Bayes_Ds ():
	return dict()

def unique (token_list):
	unique_tokens = []
	for token in token_list:
		if token not in unique_tokens:
			unique_tokens.append(token)
	
	return unique_tokens 

def tokenize (text):
	textl = text.lower()
	textl1 = re.sub(r"\W. "," ",textl) 
	textl2 = re.sub(r"s+, "," ",textl1) 
	textl3 = re.split(' ', textl2.strip())
	textl4 = unique(textl3)
	return textl4

def inc_token(token,label,bayes_ds):
	assert label in bayes_ds.keys() 
	
	token_dic = bayes_ds[label]["Token_counts"]
	if token in token_dic.keys():
		token_dic[token] += 1 
	else:
		token_dic [token] = 1

	return bayes_ds

def inc_Doc_Count(label,bayes_ds):
	assert label in bayes_ds.keys() 

	if bayes_ds[label]["Doc_count"] > 0:
		bayes_ds[label]["Doc_count"] += 1 
	else:
		bayes_ds[label]["Doc_count"] = 1 

	return bayes_ds

def total_doc_count(bayes_ds):
	#Total number of docs that have been saved
	total = 0 
	for key in bayes_ds.keys():
		total += bayes_ds[key]["Doc_count"]
	return total 

def doc_count_for_label(label, bayes_ds):
	return bayes_ds[label]["Doc_count"]

def inverse_Doc_Count (label,bayes_ds): 
	#Total number of docs that have been saved, except for the given label 
	total_docs = total_doc_count(bayes_ds)
	return (total_docs - doc_count_for_label(label, bayes_ds))

def register_Label (label, bayes_ds):
	if label not in bayes_ds.keys():
		label_dic = {"Doc_count": 0, "Token_counts":{} } 
		bayes_ds[label] = label_dic 

	return bayes_ds


def labels (bayes_ds):
	#returns a list of the current label names in the bayes_ds data structure
	return bayes_ds.keys()

	
def token_Label_Count(token, label, bayes_ds):
	# Returns how many times the given token occurs for the given label 
	token_dic = bayes_ds[label]["Token_counts"]
	count = 0 
	if token in token_dic.keys():
		count = token_dic[token]
	return count 
	
def token_Inverse_Label_Count (token, l, bayes_ds):
	#Returns how many times the given token occurs for lables other than the given label 
	count = 0
	for label in labels(bayes_ds):
		if (label != l): 
			count += token_Label_Count(token,label,bayes_ds) 
	return count

def total_token_count (token, bayes_ds):
	#Returns the number of times we've seen the given token in any document during training 
	count = 0
	for label in labels(bayes_ds):
		count += token_Label_Count(token, label, bayes_ds) 

	return count

def train_With_list(lst,bayes_ds):
	for item in lst:
		text, label = item 
		bayes_ds = train(text,label,bayes_ds)

	return bayes_ds

def train (text, label, bayes_ds):
	if label not in labels(bayes_ds):
		bayes_ds = register_Label(label,bayes_ds)
	
	tokens = tokenize(text)
	
	for token in tokens:
		bayes_ds = inc_token(token,label,bayes_ds)
		
	bayes_ds = inc_Doc_Count(label, bayes_ds)

	return bayes_ds

	
def guess(text, bayes_ds):

	assert (total_doc_count(bayes_ds)) > 0 

	tokens = tokenize(text)
	
	scores = {}
	labelProbability = {}
			
	for label in labels(bayes_ds):
		
		logSum = 0.00 
		labelProbability[label] = doc_count_for_label(label, bayes_ds) / float(total_doc_count(bayes_ds))
	
		for token in tokens: 

			tokenicity = 0.01
			total_Tokins = total_token_count(token,bayes_ds)
			
			if (total_Tokins == 0):
				if (debug): print "Skipping " + token 
				continue
			else:
				if (debug): print "Starting " + token 
				tokenProbability = token_Label_Count(token, label, bayes_ds) /  float(doc_count_for_label(label, bayes_ds))
				tokenInverseProbability = token_Inverse_Label_Count(token, label, bayes_ds) / float(inverse_Doc_Count(label, bayes_ds))

				if (debug): print "inverse_Doc_Count " + str(float(inverse_Doc_Count(label, bayes_ds)))
				if (debug): print "tokenProbability " + str(tokenProbability)
				if (debug): print "tokenInverseProbability " + str(tokenInverseProbability)

				tokenicity = tokenProbability / float(tokenProbability + tokenInverseProbability)
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




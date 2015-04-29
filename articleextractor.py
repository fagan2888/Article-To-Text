#!/usr/bin/python
# CS51 Final Project 2015 
# Nathaniel Burbank 
#   

### External Librarys 
from bs4 import BeautifulSoup, NavigableString, Comment
import urllib2
import html2text
import sys 
import codecs
import pickle
import sys 
import re 

## Other sections of the project 
import Helpers
import NaiveBayes 
import PreProcessor

debug = True

training_dir = "trainingdata/"
training_tsv = training_dir + "training.tsv"
valid_categories = {'h': 'headline', 'a': 'article', 'd': 'dateline', 'b':'byline', 's':'spam'} 

### Helper functions

def unique (token_list):
	# Returns list with unique values only 
	unique_tokens = []
	[unique_tokens.append(item) for item in token_list if item not in unique_tokens]
	return unique_tokens 
		

def stem(word):
# Super simple word stemmer, that removes common English suffixes. 
# Obviously not perfect and could be (vastly!) improved, but that is out scope for now. 
	for suffix in ['ing','ly','ed','ious','ies','ive','es',"'s",'ment']:
		if word.endswith(suffix):
			return word[:-len(suffix)]
	
	return word 

def tokenize_string (text):
	"""
	Very rudimentary tokenizer. Converts a sentence such as this:
	Hey!! You can't use those. Those are Jack's  bowling balls! 
	Into a list of unique, stemmed words like this: 
	['hey', '!', 'you', "can't", 'use', 'those', '.', 'are', 'jack', 'bowl', 'balls']

	Unlike many stemming functions, I decided to explicitly include punctuation, 
	as I think it may have meaning in this context. 

	"""

	text_with_punc = re.sub(r"([.!,;?])", r" \1 ", text) 
	#Add spaces to certain puncuation so that it's preserverd in the next step

	words = re.sub("[^\w.!,;?']", " ", text_with_punc).lower().split()
	# Normalize spaces, lowercase everything, then convert string to list of words 
	
	stemmed_words = []
	[stemmed_words.append(stem(word)) for word in words]
	
	return unique(stemmed_words)


### Main functions 

def download_webpage(url): 
	if (debug): print "Downloading webpage source for", url, "...", 
		
	#make an url opener that can handle cookies so this works with NYtimes... 
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
	opener.addheaders = [('User-agent', 'Mozilla/5.0')]
	#read in the site
	response = opener.open(url)
	html = response.read()
	
	if (debug): print "done"
	return html
	

def soupify (raw_html):
	#processed = re.sub(r"<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>","",pagedata, re.M )
	# Removes Javascript from page # 
	
	soup = BeautifulSoup(raw_html)

	for elem in soup.findAll(['script','style']):
		elem.decompose()

	for element in soup(text=lambda text: isinstance(text, Comment)):
		element.extract()

	return soup 

def make_article_dic(soup, url):

	article_dic = {}
	
	try:
		article_dic[headline] = soup.title.string
	except:
		article_dic[headline] = Helpers.get_title_from_url(url)

	try:
		article_dic[date] = soup.date.string
	except:
		print "could not find date"
		
	return article_dic 



def page_pre_processer (soup):

	div_list = PreProcessor.tokenizer(soup) 
	div_score_table = PreProcessor.div_selector(div_list, soup)
	
	score_list_max = div_score_table[0][0]
	article_div = div_list[score_list_max]
	
	return article_div

def article_div_pre_processer (article_div):

	# Remove tags that contain no content 
	empty_tags = article_div.findAll(lambda tag: tag.is_empty_element or not tag.contents and (tag.string is None or not tag.string.strip()))
	[empty_tag.decompose() for empty_tag in empty_tags]

	# Remove empty navigable strings 

	for x in range(0,3):
		for child in article_div:
			if isinstance(child, NavigableString):
				if (len(child.string.strip()) <= 1):
					child.extract()
	
	# The x in range loop bit of this is a hack. I'm not sure why I need to do multiple
	# iterations over the list of children to find all of the empty navigable
	# strings, but if I don't, some are left behind and it causes problems
	# further below.  Might be a bug in BeautifulSoup.

	return article_div 

def article_tokenizer (clean_article_div):
	"""
	For each html object one level below the article div, this function tokenizes it, 
	and returns a dictionary keyed off of the beautiful soup child objects. 
	""" 

	def get_classes(tag):
		classes = []
		if 'class' in tag.attrs: 
			for c in tag.attrs['class']:
				classes.append("[" + c + "]")

		return classes 
	
	token_dic = {}
	for child in clean_article_div.contents:
		child_tokens = []
		if isinstance(child, NavigableString): # is NavigableString  
			string = tokenize_string(child.string)
			child_tokens = ["<NS>"] + string

		else: #Child is tag, and can have it's own children 
			
			# Build list of html tags in the child, including the parrent tag 
			child_tags = [("<" + str(child.name) + ">")]  
			child_classes = get_classes(child)
			for tag in child.find_all(True):
				tag_name = "<" + str(tag.name) + ">"
				child_tags.append(tag_name) 
				child_classes += get_classes(tag)

			child_text = child.get_text().strip()
			child_tokens += unique(child_tags) + unique(child_classes) + tokenize_string(child_text)

		token_dic[child] = child_tokens

	return token_dic


def bayes_processer (token_dic, b_dic):
	scores = {}
	for child in token_dic.keys():
		scores[child] = NaiveBayes.guess(token_dic[child],b_dic)

	return scores 


def article_extractor (score_dic, article_div):

	for x in range(0,3):
		for child in article_div.contents: 
			rankings = score_dic[child]
			guess = NaiveBayes.extract_Winner(rankings) 
			if guess != "article":
				child.extract()
		
	return article_div

def token_selector (score_list_max, div_list):
	return div_list[score_list_max]
	
def article_post_processer(article_div):
	# Still todo
	
	VALID_TAGS = ['strong', 'em', 'p', 'ul', 'li', 'br', 'b', 'a', 'i'] 

	# Remove attibutes from html tags 
	for tag in article_div():
		tag.attrs = None

	for tag in article_div.findAll(True):
		if tag.name not in VALID_TAGS:
			tag.hidden = True

	return html2text.html2text(article_div.prettify())


def print_div (article_div):

	t = len(article_div)
	i = 1 
			
	for child in article_div.contents:
		if isinstance(child, NavigableString):
			print "####"
			print "%d of %d" % (i,t) 
			print len(child.string)
			print child.string
		else:
			print "####"
			print "%d of %d" % (i,t) 
			print child
		i += 1 



def rebuild_training_dic (): 
	
	b_dic = {} 

	training_data = Helpers.read_file_utf(training_tsv)

	i = 0 
	for line in training_data.split("\n"):
		if line[0] not in ["#"]: 
			lst = line.split(",")
			filename = training_dir + lst.pop(0) #Both returns first elm and deletes it 

			print "starting " + filename 
			list_len = int(lst.pop(0)) 
			raw_html = Helpers.read_file_utf(filename) 
			soup = BeautifulSoup(raw_html)
			article_div = page_pre_processer(soup)
			clean_article_div = article_div_pre_processer (article_div)
			token_dic = article_tokenizer(clean_article_div)

		
			#Confirm invariants

			for tag in lst:
				assert tag.lower() in valid_categories.keys() 
			
			print "Num of children: " + str(len(clean_article_div))
			print "Expected number of classifcations" + str(list_len)
			print "Number of classifcations " + str(len(lst)) 
			print "Number of keys " + str(len(token_dic.keys()))  
			
			if filename == "trainingdata/story.html": print_div(clean_article_div)

			assert len(lst) == list_len
			assert len(clean_article_div) == len(lst) 

			c = 0 
			for child in clean_article_div.children:
				b_dic = NaiveBayes.train(token_dic[child],valid_categories[lst[c]], b_dic)
				c += 1 

			i +=1 

	print "processed ", str(i), " docs into b_dic. Training complete."

	return b_dic 


def train_on_article (url, soup, clean_article_div, token_dic, b_dic):

	# Save artcle html to training dir 
	#html = soup.renderContents()  
	html = unicode(soup)
	filename = Helpers.filename_from_url(url) 

	Helpers.write_file_utf(html, training_dir + filename)

	print_div(clean_article_div)

	# Make new line in training file 
	t = len(clean_article_div) 
	data = "\n" + filename + "," + str(t)
	Helpers.append_file_utf(data, training_tsv)


	print "Starting training"
	print len(clean_article_div)
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
	print(chr(27) + "[2J")  #Clear screen 
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


def process_html(raw_html):
	article_div = page_pre_processer(raw_html)
	clean_article_div = article_div_pre_processer (article_div)
	return article_tokenizer(article_div)


if __name__ == '__main__':


	#raw_html = Helpers.read_file_utf(sys.argv[1])
	#if Helpers.is_url(sys.argv[1]):

	try:
		b_dic = Helpers.load_pickle('bdic.data')
	except: 
		print "Error: could not load bayes dictionary"
		b_dic = {}
	
	if len(sys.argv) < 2: 
		print "Error: No aurguments provided" 
		b_dic = rebuild_training_dic() 
		Helpers.pickle_data(b_dic, 'bdic.data') 

	elif len(sys.argv) == 2:

		url = sys.argv[1] 
		raw_html = download_webpage(url)
		soup = soupify(raw_html)
		article_div = page_pre_processer(soup)
		clean_article_div = article_div_pre_processer (article_div)
		token_dic = article_tokenizer(clean_article_div) 
		b_scores = bayes_processer(token_dic, b_dic)
		article_div_processed = article_extractor(b_scores, clean_article_div)
		print article_post_processer(article_div_processed)

	elif len(sys.argv) == 3:
		url = sys.argv[1] 
		raw_html = download_webpage(url)
		soup = soupify(raw_html)
		article_div = page_pre_processer(soup)
		clean_article_div = article_div_pre_processer (article_div)
		token_dic = article_tokenizer(clean_article_div)
		b_dic = train_on_article(url, soup, clean_article_div, token_dic, b_dic)
		Helpers.pickle_data(b_dic, 'bdic.data') 







	



		
	
		
	

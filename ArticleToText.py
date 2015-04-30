#!/usr/bin/python
# CS51 Final Project 2015 
# Nathaniel Burbank 
#   

# Standard Librarys  
import urllib2
import sys 
import codecs
import sys 
import re 

# External Librarys 
from bs4 import BeautifulSoup, NavigableString, Comment
import html2text

# Other sections of the project 
import Helpers
import NaiveBayes 
import PreProcessor

# Global variables 

help_message = \
"""
ArticleToText 
Harvard CS51 Final Project 2015 
Nathaniel Burbank 

Usage: ./ArticleToText.py url [options] 

Options:
  -h, --help    Show this help message and exit.
  -d, --debug	Print debugging information while running.
  -r, --rebuild	Rebuild the Bayes data structure based on the webpages 
  				in the training directory and training.tsv file.
  -t, --train	Run supervised trainer on submitted url. Save results to 
  				training directory and Bayes data structure.  
  -u, --unit	Run unit tests and exit.
  
"""
debug = False

training_dir = "trainingdata/"
training_tsv = training_dir + "training.tsv"
valid_categories = \
{'h': 'headline', 'a': 'article', 'd': 'dateline', 'b':'byline', 's':'spam'}
bdic_file = "bdic.data" 



### Main functions 

def download_webpage(url): 
	# Downloades webpage using urllib2 and returns unprocessed html.  

		
	if (debug): print "Downloading webpage source for", url, "...", 
		
	#make an url opener that can handle cookies so this works with NYtimes... 
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
	opener.addheaders = [('User-agent', 'Mozilla/5.0')]
	#read in the site
	response = opener.open(url)
	raw_html = response.read()
	
	if (debug): print "done"
	return raw_html
	

def soupify (raw_html):
	"""
	Parses raw html into BeautifulSoup data structure. Also removes html comments
	and javascript and style tags.
	"""
	soup = BeautifulSoup(raw_html)

	# just delete javascript and style tags 
	for tag in soup.findAll(['script','style']):
		tag.decompose()

	# Remove html comments as well 
	for element in soup(text=lambda text: isinstance(text, Comment)):
		element.extract()

	return soup 

def make_article_dic(soup, url):
	"""
	Returns a dictionary object with metadata about the article. For now, just
	contains the url and page title, but plan to extend further with date and
	other attributes if I have time. 
	"""

	article_dic = {}
	article_dic[url] = url 
	
	try:
		article_dic['headline'] = soup.title.string
	except:
		article_dic['headline'] = Helpers.get_title_from_url(url)

	return article_dic 

def article_div_extractor(soup):
	"""
	Returns a pointer to the div that (likely) contains the article text within
	the Beautiful Soup data structure. Guess is based on a set of heuristics
	hard-coded within the PreProcessor module.  
	"""

	div_list = PreProcessor.tokenizer(soup) 
	div_score_table = PreProcessor.div_selector(div_list, soup)
	
	score_list_max = div_score_table[0][0]
	article_div = div_list[score_list_max].extract()
	
	return article_div

def article_div_pre_processer (article_div):

	# Remove tags that contain no content 
	empty = lambda tag: tag.is_empty_element or \
	not tag.contents and (tag.string is None or not tag.string.strip())
	
	empty_tags = article_div.findAll(empty)
	[empty_tag.decompose() for empty_tag in empty_tags]

	# Remove empty navigable strings 

	for x in range(0,3):
		for child in article_div:
			if isinstance(child, NavigableString):
				if (len(child.string.strip()) <= 1):
					child.extract()
	
	# The x in range loop bit above is a bit of a hack. I'm not sure why I
	# need to do multiple iterations over the list of children to find all of
	# the empty navigable strings, but if I don't, some are left behind and it
	# causes problems further below. Might be a bug in BeautifulSoup.

	return article_div 

def article_tokenizer (clean_article_div):
	"""
	For each html object one level below the article div, this function 
	tokenizes it, and returns a dictionary keyed off of the beautiful 
	soup child objects. 
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
			string = Helpers.tokenize_string(child.string)
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
			child_tokens += Helpers.unique(child_tags) + \
			Helpers.unique(child_classes) + Helpers.tokenize_string(child_text)

		token_dic[child] = child_tokens

	return token_dic


def bayes_processer (token_dic, b_dic):
	scores = {}
	for child in token_dic.keys():
		scores[child] = NaiveBayes.guess(token_dic[child],b_dic)

	return scores 


def filter_article_div (score_dic, article_div, article_dic):

	for x in range(0,3):
		for child in article_div.contents: 
			rankings = score_dic[child]
			guess = NaiveBayes.extract_Winner(rankings) 
			if guess != "article":
				child.extract()
		
	return article_div



def rebuild_training_dic ():

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


def train_on_article (url, soup, b_dic):

	# Save artcle html to training dir 
	#html = soup.renderContents()  

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


def article_post_processer(article_div,article_dic):

	headline = article_dic['headline']
	hl = BeautifulSoup("<h1>" + headline + "</h1>")
	article_div.insert(0,hl)
		
	valid_tags = ['strong', 'em', 'p', 'ul', 'li', 'br', 'b', 'a', 'i'] 

	# Remove all attibutes from html tags 
	for tag in article_div():
		tag.attrs = None

	for tag in article_div.findAll(True):
		if tag.name not in valid_tags:
			tag.hidden = True

	return html2text.html2text(article_div.prettify())
	#return article_div.prettify()


if __name__ == '__main__':

	rebuild = False 
	train = False 
	needhelp = False 
	url = False 
	unittests = False 

	while(True):
		if len(sys.argv) <= 1: 
			print "Error: No aurguments provided"
			print "Usage: ./ArticleToText.py url [options]" 
			break  		
		
		else:
			for arg in sys.argv[1:]:
				if Helpers.is_url(Helpers.clean_url(arg)): 
					url = Helpers.clean_url(arg)

				elif arg.lower() in ['-r','--rebuild']:
					rebuild = True 

				elif arg.lower() in ['-t','--train']:
					train = True 

				elif arg.lower() in ['-d','--debug']:
					debug = True

				elif arg.lower() in ['-h','--help', 'help']:
					needhelp = True

			if needhelp:
				print help_message
				break 

			if rebuild:
				b_dic = rebuild_dic() 
			else: 
				try:
					b_dic = Helpers.load_pickle(bdic_file)
				except: 
					print "\nError: could not load bayes dictionary."
					b_dic = rebuild() 

			if not url and not rebuild: 
				print "Error: must include a valid url"
			elif not url:
				break 

			try: 
				raw_html = download_webpage(url)
			except:
				print "Error: unable to download " + url 
				break

			try: 
				soup = soupify(raw_html)
			except:
				"Error: unable to parse " + url 
				break 

			if train:
				b_dic = train_on_article(url, soup, b_dic)
				Helpers.pickle_data(b_dic, bdic_file)
				break 
			
			# Standard behavior 
			article_dic = make_article_dic(soup,url)
			article_div = article_div_extractor(soup)
			clean_article_div = article_div_pre_processer (article_div)
			token_dic = article_tokenizer(clean_article_div) 
			b_scores = bayes_processer(token_dic, b_dic)
			article_div_processed = filter_article_div(b_scores, clean_article_div, article_dic)
				
			#Helpers.clear_screen() 
			print article_post_processer(article_div_processed,article_dic)
			break 
			
		break 

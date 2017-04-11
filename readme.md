# Article-To-Text
A python command line utility for intelligently converting webpages into text files

Harvard CS51 Final Project 2015
Nathaniel Burbank

Usage: `./ArticleToText.py url [optional flags]`

For example:

	./ArticleToText.py http://www.seattletimes.com/nation-world/forest-service-may-blow-up-frozen-cows-in-cabin/

Optional flags:

	-f, --file 		Save output to .txt file in the current working directory.
	-h, --help 		Show this help message and exit.
	-r, --rebuild 	Rebuild the Bayes data structure based on the webpages
  					in the training directory and training.tsv file.
	-t, --train 	Run supervised trainer on submitted url. Save results to
  					training directory and Bayes data structure.

## Requirements:

- Python 2.x
- [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/#Download)
- [htmltotxt](https://github.com/aaronsw/html2text)

Both BeautifulSoup and htmltotxt are already included in the distribution.
However, if you have any difficulty running them, the modules can be installed
using one of these two sets of commands:

	sudo easy_install beautifulsoup4
	sudo easy_install htmltotxt

	sudo pip beautifulsoup4
	sudo pip htmltotxt





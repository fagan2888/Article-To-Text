#!/usr/bin/python

### Basic file functions ### 
def write_file_utf(data, filename):
	print "Writing data to", filename, "...",   
	writefile = codecs.open(filename, 'w', 'utf-8')
	writefile.write(data)
	writefile.close()
	print ".",
	print "done" 

def append_file_utf(data, filename):
	print "appending data to", filename, "...",
	try: 
		writefile = codecs.open(filename, 'a', 'utf-8')
		writefile.write(data)
		writefile.close()
		print "done"
		
	except IOError as e:
		print "Unable to find file", filename
		raise NameError('File does not exist...') 


def pickle_data(data, filename):
	print "Pickleing data to", filename, "...",
	file = open(filename, 'wb')
	pickle.dump(data, file)
	file.close()
	print "done" 

def load_pickle(filename):
	print "Unpickling data from file", filename, "...", 
	file = open(filename, 'rb')
	data = pickle.load(file)
	file.close()
	print "done" 
	return data
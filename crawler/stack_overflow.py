# coding=utf8

import urllib
import robotexclusionrulesparser as rerp
from bs4 import BeautifulSoup
from urlparse import urlparse, urljoin


def crawl_web(seed, max_pages, max_depth): # returns index, graph of inlinks
	if is_stackoverflow(seed):
		tocrawl = [[seed, 0]]
	else: 
		print "This seed is not a stackoverflow site!"
		return
	crawled = []
	graph = {}  # <url>, [list of pages it links to]
	index = {} 
	while tocrawl: 
		page, depth = tocrawl.pop()
		print "CURRENT DEPTH: ", depth
		print "PAGES CRAWLED: ", len(crawled)
		if page not in crawled and len(crawled) < max_pages and depth <= max_depth:
			soup, url = get_page(page)
			add_page_to_index(index, page, soup)
			outlinks = get_all_links(soup, url)
			graph[page] = outlinks
			add_new_links(tocrawl, outlinks, depth)
			#print tocrawl
			crawled.append(page)
			#print crawled
	return index, graph

def get_all_links(page, url):
	links = []
	page_url = urlparse(url)
	print "PAGE URL: " , page_url
	if page_url[0]:
		base = page_url[0] + '://' + page_url[1]
		print "BASE URL: " , base
		robots_url = urljoin(base, '/robots.txt')
		print "ROBOTS URL: " , robots_url
	else:
		robots_url = "http://www.stackoverflow-forums.com/robots.txt"
	rp = rerp.RobotFileParserLookalike()
	rp.set_url(robots_url)
	rp.read()
	#print rp
	for link in page.find_all('a'):
		link_url = link.get('href')
		print "Found a link: ", link_url
		#Ignore links that are 'None'.
		if link_url == None: 
			pass
		elif not rp.can_fetch('*', link_url):
			print "Page off limits!" 
			pass		
		#Ignore links that are internal page anchors. 
		#Urlparse considers internal anchors 'fragment identifiers', at index 5. 
		elif urlparse(link_url)[5] and not urlparse(link_url)[2]: 
			pass
		elif urlparse(link_url)[1]:
			links.append(link_url)
		else:
			newlink = urljoin(base, link_url)
			links.append(newlink)
	return links

def add_new_links(tocrawl, outlinks, depth):
    for link in outlinks:
        if link not in tocrawl:
        	if is_stackoverflow(link):
        		tocrawl.append([link, depth+1])

def add_page_to_index(index, url, content):
	try:
		text = content.get_text()
	except:
		return
	words = text.split()
	for word in words:
		add_to_index(index, word, url)
        
def add_to_index(index, keyword, url):
    if keyword in index:
        index[keyword].append(url)
    else:
        index[keyword] = [url]

def lookup(index, keyword):
    if keyword in index:
        return index[keyword]
    else:
        return None

def get_page(url):
	page_url = urlparse(url)
	base = page_url[0] + '://' + page_url[1]
	robots_url = base + '/robots.txt'
	rp = rerp.RobotFileParserLookalike()
	rp.set_url(robots_url)
	rp.read()
	if not rp.can_fetch('*', url):
		print "Page off limits!"
		return BeautifulSoup(""), ""
	if url in cache:
		return cache[url]
	else:
		print "Page not in cache: " + url
		try:
			content = urllib.urlopen(url).read()
			return BeautifulSoup(content), url
		except:
			return BeautifulSoup(""), ""

def compute_ranks(graph):
    d = 0.8 # damping factor
    numloops = 10
    
    ranks = {}
    npages = len(graph)
    for page in graph:
        ranks[page] = 1.0 / npages
    
    for i in range(0, numloops):
        newranks = {}
        for page in graph:
            newrank = (1 - d) / npages
            for node in graph:
                if page in graph[node]:
                    newrank = newrank + d * (ranks[node] / len(graph[node]))
            
            newranks[page] = newrank
        ranks = newranks
    return ranks

def is_stackoverflow(url):
	stackoverflow_urls = ['http://www.stackoverflow.com']
	parsed_url = urlparse(url)
	if parsed_url[1] not in stackoverflow_urls:
		return True
	else:
		return True
        	
cache = {}
max_pages = 1
max_depth = 1
index, graph = crawl_web('http://www.stackoverflow.com/questions',max_pages, max_depth)
ranks = compute_ranks(graph)

print "INDEX: ", index
print ""
print "GRAPH: ", graph
print ""
print "RANKS: ", ranks
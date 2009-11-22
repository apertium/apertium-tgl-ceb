#!/usr/bin/python
# -*- coding: utf-8 -*-
version = "0.1"

import warnings # Because deprecation sounds suck!
warnings.filterwarnings('ignore', category=DeprecationWarning)

import sys, pycurl, StringIO, html5lib #, chardet
from html5lib import treebuilders
from BeautifulSoup import BeautifulSoup

from xml.sax.handler import ContentHandler # XML parsing modules
from xml.sax import make_parser, parseString # XML parser

class dirtyTableHandler(ContentHandler):
	dump = []
	tableCount = 0
	isTable = False
	isTd = False
	tdCount = 0
	isTr = False
	trCount = -1
	anyTag = 0
	output = ""
	predump = []
	def shortOutput(self):
		long1 = 0
		long2 = 0
		for i in range(len(self.dump)):
			if len(self.dump[i][0]) > long1:
				long1 = len(self.dump[i][0])
			if len(self.dump[i][1]) > long2:
				long2 = len(self.dump[i][1])
		for i in range(len(self.dump)):
			if i == 0:
				print "\033[4m{0:{3}}\033[0m  {1:^{4}}  \033[4m{2}\033[0m".format(self.dump[i][0].encode("utf-8"), "\033[4m%s\033[0m" % self.dump[i][1].encode("utf-8"), self.dump[i][4].encode("utf-8"), long1, long2)
			else:
				print "{0:{3}}  {1:{4}}  {2}".format(self.dump[i][0].encode("utf-8"), self.dump[i][1].encode("utf-8"), self.dump[i][4].encode("utf-8"), long1, long2)
	 
	def startElement(self, tag, attrs):
		if tag == "table":
			self.tableCount += 1
			if self.tableCount == 2:
				self.isTable = True
		elif tag == "td":
			self.isTd = True
			self.tdCount += 1
		elif tag == "tr":
			self.isTr = True
			self.trCount += 1
			#if self.trCount >= 0:
			#	self.dump.append([])
		elif tag:
			self.anyTag += 1
			if tag == "b":
				if self.output[-1:] != "-":
					self.output += " "
			

	def characters(self, content):
		if self.isTd and self.tdCount > 2:
			self.output += content.strip()

	def endElement(self, tag):
		if tag == "table":
			self.isTable = False
		elif tag == "tr":
			if self.trCount > 2:
				self.dump.append(self.predump)
				self.predump = []
			self.isTr = False
			self.tdCount = 0
		elif tag == "td":
			if self.tdCount > 2:
				self.predump.append(self.output.strip().strip())
			self.output = ""
			self.isTd = False
		elif tag:
			self.anyTag -= 1
			if tag == "font":
				self.output += " "


url = "http://baseportal.com/cgi-bin/baseportal.pl?htx=/fileng/allsearch&list=100"
args = ''
oFlag = False
oFile = ""
arglen = len(sys.argv)
x = 1
def usage():
	print "scream-filengnor.py [-o output.html] <search query>"
	print "Totally sexy FilEngNor parsing with awesome column layout!"
	exit(0)

if arglen > 1:
	if sys.argv[1] in ["--help", "-h"]:
		usage()
	if sys.argv[1] in ["--version", "-v"]:
		print version
		exit(0)
	if sys.argv[1] == "-o":
		if arglen > 3:
			oFlag = True
			oFile = sys.argv[2]
			x = 3
		else:
			print "Now you know you shouldn't do that. >:|"
			exit(1)
	if arglen > x:
		for i in sys.argv[x:]:
			args += "%s " % i
			#print "Query: %s" % args
	else: 
		print "Query missing, exiting."
		usage()
else:
	usage()

pf = [	('_fullsearch==', args),
	('list=', '45000')  ]

out = StringIO.StringIO()
c = pycurl.Curl()
c.setopt(c.URL, url)
c.setopt(c.HTTPPOST, pf)
c.setopt(c.WRITEFUNCTION, out.write)
c.perform()
c.close()

out = out.getvalue()
x = out.find("<html>")
out = out[x:].replace("\n", "").replace("ISO-8859-1", "UTF-8")
parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("BeautifulSoup"))
soup = parser.parse(out)
out =  soup.html.table.prettify()
if oFlag:
	f = open(oFile, 'w')
	f.write(out)
	f.close()

parser = make_parser()
o = dirtyTableHandler()
parser.setContentHandler(o)
parser.parse(StringIO.StringIO(out))
o.dump.pop(0) # Fix for random error that I cant be bothered to work out
o.dump.pop(len(o.dump)-1) # <3 half-assed cleanups
o.shortOutput()

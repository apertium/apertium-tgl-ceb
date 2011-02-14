#!/usr/bin/env python2.7

# v0.1

import lxml.etree as etree
import cStringIO as StringIO
import sys, os, argparse #etc etc

def sanitise_name(p):
	if type(p) is str:
		return p.replace('/', '')
	
	for i in p.items():
		if i[0] == 'n':
			# TODO: check for stuff other than /
			return i[1].replace('/', '')
	return None

W = 80
buf = dict()

argparser = argparse.ArgumentParser(
	description="Convert Apertium dictionaries to lexc."
	)
argparser.add_argument("dix_input", nargs=1, help="Apertium dictionary input file")
argparser.add_argument("lexc_output", nargs=1, help="Lexc dictionary output file")
args = argparser.parse_args()

outfile = open(args.lexc_output[0], 'w')
root = etree.parse(args.dix_input[0]).getroot()
sdefs = None
pardefs = None
sections = []

# Pan out all the fun bits
for i in root.getchildren():
	if i.tag == "sdefs" and sdefs == None:
		sdefs = i
	elif i.tag == "pardefs" and pardefs == None:
		pardefs = i
	elif i.tag == "section":
		sections.append(i)
	elif i.tag != "alphabet":
		print "WARNING: '%s' found, but shouldn't have been!" % i.tag

# Check they all exist
msg = "ERROR: %s not found; required."
if sdefs == None:
	print msg % "sdefs"
	sys.exit(1)
if pardefs == None:
	print msg % "pardefs"
	sys.exit(1)
if sections == []:
	print msg % "section"
	sys.exit(1)

# STEP 0: Put a header, because they're awesome.
buf['top'] = StringIO.StringIO()
buf['top'].write("! Dictionary generated from %s.\n" % args.dix_input[0]) 

# STEP 1: Convert sdefs to Multichar_Symbols
buf['top'].write("Multichar_Symbols\n")

buf['mchar'] = StringIO.StringIO()
for s in sdefs.getchildren():
	if s.tag == "sdef":
		n = None
		for t in s.items():
			if t[0] == 'n':
				n = t[1]
		if n == None:
			print "WARNING: no 'n' found for sdef!"
		else:
			if (buf['mchar'].tell() + len(n) + 2) > W:
				buf['top'].write("%s\n" % buf['mchar'].getvalue())
				buf['mchar'] = StringIO.StringIO()
			buf['mchar'].write("+%s " % n)
	elif s.tag != etree.Comment:
		print "WARNING: %s found in sdefs. Why?" % s.tag
buf['top'].write("%s\n" % buf['mchar'].getvalue())
del buf['mchar']

# STEP 2: Prep LEXICON Root for DESTRUCTION
buf['root'] = StringIO.StringIO()
buf['root'].write("\nLEXICON Root\n")

# STEP 3: Convert pardefs to Lexicons
#buf['lex_pardefs'] = StringIO.StringIO()
#buf['lex_pardefs'].write("LEXICON Paradigms\n")

buf['pardefs'] = StringIO.StringIO()
buf['pardefs'].write("\n!<!--PARDEFS-->")

for pardef in pardefs.getchildren():
	if pardef.tag == "pardef":
		buf['pardefs'].write("\nLEXICON pardef_%s\n" % sanitise_name(pardef))
		for e in pardef.getchildren():
			for f in e.getchildren():
				if f.tag == "p":
					surface = ""
					lexical = ""
					for g in f.getchildren():
						if g.tag == "l":
							for trap in g.getchildren():
								if trap.tag == "a":
									surface = trap.tail.strip()
								#TODO: find more tags like a
							if g.text is not None and surface == "":
								surface = g.text.strip()

						if g.tag == "r":
							if type(g.text) != type(None):
								lexical += g.text
							for trap in g.getchildren():
								for trapsauce in trap.items(): 
									if trapsauce[0] == 'n':
										lexical += "+%s" % trapsauce[1]
					buf['pardefs'].write("%s:%s\t# ;\n" % (lexical, surface))
				#TODO: rest of tags
				
	elif pardef.tag != etree.Comment:
		print "WARNING: %s found in pardefs. Why?" % p.tag

# STEP 4: Now for sections into Lexicons
buf['sections'] = []
for i in range(len(sections)):
	buf['sections'].append(StringIO.StringIO())
	n_id = ""
	n_type = ""
	for th in sections[i].items():
		if th[0] == "id":
			n_id = th[1]
		if th[0] == "type":
			n_type = th[1]
	if i == 0:
		buf['sections'][i].write("\n!<!--SECTIONS-->")
	buf['sections'][i].write("\nLEXICON section_%s_%s\n" % (n_id, n_type))
	buf['root'].write("\tsection_%s_%s ;\n" % (n_id, n_type)) 
	for e in sections[i].getchildren():
		if e.tag == "e":
			surface = ""
			lexical = ""
			par = ""
			# TODO: possible recursion here
			for f in e.getchildren():
				if f.tag == "p":
					for g in f.getchildren():
						pass # TODO: cbf right now
				if f.tag == "i":
					surface = lexical = f.text
				if f.tag == "par":
					par = f.items()[0][1]
			if surface == lexical:
				buf['sections'][i].write("%s\tpardef_%s ;\n" % (surface, sanitise_name(par)))
			else:
				buf['sections'][i].write("%s:%s\tpardef_%s ;\n" % (lexical, surface, sanitise_name(par)))
		elif e.tag != etree.Comment:
			print "WARNING: %s found in section. Why?" % e.tag

			

# STEP 0xFF: Write results to file
for f in ('top', 'root', 'pardefs'): 
	outfile.write(buf[f].getvalue())
for f in (buf['sections']):
	outfile.write(f.getvalue())

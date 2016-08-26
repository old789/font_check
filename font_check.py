#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import os
import re
import sys
import fnmatch
import subprocess

fonts={}

def fontsReadFrom(subtitleFile):
	tf=''
	tst1=re.compile('^\s*\[.+\].*$')
	tst2=re.compile('^\s*\[\S+\s+Styles\].*$')
	tst3=re.compile('^\s*Style\:\s+.+$')
	tst4=re.compile('^\s*\[\s*Events\s*\].*$')
	tst5=re.compile('^\s*Dialogue\:.*\{(.+?)\}.*$')
	styleSection=False
	eventSection=False
	infile=open(subtitleFile, 'r')
	for stri in infile:
		if styleSection:
			if tst1.match(stri):
				styleSection=False
				if tst4.match(stri):
					eventSection=True
				continue
			elif tst3.match(stri):
				tf=stri.split(',')[1]
				if tf.find('@') == 0:
					tf=tf.replace('@','')
				if not tf in fonts:
					fonts[tf]=os.path.basename(subtitleFile)
				continue
		elif eventSection:
			if tst1.match(stri):
				eventSection=False
				if tst2.match(stri):
					styleSection=True
				continue
			else:
				rc=tst5.match(stri)
				if rc:
					tf=rc.group(1)
					# dirty bypass of 'python backslash plague'
					i=tf.find('\\fn')
					if i < 0:
						continue
					tf=tf[i+3:]
					i=tf.find('\\')
					if i > -1:
						tf=tf[0:i]
					#print 'Found',tf,'in event section' 
					if tf.find('@') == 0:
						tf=tf.replace('@','')
					if not tf in fonts:
						#print 'Added',tf,'in event section'
						fonts[tf]=os.path.basename(subtitleFile)
					continue
		elif tst2.match(stri):
			styleSection=True
			eventSection=False
			continue
		elif tst4.match(stri):
			styleSection=False
			eventSection=True
			continue
	infile.close()

def findFont(fontName):
	tst1=re.compile('^\s*(\S+\.\S+)\:\s+\"(.+?)\".*$')
	cmdString='fc-match \"'+fontName+'\"'
	p = subprocess.Popen(cmdString, stdout=subprocess.PIPE,shell=True)
	(output, err) = p.communicate()
	p_status = p.wait()
	aIn=output.splitlines()
	if p_status > 0:
		sys.stderr.write('!!Error with font \"'+fontName+'\"\n')
		return([])
	else:
		if len(aIn) < 1:
			sys.stderr.write('!!Error with font \"'+fontName+'\" - fc-match return nothing\n')
			return([])
		elif len(aIn) > 1:
			sys.stderr.write('! Warning: font \"'+fontName+'\" - multyline answer\n')
		rc=tst1.match(aIn[0])
		if rc:
			return([rc.group(2),rc.group(1)])
		else:
			sys.stderr.write('!!Error with font \"'+fontName+'\" - nothing found\n')
		return([])


if len(sys.argv) < 2:
	sys.stderr.write('!!Usage: <progname> <path to subtitles file or dir>\n')
	exit(1)
f=sys.argv[1]
if os.path.isfile(f):
	fontsReadFrom(f)
elif os.path.isdir(f):
	indexOfLst=os.listdir(f)
	if len(indexOfLst) > 0:
		for item in indexOfLst:
			if fnmatch.fnmatch(item.lower(), "*.ass"):
				fontsReadFrom(os.path.join(f,item))

t=[]
fontList=sorted(fonts.keys())
for i in fontList:
	t=findFont(i)
	if len(t) > 0:
		if t[0] != i:
			print '! Font "'+i+'" not found, proposed "'+t[0]+'"'
		else:
			print '  Font "'+i+'" found, file: '+t[1]

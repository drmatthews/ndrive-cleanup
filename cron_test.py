#!/usr/bin/env python

import os
import argparse

def delete_file(path):
	os.remove(path)

if __name__=='__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-p", "--path", type=str, help="enter the path")
	args = parser.parse_args()	
	filename = args.path
	delete_file(filename)
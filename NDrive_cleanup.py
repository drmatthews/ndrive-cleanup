import os
import sys
import datetime
import time
import csv
import argparse

deletedays = 30 #delete files on dest older than this many days
now = time.time();
deletesecs = 1200#deletedays*24*60*60;
EXCEPTIONS = ['daniel','isma','dmitry']

def write_log(fpath,dirs):
	unique_dirs = set(dirs)
	with open(fpath, 'wb') as myfile:
		wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
		for row in unique_dirs:
			wr.writerow([row,])

def modification_date(filename):
    t = os.path.getmtime(filename)
    return t,datetime.datetime.fromtimestamp(t)

def main(walk_dir,verbose,log):
	global EXCEPTIONS

	EXCEPTIONS = [os.path.join(walk_dir,ex) for ex in EXCEPTIONS]
	print EXCEPTIONS

	to_delete = []
	last_mod = []
	to_delete_root = []
	size = 0
	for root, subdirs, files in os.walk(walk_dir):
		print root
		for f in files:
			fpath = os.path.join(root,f)
			t, mtime = modification_date(fpath)
			if ((now - t) > deletesecs) and (root not in EXCEPTIONS):
				size += os.path.getsize(fpath)
				#print 'delete ', fpath, 'last mod on: ',mtime
				to_delete.append(fpath)
				last_mod.append(mtime)
				to_delete_root.append(root)
			else:
				pass
				#print 'keep', fpath, 'last mod on: ',mtime

	if verbose:
		for tod in to_delete:
			print 'Delete: ', tod, ' last mod on: ',mtime

	print 'There are ',len(to_delete),' items to be deleted.'
	print 'this will free up ', float(size)/1e9,' Gb'
	
	if log:
		write_log(log,to_delete_root)

	decision = raw_input('Continue with deletion? (Y/n)  ')

	if decision == 'Y':
		for fp in to_delete:
			try:
				os.remove(fp)
			except:
				os.chmod(filepath, stat.S_IWRITE)
				os.remove(filepath)
		for folder in to_delete_root:
			try:
				os.rmdir(folder) #os.rmdir won't delete non-empty dirs
			except OSError as ex:
				pass
	else:
		return

if __name__=='__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--drive", type=str, help="enter the path to the network drive")
	parser.add_argument("-v", "--verbose", action='store_true',help="list everything that will be deleted")
	parser.add_argument("-w", "--writefile", type=str, help="write root dirs to csv file")
	args = parser.parse_args()
	if args.drive:
		print 'drive to scan', args.drive
		walk_dir = args.drive
	else:
		walk_dir = '/media/NDrive' 
		print 'reverting to default'
	log = None	
	if args.writefile:
		log = args.writefile
		print 'writing root dirs to: ', log  
	main(walk_dir,args.verbose,log)


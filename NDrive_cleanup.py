import os
import sys
import datetime
import time
import csv
import argparse
import stat

deletedays = 32 #delete files on dest older than this many days
now = time.time();
deletesecs = deletedays*24*60*60;
EXCEPTIONS = ['Dan','Isma','JH (Do Not Delete)']

def write_log(fpath,dirs,dates,folder_dates):
	with open(fpath, 'wb') as myfile:
		wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
		for row in zip(dirs,dates,folder_dates):
			wr.writerow(row)

def modification_date(filename):
    t = os.path.getmtime(filename)
    return t,datetime.datetime.fromtimestamp(t)

def main(walk_dir,verbose,log):
	global EXCEPTIONS

	EXCEPTIONS = [os.path.join(walk_dir,ex) for ex in EXCEPTIONS]
	print EXCEPTIONS

	to_delete = []
	last_mod = []
	last_mod_root = []
	to_delete_root = []
	size = 0
	for root, subdirs, files in os.walk(walk_dir):
		for f in files:
			fpath = os.path.join(root,f)
			rt,rmtime = modification_date(root)
			t, mtime = modification_date(fpath)
			if ((now - rt) > deletesecs) and ('Dan' not in root):
				size += os.path.getsize(fpath)
				#print 'delete ', fpath, 'last mod on: ',mtime
				to_delete.append(fpath)
				last_mod.append(mtime)
				last_mod_root.append(rmtime)
				to_delete_root.append(root)
			else:
				pass
				#print 'keep', fpath, 'last mod on: ',mtime

	if verbose:
		for tod,tod_mtime in zip(to_delete,last_mod):
			print 'Delete: ', tod, ' last mod on: ',tod_mtime

	print 'There are ',len(to_delete),' items to be deleted.'
	print 'this will free up ', float(size)/1e9,' Gb'
	
	if log:
		write_log(log,to_delete,last_mod,last_mod_root)

	decision = raw_input('Continue with deletion? (Y/n)  ')

	if decision == 'Y':
		for fp in to_delete:
			try:
				os.remove(fp)
			except:
				os.chmod(fp, stat.S_IWRITE)
				os.remove(fp)
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
		walk_dir = '/media/nicshare' 
		print 'reverting to default'
	log = None	
	if args.writefile:
		log = args.writefile
		print 'writing root dirs to: ', log  
	main(walk_dir,args.verbose,log)


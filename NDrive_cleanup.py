import os
import sys
import datetime
import time
import csv

walk_dir = '/media/NDrive'
deletedays = 30 #delete files on dest older than this many days

def modification_date(filename):
    t = os.path.getmtime(filename)
    return t,datetime.datetime.fromtimestamp(t)

#first, delete files older than X days on dest
now = time.time();
deletesecs = deletedays*24*60*60;

to_delete = []
to_delete_root = []
size = 0
for root, subdirs, files in os.walk(walk_dir):
    for f in files:
        fpath = os.path.join(root,f)
    	t, mtime = modification_date(fpath)
	if ((now - t) > deletesecs) and ('do not delete' not in root.lower()):
	    size += os.path.getsize(fpath)
            #print 'delete ', fpath, 'last mod on: ',mtime
            to_delete.append(fpath)
            to_delete_root.append(root)
        else:
            pass
            #print 'keep', fpath, 'last mod on: ',mtime

print 'There are ',len(to_delete),' items to be deleted.'
print 'this will free up ', float(size)/1e9,' Gb'

with open('/home/daniel/Documents/users_with_old_data.csv', 'wb') as myfile:
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    for row in to_delete_root:
        wr.writerow([row,])
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
    exit()


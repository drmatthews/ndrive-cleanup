import os
import sys
import datetime
import time
import csv
import argparse
import stat
from scandir import walk

deletedays = 32 #delete files on dest older than this many days
now = time.time()
deletesecs = deletedays*24*60*60
# EXCEPTIONS = ['Dan','Isma']
EXCEPTIONS = []

def write_log(fpath,dirs,folder_dates,file_dates,age):
    with open(fpath, 'w') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        for row in zip(dirs,folder_dates,file_dates,age):
            wr.writerow(row)

def modification_date(filename):
    t = os.path.getmtime(filename)
    return t,datetime.datetime.fromtimestamp(t)

def main(walk_dir,verbose,log,force):
    # global EXCEPTIONS

    # EXCEPTIONS = [os.path.join(walk_dir,ex) for ex in EXCEPTIONS]
    print("EXCEPTIONS {}".format(EXCEPTIONS))

    to_delete = []
    last_mod = []
    last_mod_root = []
    to_delete_root = []
    age = []
    size = 0
    s = time.time()
    upperlimit = 100 * 24 * 60 * 60
    for root, subdirs, files in walk(walk_dir):
        for f in files:
            fpath = os.path.join(root,f)
            if '.Trash' not in fpath:
                del_path = fpath
                rt,rmtime = modification_date(root)
                t, mtime = modification_date(del_path)
                if ((now - t) > deletesecs) and ((now - t) < upperlimit):
                    size += os.path.getsize(del_path)
                    to_delete.append(del_path.encode('ascii','ignore'))
                    last_mod.append(mtime)
                    last_mod_root.append(rmtime)
                    to_delete_root.append(root)
                    age.append((now - t))
                else:
                    pass
    print("traversing dirs took {} seconds".format(time.time() - s))

    to_delete_without_exceptions = [f for f in to_delete if f not in EXCEPTIONS]
    to_delete_root_without_exceptions = [d for d in to_delete_root if os.path.dirname(d) not in EXCEPTIONS]

    if verbose:
        for tod,tod_mtime in zip(to_delete,last_mod):
            print('Delete: {0} last mod on: {1}'.format(tod, tod_mtime))

    print('There are {} items to be deleted.'.format(len(to_delete)))
    print('this will free up {} Gb'.format(float(size)/1e9))

    if force:
        decision = 'Y'
    else:
        decision = input('Continue with deletion? (Y/n)  ')

    if decision == 'Y':
        if log:
            write_log(log,to_delete_without_exceptions,last_mod,last_mod_root,age)

        for fp in to_delete_without_exceptions:
            try:
                os.remove(fp)
            except OSError:
                continue
                # os.chmod(fp, stat.S_IWRITE)
                # os.remove(fp)

        for folder in to_delete_root_without_exceptions:
            try:
                os.rmdir(folder) #os.rmdir won't delete non-empty dirs
            except OSError as ex:
                pass
    else:
        return

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--drive", type=str, help="enter the path to the network drive")
    parser.add_argument("-f", "--force", action='store_true', help="deletes without warning")
    parser.add_argument("-v", "--verbose", action='store_true', help="list everything that will be deleted")

    args = parser.parse_args()
    if args.drive:
        print('drive to scan {}'.format(args.drive))
        walk_dir = args.drive
        force = None
        if args.force:
            force = True

        date = str(datetime.date.today())
        folder = walk_dir[7:]
        if '/' in folder:
            folder = folder[:-1]
        log =  folder + '-deleted-' + date + '.csv'
        print('writing root dirs to: {}'.format(log))  
        main(walk_dir,args.verbose,log,force)       
    elif args.drive is None:
        print('You need to provide at least the folder to clear. Pass -h to see options.')


        


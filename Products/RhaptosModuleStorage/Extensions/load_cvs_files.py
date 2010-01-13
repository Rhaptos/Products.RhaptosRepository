#!/usr/bin/python
import psycopg
import os
import sys
import md5
import cvs
import subprocess as sp

def saveModule(modver):
    """Save all the files in a module to cvs"""
    modid,version=modver
    #Two cases: new module (no older version in CVS) and new version of existing
    # Here be dragons - pycvs is a bit funky: need to set cwd
    cwd = os.getcwd()
    cur = con.cursor()
    wd=cvs.CVSWorkingDir('/var/lib/cvs','xmlpages/%s' % modid)
    try:
        wd.checkout()
        target=wd.path
        newmod=0
    except cvs.CVSCheckoutError:
    #perhaps it's new
        wd=cvs.CVSWorkingDir('/var/lib/cvs','xmlpages')
        wd.checkout(recursive=0)
        target=os.path.join(wd.path,modid)
        os.mkdir(target)
        newmod=1

    cur.execute('select module_ident,submitlog from modules where moduleid = %s and version = %s' , (modid,version))
    res = cur.fetchall()
    if not res:
        "something happened %s/%s" % (moddir,res)
        return
        
    mod_ident,message = res[0]
    
    cur.execute("select * from module_files natural join files where module_ident = %s", [mod_ident])
    modfiles=cur.dictfetchall()
    for f in modfiles:
        fpath=os.path.join(target,f['filename'])
        newfile = not(os.path.isfile(fpath))
        fd=open(fpath,'w')
        fd.write(f['file'])
        fd.close()
        if newfile and not newmod:
            wd.add(f['filename'])

    os.chdir(wd.path)
    if newmod:
        wd.add(target)
    wd.commit(message,version)


def main(mods_vers):
    print "%s modules to store" % len(mods_vers)

    for mod in mods_vers:
        print '%s%% Storing %s' % ((mods_vers.index(mod)*100)/len(mods_vers),mod)
        saveModule(mod)

if __name__ == '__main__':
  
    output = sp.Popen(["pg_lsclusters", "-h"], stdout=sp.PIPE).communicate()[0]
    port = [line.split()[2] for line in output.split('\n') if line.startswith('8.2     main')][0]
    con = psycopg.connect('dbname=repository user=rhaptos port=%s' % (port))
    mod_vers=[x.split("/") for x in sys.argv[1:]]
    main(mod_vers)

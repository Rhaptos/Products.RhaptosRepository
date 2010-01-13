#!/usr/bin/python
import psycopg
import os
import sys
import md5
import cvs
import subprocess as sp



def pushfile(file):
    """get a files fid from the db, saving to db if needed'"""
    bits=file.read()
    m = md5.new(bits).hexdigest()

    cur = con.cursor()
    cur.execute('select fileid,file from files where md5 = %s', [m])
    res = cur.dictfetchall()
    for r in res:
        if r['file'] == bits:
            print " repeat"
            return r['fileid']
    #fell through: no results, or have an md5 collision! push file to db
    cur.execute('insert into  files (file) values (%s) returning fileid' , [psycopg.Binary(bits)])
    res = cur.dictfetchall()
    fid = res[0]['fileid']
    con.commit()

    return fid


def saveModule(moddir):
    """Save all the files in a module to db"""
    mod = os.path.basename(moddir)
    
    # Here be dragons - pycvs is a bit funky
    cwd = os.getcwd()
    cur = con.cursor()
    wd=cvs.CVSWorkingDir('/var/lib/cvs','xmlpages%s/%s' % (instance,moddir))
    try:
        wd.checkout()
    except:
        print "couldn't checkout %s" % moddir
        return
    c=cvs.CVSFile(wd.path,'index.cnxml')
    os.chdir(wd.path)
#    try:
#        logs=c.log()
#    except:
#    print "something funny w/ the logs, trying DB"
    logs=[]
    cur.execute('select version as revision from modules where moduleid = %s order by module_ident desc' , (mod,))
    logs = cur.dictfetchall()

    for log in logs:
        rev=log['revision']
        cur.execute('select module_ident from modules where moduleid = %s and version = %s' , (mod,rev))
        res = cur.fetchall()
        if not res:
            "something happened %s/%s" % (moddir,res)
            continue

        mod_ident = res[0][0]

        cur.execute("select 1 from module_files where module_ident = %s and filename = 'index.cnxml'", [mod_ident])
        res = cur.fetchall()
        if res:
            print "Already stored: %s/%s" % (moddir,rev)
            continue

        wd.update(revision=rev)

        print rev

        files = [f for f in wd.listfiles() if f not in ['CVS','.cvsignore'] and not f.endswith('.swp')]
        for fname in files:
            print "  %s" % fname,
            f=open(fname)
            fid = pushfile(f)
            f.close()
            try:
                cur.execute('insert into module_files (module_ident,fileid,filename) values (%s,%s,%s)' , (mod_ident,fid,fname))
            except:
                print "Probable duplicate error"
            con.commit()
    os.chdir(cwd)
    print
    wd.release()

def main():
    #mods = [m for m in os.listdir(os.getcwd()) if m.startswith('m')]
    cur=con.cursor()
    cur.execute("select distinct moduleid from modules lm where not exists (select 1 from module_files where module_ident = lm.module_ident and filename='index.cnxml') order by moduleid")
    res=cur.fetchall()
    mods=[r[0] for r in res]
    print "%s modules to store" % len(mods)

    for mod in mods:
        print '%s%% Storing %s' % ((mods.index(mod)*100)/len(mods),mod)
        saveModule(mod)


if __name__ == '__main__':
    try:
        instance = '-%s' % sys.argv[1]
    except IndexError:
        instance = ''
    output = sp.Popen(["pg_lsclusters", "-h"], stdout=sp.PIPE).communicate()[0]
    port = [line.split()[2] for line in output.split('\n') if line.startswith('8.2     main')][0]
    con = psycopg.connect('dbname=repository%s user=rhaptos port=%s' % (instance,port))
    main()


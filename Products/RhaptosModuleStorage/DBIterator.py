from ZPublisher.Iterators import IStreamIterator
import psycopg2.psycopg1 as psycopg


class rhaptosdb_iterator:
    """
    a simple class which implements an iterator that returns a
    fixed-sized sequence of bytes. from a Rhapotos repository db.
    """

    __implements__ = (IStreamIterator,)

    def __init__(self, name, modid, version, db_connect, streamsize=1<<16):
        self.name = name
        self.db = psycopg.connect(db_connect)
        self.streamsize = streamsize
        self.pos = 0
        self.statement = "FROM modules NATURAL JOIN module_files NATURAL JOIN files WHERE moduleid = '%s' AND version = '%s' AND filename = '%s'" % (modid,version,name)

    def next(self):
        cur = self.db.cursor()
        cur.execute('SELECT substr(file,%s,%s) AS data %s' % (self.pos,self.streamsize,self.statement))
        res = cur.dictfetchone()
        if res:
            data = res['data']
        else:
            raise StopIteration
        self.pos += self.streamsize

        return str(data)

    def __len__(self):
        cur = self.db.cursor()
        cur.execute('SELECT length(file) %s' % (self.statement))
        res = cur.dictfetchone()
        if res:
            size = res['length']
        else:
            size = 0
        return size

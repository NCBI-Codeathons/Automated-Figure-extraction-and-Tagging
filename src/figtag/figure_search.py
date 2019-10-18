
import sys
import sqlite3


def querier(query, database_file='ImageIndex.sqlite'):

    def db_select(db_,
                  tbl_, cols='*',
                  cnt=False,
                  cond=None,
                  cmpr=None,
                  vlu=None):

        db = db_

        conn = sqlite3.connect(db)
        c = conn.cursor()

        if cols == '*':
            statement = 'SELECT *'
        else:
            if not isinstance(cols, list):
                raise TypeError('cols must be a list')
            if cnt is False:
                statement = 'SELECT ('+','.join(cols)+') '
            if cnt is True:
                statement = 'SELECT count('+','.join(cols)+') '

        statement += (' FROM {tbl} calc INNER JOIN '
                      ' users raw ON calc.idx=raw.idx ').format(tbl=tbl_)

        if (cond is not None) & (cmpr is not None) & (vlu is not None):
            statement += ' WHERE instr({v}, {c});'.format(c=cond, s=cmpr, v=vlu)
            # statement += ' WHERE {c} {s} {v};'.format(c=cond, s=cmpr, v=vlu)
            pass
        else:
            raise Exception('clms, cmpr, and vlu arguments\
                            must be used together')

        try:
            c.execute(statement)
            results = c.fetchall()
            c.close()

            return results
        except Exception:
            print('select failed')
            print(statement)
            print(sys.exc_info()[0], sys.exc_info()[1])
            raise sys.exc_info()

    result = db_select(db_=database_file,
                       tbl_='calcData',
                       cols=['raw.uid'],
                       cnt=False,
                       cond="'" + query + "'",
                       cmpr='',
                       vlu="(ifnull(calc.mesh, ''))")

    return result

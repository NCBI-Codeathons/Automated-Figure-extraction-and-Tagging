def querier(query, database_file='ImageIndex.sqlite'):

    def db_select(db_,
                  tbl_, cols='*',
                  cnt=False,
                  cond=None,
                  cmpr=None,
                  vlu=None):

        import sys
        import sqlite3

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

        statement += ' FROM {tbl}'.format(tbl=tbl_)

        if (cond is not None) & (cmpr is not None) & (vlu is not None):
            statement += ' WHERE {c} {s} {v};'.format(c=cond, s=cmpr, v=vlu)
        elif (cond is None) & (cmpr is None) & (vlu is None):
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

    result = db_select(database_file,
                       'calcData',
                       cols=['uid'],
                       cnt=False,
                       cond=query,
                       cmpr='IN',
                       vlu='mesh')

    return result

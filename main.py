import matplotlib.pyplot as plt
import mca
import dmsql
import MySQLdb

# establish connection
db = MySQLdb.connect(host="10.233.1.2",
                     user="nox",
                     passwd="afj;49",
                     db="proj2")

def curprint(cur):
    for row in cur.fetchall():
        print row
    print("\n")

def dmexecute(queryarr, isdict=False):
    if(isdict):
        cur = db.cursor(MySQLdb.cursors.DictCursor)
    else:
        cur = db.cursor()

    for q in queryarr:
        cur.execute(q)
    db.commit()
    return cur


def main():
    print dmsql.colnameRet('diabetic')
    mycur = dmexecute(dmsql.colnameRet('diabetic'))
    curprint(mycur)
    mycur.close()




    db.commit()
    db.close()
main()

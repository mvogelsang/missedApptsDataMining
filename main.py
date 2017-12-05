import matplotlib.pyplot as plt
import mca
import dmsql
import MySQLdb
import numpy as np

# establish connection
db = MySQLdb.connect(host="10.233.1.2",
                     user="nox",
                     passwd="afj;49",
                     db="proj3")
curtable = 'preproc'

def rowprint(fetched, prep="", extra=False):
    for row in fetched:
        print prep+str(row)
    if(extra):
        print ""

def dmexecute(queryarr, isdict=False):
    if(isdict):
        cur = db.cursor(MySQLdb.cursors.DictCursor)
    else:
        cur = db.cursor()

    for q in queryarr:
        cur.execute(q)
    db.commit()
    return cur

def uniqcounter(usetable=curtable):
    mycur = dmexecute(dmsql.colnameRet(usetable))
    for row in mycur.fetchall():
        col = row[0]
        distcur =  dmexecute(dmsql.numdistinct(col, usetable))
        statcur =  dmexecute(dmsql.statfinder(col, usetable))
        stats = statcur.fetchall()[0]
        res = distcur.fetchall()
        print str(col) + ": " + str(res[0][0])
        print ("AVG:"+ str(stats[0]) +", STDDEV:"+ str(stats[1]) +", MAX:"+ str(stats[2]) +", MIN:"+ str(stats[3]))
        distcur.close()
        statcur.close()
        if(res[0][0] < 500):
            gengraphs(col)
        print ""
    mycur.close()

def bchrt(cats,counts,acolor,ax):
    width = .8
    indices = np.arange(len(cats))*1.5

    bars = ax.bar(indices, counts, width=width,
            color=acolor, tick_label = cats)
    ax.set_xticks(indices)
    ax.set_ylabel('number of instances')

    return bars


def gengraphs(col, usetable=curtable):
    mycur = dmexecute(dmsql.categoricalcounter(col, usetable))
    res = mycur.fetchall()
    mycur.close()
    rowprint(res, "\t")

    fig, ax = plt.subplots(1,1,True,True )

    mycur = dmexecute(dmsql.categoricalcounter(col, usetable))
    res = mycur.fetchall()
    cats, counts = zip(*res)
    mycur.close()
    r1 = bchrt(cats, counts, 'b', ax)

    mycur = dmexecute(dmsql.categoricalcounter(col, usetable, True, 'Yes'))
    res = mycur.fetchall()
    cats, counts = zip(*res)
    mycur.close()
    r2 = bchrt(cats, counts, 'r', ax)


    fig.suptitle("Appointment Distributions by " +col, fontsize=18)
    fig.set_figwidth(10, forward=True);
    plt.legend((r1,r2), ('Made', 'Missed'))
    plt.show()
    plt.close()

def preprocess():
    mycur = dmexecute(dmsql.preTabCreator)
    mycur.close()

def gencsv(tab):
    

def main():
    # preprocess()
    # uniqcounter();

    db.commit()
    db.close()
main()

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

def bchrt(cats,counts,acolor,ax,atitle):
    width = .8
    indices = np.arange(len(cats))*1.5
    bars = ax.bar(indices, counts, width=width, color=acolor, tick_label = cats)
    ax.set_xticks(indices)
    ax.set_ylabel('number of instances')
    ax.set_title(atitle)

    return bars


def gengraphs(col, usetable=curtable):
    mycur = dmexecute(dmsql.categoricalcounter(col, usetable))
    res = mycur.fetchall()
    mycur.close()
    rowprint(res, "\t")

    fig, (ax1, ax2) = plt.subplots(1,2,True,False )

    mycur = dmexecute(dmsql.categoricalcounter(col, usetable))
    res = mycur.fetchall()
    catstot, countstot = zip(*res)
    mycur.close()
    r1 = bchrt(catstot, countstot, 'b', ax1, "Numeric Totals")

    mycur = dmexecute(dmsql.categoricalcounter(col, usetable, True, 'Yes'))
    res = mycur.fetchall()
    catsmiss, countsmiss = zip(*res)
    mycur.close()
    r2 = bchrt(catsmiss, countsmiss, 'r', ax1, "Numeric Totals")

    mycur = dmexecute(dmsql.categoricalcounter(col, usetable, True, 'No'))
    res = mycur.fetchall()
    catsmade, countsmade = zip(*res)
    mycur.close()
    percentages = []
    for i in range(len(countstot)):
        percentages.append(max((1.0-float(countsmade[i])/float(countstot[i]))*100.0, float(countsmiss[i])/float(countstot[i])*100.0))
    r3 = bchrt(catstot, percentages, 'g', ax2, "percent missed")


    fig.suptitle("Appointment Distributions by " +col, fontsize=18)
    fig.set_figwidth(15, forward=True);
    ax1.legend((r1,r2), ('Made Appointments', 'Missed Appointments'))
    plt.show()
    plt.close()

def prepnclean():
    mycur = dmexecute(dmsql.preTabCreator)
    mycur.close()

def gencsv(cols='*', tab='preproc', clause="1=1"):
    mycur = dmexecute(dmsql.csvgetter(cols, tab, clause))
    res = mycur.fetchall()
    mycur.close()
    print cols
    for row in res:
        out = ""
        for item in row:
            out = out+str(item)+','
        out = out[0:-1]
        print out
def main():
    # prepnclean()
    uniqcounter();
    # gencsv(dmsql.simplecsvcols)
    db.commit()
    db.close()
main()

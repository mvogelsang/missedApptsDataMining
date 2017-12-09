import matplotlib.pyplot as plt
import mca
import dmsql
import MySQLdb
import numpy as np
import statsmodels.stats.proportion as propm

# establish connection
db = MySQLdb.connect(host="10.233.1.2",
                     user="",
                     passwd="",
                     db="")
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

def grabval(crit):
    statcur =  dmexecute(dmsql.criteriaSuccess(crit))
    stats = statcur.fetchall()
    statcur.close()
    return stats[0][0]

def criteriazstat(sqlcritstng):
    focus = sqlcritstng
    competition = " not( "+focus+" )"
    magic = " AND Noshow='Yes' "
    successcounts=[0,0]
    attemptcounts=[0,0]

    successcounts[0]=grabval(focus+magic)
    attemptcounts[0]=grabval(focus)

    successcounts[1]=grabval(competition+magic)
    attemptcounts[1]=grabval(competition)

    focuspct = successcounts[0]*1.0/attemptcounts[0]
    comppct = successcounts[1]*1.0/attemptcounts[1]

    z, p = propm.proportions_ztest(successcounts, attemptcounts)
    # if p <.01:
    #     print 'SIGNIFICANT!!!!!!'
    #     print sqlcritstng
    #     print p
    #     print 'focus% ' + str(focuspct)
    #     print 'comp% ' + str(comppct)
    return (focuspct, comppct, p)

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

    ax2.set_ylabel('%% missed of total')
    fig.suptitle("Appointment Distributions by " +col, fontsize=18)
    fig.set_figwidth(12, forward=True);
    ax1.legend((r1,r2), ('Made Appointments', 'Missed Appointments'))
    plt.show()
    plt.close()
def getprevtot():
    mycur = dmexecute(dmsql.categoricalcounter('AppointmentID', 'preproc'))
    res = mycur.fetchall()
    mycur.close()
    a, b = zip(*res)
    i=0
    tupkeeper=[]
    for appid in a:
        i = i+1
        mycur = dmexecute(dmsql.prevfinds1(appid))
        res = mycur.fetchall()
        mycur.close()
        patid = res[0][0]
        tstamp = res[0][1]
        tstamp = tstamp.isoformat()
        totcur = dmexecute(dmsql.prevfinds2(patid,tstamp))
        tot = totcur.fetchall()[0][0]
        totcur.close()
        tupkeeper.append((appid, tot))
        if(i%50==0):
            print i
    i=0
    for t in tupkeeper:
        incur = dmexecute(dmsql.puttot(t[0],t[1]))
        incur.close()
        if(i%50==0):
            print i

def prepnclean():
    mycur = dmexecute(dmsql.preTabCreator)
    mycur.close()

def discrleadt():
    mycur = dmexecute(dmsql.statfinder('lead_time', 'preproc'))
    res = mycur.fetchall()
    mycur.close()
    av = res[0][0]
    st = res[0][1]
    mycur = dmexecute(dmsql.discretizer('lead_time', 'preproc', av, st))
    mycur.close()

def killwhite(mst):
    tmp = mst[::]
    for w in [' ', '\t', '\r', '\n']:
        tmp = tmp.replace(w, '')
    return tmp

def gencsv(cols='*', tab='preproc', clause="1=1"):
    cols = killwhite(cols)
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

def extractRule(line, istert=False):
    builder = ''
    if(istert):
        nshw = line.split('/')[-1].split('==>')[-1].split()[-1]
        ret=line.split('/')[-1].split('==>')[0].strip()
        ret=ret.replace(' = ', '=')
        n=0
        escapes = ['and', 'or', 'not']
        for i in ret.split():
            raw = ''
            if n > 0:
                raw = raw + ' '
            if i in escapes:
                builder= builder + raw + i
                n += 1
                continue
            sep = i.split("=")
            tok = sep[-1]
            if tok.isdigit():
                pass
            else:
                tok = "'"+tok+"'"
            raw = raw +sep[0]+"="+tok
            builder= builder+(raw)
            n += 1
    else:
        nshw=line.split('.')[1].split("==>")[-1].split('=')[1].split()[0]
        ret=line.split('.')[1].split("==>")[0].strip()
        bricks = ret.split()[0:-1]
        n=0
        for i in bricks:
            raw = ''
            if n > 0:
                raw = raw + ' and '
            sep = i.split("=")
            tok = sep[-1]
            if tok.isdigit():
                pass
            else:
                tok = "'"+tok+"'"
            raw = raw +sep[0]+"="+tok
            builder= builder+(raw)
            n += 1

    return (builder, nshw)

def procfinal(rows):
    i=0
    end=len(rows)
    while i<end:
        results = criteriazstat(rows[i][0])
        for res in results:
            rows[i].append(res)
        i+=1
    for ln in rows:
        if ln[-1] > .01:
            continue
        output = ''
        for item in ln:
            output = output + str(item) + ','
        output=output[0:-1]
        print output
    return

def procapr():
    print 'apriorirule,predicts,pct_in_rule_noshow,pct_out_rule_noshow,pvalue'
    critarr = []
    f = open('./fresh.dat', 'r')
    lines = f.readlines()
    f.close()
    for l in lines:
        tmp = extractRule(l)
        if tmp[0].count('=') > 1:
            critarr.append([tmp[0], tmp[1]])
    procfinal(critarr)

def proctert():
    print 'Tertiusrule,predicts_nshw,pct_in_rule_noshow,pct_out_rule_noshow,pvalue'
    critarr = []
    f = open('./tert.dat', 'r')
    lines = f.readlines()
    f.close()
    for l in lines:
        tmp = extractRule(l, True)
        if tmp[0].count('=') > 1:
            critarr.append([tmp[0], tmp[1]])
    procfinal(critarr)

def superIterate():
    print 'naiverule,distinct_vals,pct_in_rule_noshow,pct_out_rule_noshow,pvalue'
    errthang = dmsql.ztestcols.replace(',', '').split()
    totalchecks = 0
    total_found = 0
    critarr = []
    for col in errthang:
        datacur= dmexecute(dmsql.categoricalcounter(col, 'preproc'))
        res = datacur.fetchall()
        datacur.close()
        dat,cts = zip(*res)
        distvals = len(dat)
        if(len(dat)<3):
            tmp = [dat[0]]
            dat = tmp
        for d in dat:
            if str(d).isdigit():
                criteria = ' '+col+"="+str(d)+' '
            else:
                criteria = " "+col+"='"+str(d)+"' "
            critarr.append([criteria,distvals])
    procfinal(critarr)



def main():
    # csvclause = "Noshow='Yes'"
    # prepnclean()
    # getprevtot()
    # discrleadt()
    # uniqcounter()
    # gencsv(dmsql.simplecsvcols)
    # superIterate()
    # criteriazstat(" lead_time = 2 and not con_handycaps = 1 and not agegroup = 'middle' ")
    # print dmsql.simplecsvcols
    # eatdat()
    proctert()
    # procapr()
    # superIterate()
    db.commit()
    db.close()
main()

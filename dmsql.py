# Other string constants
def listingcreator(drops, adds, base):
    ret = base[::]
    for d in drops:
        ret = ret.replace(d+',', '')
    for a in adds:
        ret = ret +" "+a+","
    return ret

normstng = "PatientId, AppointmentID, Gender, ScheduledDay, AppointmentDay, Age, Neighbourhood, Scholarship, Hipertension, Diabetes, Alcoholism, Handcap, SMS_received, Noshow,"
ppcstng = normstng + " dayidx, lead_time," + " con_handycaps, agegroup, townsize,"
allcols = []
for s in ppcstng.split(",")[0:-1]:
    allcols.append(s.strip())

sqltypes = {}
for col in allcols:
    sqltypes[col]='varchar(255)'

replacedtypes = {
                'Gender': "ENUM('M', 'F')",
                'ScheduledDay': 'DATETIME',
                'AppointmentDay': 'DATETIME',
                'Age': 'INT',
                'Neighbourhood': 'INT',
                'Scholarship': 'INT',
                'Hipertension': 'INT',
                'Diabetes': 'INT',
                'Alcoholism': 'INT',
                'Handcap': 'INT',
                'SMS_received': 'INT',
                'Noshow': "ENUM ('No', 'Yes')",
                'dayidx': 'INT',
                'lead_time': 'INT',
                'con_handycaps': 'INT',
                'agegroup':     "ENUM('minor', 'young', 'middle', 'advanced', 'old')",
                'townsize':     "ENUM('small', 'medium', 'large')"
                }

ppsql = ppcstng
sqltypes.update(replacedtypes)
for col, ctype in sqltypes.items():
    ppsql = ppsql.replace( col+',', col+' '+ctype+',')

dropcols = ['PatientId', 'AppointmentID', 'ScheduledDay', 'AppointmentDay', 'Handcap', 'Age', 'Neighbourhood']
addcols = ['Neighbourhood', 'Handcap']
simplecsvcols = listingcreator(dropcols, [], ppcstng)
ztestcols = listingcreator([], addcols, simplecsvcols)

ztestcols = ztestcols[0:-1]
ppsql = ppsql[0:-1]
normstng = normstng[0:-1]
ppcstng = ppcstng[0:-1]
simplecsvcols = simplecsvcols[0:-1]

# Procedures
preTabCreator = [
                'DROP TABLE preproc;',
                (
                    'CREATE TABLE preproc '
                    '('
                        + ppsql +
                    ')'
                ),
                (
                    'INSERT INTO preproc ('+normstng+') '
                    'SELECT ' +normstng.replace('Neighbourhood', 'tmp.nbhnum')+' '
                    'FROM ( '
                        'SELECT appts.*, hoods.idx as nbhnum FROM appts, hoods WHERE STRCMP(appts.Neighbourhood, hoods.name)=0 '
                    ') as tmp '
                ),
                (
                    'DELETE FROM preproc WHERE age < 1'
                ),
                (
                    'UPDATE preproc '
                    'SET townsize=1 '
                    'WHERE Neighbourhood IN'
                        '(SELECT Neighbourhood from ( '
                            'SELECT Neighbourhood, count(*) as cnt from preproc group by Neighbourhood '
                        ') as tmp1 where tmp1.cnt<= 1885 ) '
                ),
                (
                    'UPDATE preproc '
                    'SET townsize=2 '
                    'WHERE Neighbourhood IN '
                        '(SELECT Neighbourhood from '
                            '(SELECT Neighbourhood, '
                                'count(*) as cnt from preproc '
                                'group by Neighbourhood '
                            ') as tmp1 where tmp1.cnt > 1885 AND tmp1.cnt <= 2773 '
                        ')'
                ),
                (
                    'UPDATE preproc '
                    'SET townsize=3 '
                    'WHERE Neighbourhood IN '
                        '(SELECT Neighbourhood from '
                            '(SELECT Neighbourhood, '
                                'count(*) as cnt from preproc '
                                'group by Neighbourhood '
                            ') as tmp1 where tmp1.cnt > 2773'
                        ')'
                ),
                (
                    'UPDATE preproc '
                    'SET con_handycaps=Handcap '
                ),
                (
                    'UPDATE preproc '
                    'SET con_handycaps=2 '
                    'where Handcap > 2'
                ),
                (
                    'UPDATE preproc '
                    'SET agegroup=1 '
                    'where age < 18'
                ),
                (
                    'UPDATE preproc '
                    'SET agegroup=2 '
                    'where age >=18 and age < 42'
                ),
                (
                    'UPDATE preproc '
                    'SET agegroup=3 '
                    'where age >=42 and age < 66'
                ),
                (
                    'UPDATE preproc '
                    'SET agegroup=4 '
                    'where age >=66 and age < 90'
                ),
                (
                    'UPDATE preproc '
                    'SET agegroup=5 '
                    'where age >=90'
                ),
                (
                    'UPDATE preproc '
                    'SET dayidx=DAYOFWEEK(AppointmentDay) '
                ),
                (
                    'UPDATE preproc '
                    'SET lead_time=DATEDIFF(AppointmentDay, ScheduledDay) '
                ),
                (
                    'DELETE FROM preproc WHERE lead_time < 1'
                )


                ]

# Templates
def csvgetter(cols, tab, clause):
    ret =   [
            (
                'SELECT '+cols+' '
                'FROM '+ tab +' '
                'WHERE '+clause+' ;'
            )
            ]
    return ret

def colnameRet(preftab):
    ret =   [
            (
                "SELECT `COLUMN_NAME` "
                "FROM `INFORMATION_SCHEMA`.`COLUMNS` "
                "WHERE `TABLE_SCHEMA`='proj3' "
                "    AND `TABLE_NAME`='"+ preftab +"';"
            )
            ]
    return ret

def statfinder(col, tab):
    ret =   [
            (
                "SELECT AVG("+ col +"), STDDEV("+ col +"), MAX("+ col +"), MIN("+ col +")"
                "FROM "+ tab +" ;"
            )
            ]
    return ret
def discretizer(col, tab, avg, std):
        ret =   [
                (
                    'UPDATE preproc '
                    'SET '+ col +'=0 '
                    'where lead_time<='+str(float(avg))+' '
                ),
                (
                    'UPDATE preproc '
                    'SET '+ col +'=1 '
                    'where lead_time>'+str(float(avg))+' '
                    'and lead_time<='+str(float(avg)+std)+' '
                ),
                (
                    'UPDATE preproc '
                    'SET '+ col +'=2 '
                    'where lead_time>'+str(float(avg)+std)+' '
                )
                ]
        return ret
def normalizer(col, tab, avg, std):
    ret = ["UPDATE "+ tab +" SET  "+ col +" = ( "+ col +" - "+ str(avg) +" )/( "+ str(std) +" );"]
    return ret

def categoricalcounter(col, tab, specific=False, nshw='No'):
    if(specific):
        truetab = " (SELECT * FROM "+tab+" WHERE Noshow='"+nshw+"')"
    else:
        truetab = tab
    hasall= " (select distinct "+ col +", 0 as fcnt from "+ tab +" ) "
    hascounts = " (select "+col+", count(*) as fcnt from "+truetab+" as tmp group by "+ col +" order by "+ col +" asc) "
    joined = " (select hasall."+col+", IFNULL(hascounts.fcnt, 0) as fcnt from "+ hascounts +" as hascounts RIGHT JOIN "+ hasall +" as hasall ON hasall."+col+"=hascounts."+col+") "
    ret =   [
                "select joined."+col+", joined.fcnt from "+ joined +" as joined order by joined."+col+" asc;"
            ]
    return ret

def numdistinct(col, tab):
    ret =   [
            "select count(*) from (select distinct "+ col +" from "+ tab +") as tmp;"
            ]
    return ret
def prevfinds1(apid):
    ret =   [
            "select PatientId, AppointmentDay from preproc where AppointmentID="+str(apid)
            ]
    return ret
def prevfinds2(patid,tstamp):
    ret =   [
            "select count(*) from (select tmp.df from (select DATEDIFF(AppointmentDay, '"+str(tstamp)+"') as df from preproc where PatientId="+str(patid)+") as tmp where tmp.df < 0)as tmp2"
            ]
    return ret
def puttot(appid,tot):
    ret =   [
            "UPDATE preproc set total_past_appointments="+str(tot)+" where AppointmentID="+str(appid)
            ]
    return ret

def criteriaSuccess(critstrng):
    ret =   [
            "select count(*) from preproc where "+critstrng+" "
            ]
    return ret

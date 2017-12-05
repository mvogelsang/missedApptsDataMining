# Other string constants
def listingcreator(drops, adds, base):
    ret = base[::]
    for d in drops:
        ret = ret.replace(d+',', '')
    for a in adds:
        ret = ret + a
    return ret

normstng = "PatientId, AppointmentID, Gender, ScheduledDay, AppointmentDay, Age, Neighbourhood, Scholarship, Hipertension, Diabetes, Alcoholism, Handcap, SMS_received, Noshow,"
ppcstng = normstng + ""
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
                }

ppsql = ppcstng
sqltypes.update(replacedtypes)
for col, ctype in sqltypes.items():
    ppsql = ppsql.replace( col+',', col+' '+ctype+',')

dropcols = ['PatientId', 'AppointmentID', 'ScheduledDay', 'AppointmentDay']
addcols = []
simplecsvcols = listingcreator(dropcols, addcols, ppcstng)

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
                )
                ]

# Queries


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

def normalizer(col, tab, avg, std):
    ret = ["UPDATE "+ tab +" SET  "+ col +" = ( "+ col +" - "+ avg +" )/( "+ std +" );"]
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

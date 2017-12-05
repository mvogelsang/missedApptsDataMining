# Other string constants
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
ppsql = ppsql[0:-1]
normstng = normstng[0:-1]
ppcstng = ppcstng[0:-1]

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

def categoricalcounter(col, tab, specific=False, nshw='Yes'):
    if(specific):
        truetab = "(SELECT * FROM "+tab+" WHERE Noshow='"+nshw+"') as tmp"
    else:
        truetab = tab
    ret =   [
            "select "+ col +", count(*) from "+ truetab +" group by "+ col +" order by "+ col +" asc;"
            ]
    return ret

def numdistinct(col, tab):
    ret =   [
            "select count(*) from (select distinct "+ col +" from "+ tab +") as tmp;"
            ]
    return ret

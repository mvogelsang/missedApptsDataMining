# Other string constants
medlist = ['metformin', 'repaglinide', 'nateglinide', 'chlorpropamide', 'glimepiride', 'acetohexamide', 'glipizide', 'glyburide', 'tolbutamide', 'pioglitazone', 'rosiglitazone', 'acarbose', 'miglitol', 'troglitazone', 'tolazamide', 'examide', 'citoglipton', 'insulin', 'glyburide_metformin', 'glipizide_metformin', 'glimepiride_pioglitazone', 'metformin_rosiglitazone', 'metformin_pioglitazone']
pprocCols = [
                'race', 'gender', 'age', 'time_in_hospital', 'num_lab_procedures', 'num_procedures',
                'num_medications', 'number_outpatient', 'number_emergency', 'number_inpatient', 'number_diagnoses',
                'max_glu_serum', 'A1Cresult', 'metformin', 'repaglinide', 'nateglinide', 'chlorpropamide', 'glimepiride',
                'acetohexamide', 'glipizide', 'glyburide', 'tolbutamide', 'pioglitazone', 'rosiglitazone', 'acarbose', 'miglitol',
                'troglitazone', 'tolazamide', 'examide', 'citoglipton', 'insulin', 'glyburide_metformin', 'glipizide_metformin', 'glimepiride_pioglitazone',
                'metformin_rosiglitazone', 'metformin_pioglitazone', 'medication_change', 'readmitted'
            ]
ppcstng = "race, gender, age, time_in_hospital, num_lab_procedures, num_procedures, num_medications, number_outpatient, number_emergency, number_inpatient, number_diagnoses, max_glu_serum, A1Cresult, metformin, repaglinide, nateglinide, chlorpropamide, glimepiride, acetohexamide, glipizide, glyburide, tolbutamide, pioglitazone, rosiglitazone, acarbose, miglitol, troglitazone, tolazamide, examide, citoglipton, insulin, glyburide_metformin, glipizide_metformin, glimepiride_pioglitazone, metformin_rosiglitazone, metformin_pioglitazone, medication_change, readmitted"

normcols = ['time_in_hospital', 'num_lab_procedures', 'num_procedures', 'num_medications', 'number_outpatient', 'number_emergency', 'number_inpatient', 'number_diagnoses']

# Procedures
preTabCreator = [
                'DROP TABLE preproc;',
                (
                    'CREATE TABLE preproc '
                    '('
                        'encounter_id varchar(255), race  varchar(255), gender  varchar(255), '
                        'age  varchar(255), '
                        'time_in_hospital  varchar(255), num_lab_procedures  varchar(255), '
                        'num_procedures  varchar(255), num_medications  varchar(255), number_outpatient  varchar(255), number_emergency  varchar(255), number_inpatient  varchar(255), '
                        'number_diagnoses  varchar(255), max_glu_serum  varchar(255), A1Cresult  varchar(255), '
                        'metformin  varchar(255), repaglinide  varchar(255), nateglinide  varchar(255), chlorpropamide  varchar(255), '
                        'glimepiride  varchar(255), acetohexamide  varchar(255), glipizide  varchar(255), glyburide  varchar(255), '
                        'tolbutamide  varchar(255), pioglitazone  varchar(255), rosiglitazone  varchar(255), acarbose  varchar(255), '
                        'miglitol  varchar(255), troglitazone  varchar(255), tolazamide  varchar(255), examide  varchar(255), '
                        'citoglipton  varchar(255), insulin  varchar(255), glyburide_metformin  varchar(255), glipizide_metformin  varchar(255), '
                        'glimepiride_pioglitazone  varchar(255), metformin_rosiglitazone  varchar(255), metformin_pioglitazone  varchar(255), '
                        'medication_change  varchar(255), '
                        'readmitted varchar(255)'
                    ')'
                ),
                (
                    'INSERT INTO preproc ('+ ppcstng +')'
                    'SELECT '+ ppcstng +' FROM (SELECT * FROM diabetic '
                    'WHERE '
                        'diabetic.discharge_disposition_id != 20 '
                    ') as tmp;'
                ),
                (
                    "UPDATE preproc SET gender = 'Female' WHERE gender <> 'Male' AND gender <> 'Female';"
                ),
                (
                    "UPDATE preproc SET age = 'YOUNG' WHERE age like '%10)' OR age like '%20)' OR age like '%30)' OR age like '%40)';"
                ),
                (
                    "UPDATE preproc SET age = 'MID' WHERE age like '%50)' OR age like '%60)' OR age like '%70)';"
                ),
                (
                    "UPDATE preproc SET age = 'OLD' WHERE age like '%80)' OR age like '%90)' OR age like '%100)';"
                ),
                (
                    "UPDATE preproc SET encounter_id='1';"
                )


                ]

# Queries
csvdat = [
        (
            "SELECT encounter_id, "+ ppcstng +" from preproc;"
        )
        ]

# Templates
def qmarkkill(col, tab):
    ret = ["UPDATE "+ tab +" SET  "+ col +" = 'QMARK' where  "+ col +" = '?';"]
    return ret;

def drugfix(drug, tab):
    ret = [ "UPDATE "+ tab +" SET  "+ drug +" = 'Yes' where  "+ drug +" NOT LIKE 'No';"]
    return ret;

def colnameRet(preftab):
    ret =   [
            (
                "SELECT `COLUMN_NAME` "
                "FROM `INFORMATION_SCHEMA`.`COLUMNS` "
                "WHERE `TABLE_SCHEMA`='proj2' "
                "    AND `TABLE_NAME`='"+ preftab +"';"
            )
            ]
    return ret

def statfinder(col, tab):
    ret =   [
            (
                "SELECT AVG("+ col +"), STDDEV("+ col +")"
                "FROM "+ tab +" ;"
            )
            ]
    return ret

def normalizer(col, tab, avg, std):
    ret = ["UPDATE "+ tab +" SET  "+ col +" = ( "+ col +" - "+ avg +" )/( "+ std +" );"]
    return ret

def uniqCtRet(col, tab):
    ret =   [
            "select "+ col +", count(*) from "+ tab +" group by "+ col +" order by count(*) asc;"
            ]
    return ret

# true preprocess
# Procedures
ppcstng2 = "encounter_id, race, gender, age, time_in_hospital, num_lab_procedures, num_procedures, num_medications, number_outpatient, number_emergency, number_inpatient, number_diagnoses, max_glu_serum, A1Cresult, metformin, repaglinide, nateglinide, chlorpropamide, glimepiride, acetohexamide, glipizide, glyburide, tolbutamide, pioglitazone, rosiglitazone, acarbose, miglitol, troglitazone, tolazamide, examide, citoglipton, insulin, glyburide_metformin, glipizide_metformin, glimepiride_pioglitazone, metformin_rosiglitazone, metformin_pioglitazone, medication_change"
inputdatcreator = [
                'DROP TABLE inputdat;',
                (
                    'CREATE TABLE inputdat '
                    '('
                        'encounter_id varchar(255), race  varchar(255), gender  varchar(255), '
                        'age  varchar(255), '
                        'time_in_hospital  varchar(255), num_lab_procedures  varchar(255), '
                        'num_procedures  varchar(255), num_medications  varchar(255), number_outpatient  varchar(255), number_emergency  varchar(255), number_inpatient  varchar(255), '
                        'number_diagnoses  varchar(255), max_glu_serum  varchar(255), A1Cresult  varchar(255), '
                        'metformin  varchar(255), repaglinide  varchar(255), nateglinide  varchar(255), chlorpropamide  varchar(255), '
                        'glimepiride  varchar(255), acetohexamide  varchar(255), glipizide  varchar(255), glyburide  varchar(255), '
                        'tolbutamide  varchar(255), pioglitazone  varchar(255), rosiglitazone  varchar(255), acarbose  varchar(255), '
                        'miglitol  varchar(255), troglitazone  varchar(255), tolazamide  varchar(255), examide  varchar(255), '
                        'citoglipton  varchar(255), insulin  varchar(255), glyburide_metformin  varchar(255), glipizide_metformin  varchar(255), '
                        'glimepiride_pioglitazone  varchar(255), metformin_rosiglitazone  varchar(255), metformin_pioglitazone  varchar(255), '
                        'medication_change  varchar(255), '
                        'readmitted varchar(255)'
                    ')'
                ),
                (
                    'INSERT INTO inputdat ('+ ppcstng2 +') '
                    'SELECT '+ ppcstng2 +' FROM (SELECT * FROM diabetic_eval '
                    'WHERE '
                        'diabetic_eval.discharge_disposition_id != 20 '
                    ') as tmp;'
                ),
                (
                    "UPDATE inputdat SET gender = 'Female' WHERE gender <> 'Male' AND gender <> 'Female';"
                ),
                (
                    "UPDATE inputdat SET age = 'YOUNG' WHERE age like '%10)' OR age like '%20)' OR age like '%30)' OR age like '%40)';"
                ),
                (
                    "UPDATE inputdat SET age = 'MID' WHERE age like '%50)' OR age like '%60)' OR age like '%70)';"
                ),
                (
                    "UPDATE inputdat SET age = 'OLD' WHERE age like '%80)' OR age like '%90)' OR age like '%100)';"
                ),
                (
                    "UPDATE inputdat SET readmitted = 'NO';"
                )

                ]

# Queries
csvdat2 = [
        (
            "SELECT encounter_id, "+ ppcstng +" from inputdat;"
        )
        ]

pprocCols2 = [
                'encounter_id', 'race', 'gender', 'age', 'time_in_hospital', 'num_lab_procedures', 'num_procedures',
                'num_medications', 'number_outpatient', 'number_emergency', 'number_inpatient', 'number_diagnoses',
                'max_glu_serum', 'A1Cresult', 'metformin', 'repaglinide', 'nateglinide', 'chlorpropamide', 'glimepiride',
                'acetohexamide', 'glipizide', 'glyburide', 'tolbutamide', 'pioglitazone', 'rosiglitazone', 'acarbose', 'miglitol',
                'troglitazone', 'tolazamide', 'examide', 'citoglipton', 'insulin', 'glyburide_metformin', 'glipizide_metformin', 'glimepiride_pioglitazone',
                'metformin_rosiglitazone', 'metformin_pioglitazone', 'medication_change', 'readmitted'
            ]

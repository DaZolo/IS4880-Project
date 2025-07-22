import pandas as pd
import pymysql
from werkzeug.security import generate_password_hash

DB_HOST = 'localhost'
DB_USER = 'alumni_user'
DB_PASSWORD = 'StrongPassword!'
DB_NAME = 'alumni_db'

EXCEL_FILE = 'data.xlsx'

conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
cur = conn.cursor()

def sql_val(val):
    if pd.isna(val):
        return None
    if hasattr(val, 'to_pydatetime'):
        val = val.to_pydatetime()
    if hasattr(val, 'date') and not isinstance(val, str):
        try:
            return val.strftime('%Y-%m-%d')
        except:
            return val
    return val

print("Reading Excel data...")

alumni_df = pd.read_excel(EXCEL_FILE, sheet_name='alumni')
address_df = pd.read_excel(EXCEL_FILE, sheet_name='address')
employment_df = pd.read_excel(EXCEL_FILE, sheet_name='employment')
skillset_df = pd.read_excel(EXCEL_FILE, sheet_name='skillset')
degree_df = pd.read_excel(EXCEL_FILE, sheet_name='degree')
donations_df = pd.read_excel(EXCEL_FILE, sheet_name='donations')
user_df = pd.read_excel(EXCEL_FILE, sheet_name='user')

print("Inserting alumni...")
for _, row in alumni_df.iterrows():
    vals = (
        sql_val(row['alumniID']), sql_val(row['fName']), sql_val(row['lName']),
        sql_val(row['phone']), sql_val(row['email']), sql_val(row['DOB']),
        sql_val(row['gender']), sql_val(row['ethnicity']), sql_val(row['website']),
        sql_val(row['linkedIn_link']), sql_val(row.get('twitter_link')), sql_val(row.get('facebook_link')),
        sql_val(row.get('instagram_link')), sql_val(row['guestSpeakerYN']), sql_val(row['newsLetterYN']),
        sql_val(row['imageThumb']), sql_val(row['imageNormal']), sql_val(row['description']),
        sql_val(row['deceasedYN']), sql_val(row['deceasedDT']), sql_val(row['deceasedNotes'])
    )
    cur.execute(
        """
        INSERT IGNORE INTO alumni (
            alumniID, fName, lName, phone, email, DOB, gender,
            ethnicity, website, linkedIn_link, twitter_link,
            facebook_link, instagram_link, guestSpeakerYN,
            newsLetterYN, imageThumb, imageNormal,
            description, deceasedYN, deceasedDT, deceasedNotes
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, vals
    )
conn.commit()

print("Inserting addresses...")
for _, row in address_df.iterrows():
    vals = (
        sql_val(row['addressID']), sql_val(row['alumniID']), sql_val(row['address']),
        sql_val(row['city']), sql_val(row['state']), sql_val(row['zipCode']),
        sql_val(row['activeYN']), sql_val(row['primaryYN'])
    )
    cur.execute(
        "INSERT IGNORE INTO address (addressID, alumniID, address, city, state, zipCode, activeYN, primaryYN) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        vals
    )
conn.commit()

print("Inserting employment records...")
for _, row in employment_df.iterrows():
    vals = (
        sql_val(row['EID']), sql_val(row['alumniID (FK)']), sql_val(row['company']),
        sql_val(row['city']), sql_val(row['state']), sql_val(row['zip']),
        sql_val(row['jobTitle']), sql_val(row['startDate']),
        sql_val(row['endDate']), sql_val(row['currentYN']), sql_val(row['notes'])
    )
    cur.execute(
        "INSERT IGNORE INTO employment (EID, alumniID, company, city, state, zip, jobTitle, startDate, endDate, currentYN, notes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        vals
    )
conn.commit()

print("Inserting skillsets...")
for _, row in skillset_df.iterrows():
    vals = (
        sql_val(row['SID']), sql_val(row['alumniID']), sql_val(row['skill']),
        sql_val(row['proficiency']), sql_val(row['description'])
    )
    cur.execute(
        "INSERT IGNORE INTO skillset (SID, alumniID, skill, proficiency, description) VALUES (%s, %s, %s, %s, %s)",
        vals
    )
conn.commit()

print("Inserting degrees...")
for _, row in degree_df.iterrows():
    vals = (
        sql_val(row['degreeID']), sql_val(row['alumniID']), sql_val(row['major']),
        sql_val(row['minor']), sql_val(row['graduationDT']), sql_val(row['university']),
        sql_val(row['city']), sql_val(row['state'])
    )
    cur.execute(
        "INSERT IGNORE INTO degree (degreeID, alumniID, major, minor, graduationDT, university, city, state) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        vals
    )
conn.commit()

print("Inserting donations...")
for _, row in donations_df.iterrows():
    vals = (
        sql_val(row['donationID']), sql_val(row['alumniID']), sql_val(row['donationAmt']),
        sql_val(row['donationDT']), sql_val(row['reason']), sql_val(row['description'])
    )
    cur.execute(
        "INSERT IGNORE INTO donation (donationID, alumniID, donationAmt, donationDT, reason, description) VALUES (%s, %s, %s, %s, %s, %s)",
        vals
    )
conn.commit()

print("Inserting users...")
for _, row in user_df.iterrows():
    raw_password = str(row['password'])
    hashed_password = generate_password_hash(raw_password)
    vals = (
        sql_val(row['UID']), hashed_password, sql_val(row['fName']),
        sql_val(row['lName']), sql_val(row['jobDescription']),
        sql_val(row['viewPriveledgeYN']), sql_val(row['insertPriveledgeYN']),
        sql_val(row['updatePriveledgeYN']), sql_val(row['deletePriveledgeYN'])
    )
    cur.execute(
        "INSERT IGNORE INTO `user` (UID, password, fName, lName, jobDescription, viewPriveledgeYN, insertPriveledgeYN, updatePriveledgeYN, deletePriveledgeYN) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        vals
    )
conn.commit()

if 'engagement' in pd.ExcelFile(EXCEL_FILE).sheet_names:
    engagement_df = pd.read_excel(EXCEL_FILE, sheet_name='engagement')
    print("Inserting engagement records...")
    for _, row in engagement_df.iterrows():
        vals = (
            sql_val(row['newsletterID']), sql_val(row['date']), sql_val(row['recipients']), sql_val(row['clicks'])
        )
        cur.execute(
            "INSERT IGNORE INTO engagement (newsletterID, date, recipients, clicks) VALUES (%s, %s, %s, %s)",
            vals
        )
    conn.commit()

print("Data seeding completed.")
cur.close()
conn.close()
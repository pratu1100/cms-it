import mysql.connector
from faker import Faker
from faker.providers import company, job, date_time
from datetime import datetime
import os

import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print(BASE_DIR)

fake = Faker()

def insertToMySQL():
  mydb = mysql.connector.connect(
    host="ls-7aad48b2eded0671a0c5ce6fcde3e04bbabc6957.cu7csf8tsbsu.ap-south-1.rds.amazonaws.com",
    user="dbmasteruser",
    passwd="balbasor",
    database="cmsdb"
  )

  mycursor = mydb.cursor()

  sql = "INSERT INTO guest_reservation (email, contact_person, institute, department, purpose, end_date, start_time, end_time, start_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

  val = []
  count = 0
  for _ in range(500):
    val.append((f"test{count}@yopmail.com", fake.name(), fake.company(), fake.job(), fake.text(), fake.date(pattern="%Y-%m-%d", end_datetime="+50y"), fake.date_time_between(start_date="-30y", end_date="now", tzinfo=None).strftime('%Y-%m-%d %H:%M:%S'), fake.date_time_between(start_date="-30y", end_date="now", tzinfo=None).strftime('%Y-%m-%d %H:%M:%S'), fake.date(pattern="%Y-%m-%d", end_datetime=None)))
    count += 1 

  # print(val)
  mycursor.executemany(sql, val)
  mydb.commit()
  print(mycursor.rowcount, "was inserted.")

def insertToSQLite():
  conn = sqlite3.connect(os.path.join(BASE_DIR, 'db.sqlite3'))

  # print(conn)
  c = conn.cursor()


  sql = "INSERT INTO guest_reservation (email, contact_person, institute, department, purpose, end_date, start_time, end_time, room_id, start_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

  val = []
  count = 0

  for _ in range(500):
    val.append((f"test{count}@yopmail.com", fake.name(), fake.company(), fake.job(), fake.text(), fake.date(pattern="%Y-%m-%d", end_datetime="+1y"), fake.date_time_between(start_date="-1y", end_date="now", tzinfo=None).strftime('%H:%M:%S'), fake.date_time_between(start_date="-1y", end_date="now", tzinfo=None).strftime('%H:%M:%S'), 18, fake.date(pattern="%Y-%m-%d", end_datetime="now")))
    count += 1 
  
    # os.path.join(BASE_DIR, 'templates')
  c.executemany(sql, val)
  conn.commit()
  print("Done")
insertToSQLite()
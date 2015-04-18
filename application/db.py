#! /usr/bin/env python

import sqlite3
import sys
import os

dbname = 'chocan.db'

class DB:
  def __init__(self):
    self.db = None
    self.cursor = None

  def load_db(self):
    if(os.path.isfile(dbname)):
      #dont recreate anything
      #connect to db
      self.db = sqlite3.connect(dbname)
      self.cursor = self.db.cursor()
    else:
      #no db file, need to make one
      self.db = sqlite3.connect(dbname)
      self.cursor = self.db.cursor()
      self.cursor.execute('''CREATE TABLE users(id INTEGER PRIMARY KEY, username TEXT, password TEXT, access INTEGER)''')
      self.cursor.execute('''CREATE TABLE members(mid INTEGER PRIMARY KEY, name TEXT, address TEXT, city TEXT, state TEXT, zipcode INTEGER, suspended INTEGER)''')
      #SQLite does not have a separate Boolean storage class. Instead, Boolean values are stored as integers 0 (false) and 1 (true).
      self.cursor.execute('''CREATE TABLE services(id INTEGER PRIMARY KEY, date TEXT, recieved_time TEXT, mid INTEGER, service_code INTEGER)''')
      self.cursor.execute('''CREATE TABLE providers(id INTEGER PRIMARY KEY, name TEXT, address TEXT, city TEXT, state TEXT, zipcode INTEGER)''')
      self.cursor.execute('''CREATE TABLE provider_directory(id INTEGER PRIMARY KEY, service TEXT, fee REAL)''')
      print "Initialized New Database"
      self.db.commit()

  def close_db(self):
    self.db.close()

  #SERVICES AND THINGS
  #sqlite> INSERT INTO services(id,date,recieved_time,member_name,mid,service_code,fee) VALUES(null,"now",strftime('%m-%d-%Y', 'now'),"Ben",1,123123123,9999999.99)
  #get fees brah sqlite> select fee from services natural join members;
  def add_service(self, mid,service_code):
    #service code is id in provier_directory table
    self.cursor.execute('''INSERT INTO services(id,date,recieved_time,mid,service_code)
    VALUES(null,strftime('%m-%d-%Y','now'),strftime('%m-%d-%Y','now'),?,?)''',(mid,service_code))
    self.db.commit()

  def get_service_costs(self, mid): #AKA get how much that member owes
  #sqlite> select fee from provider_directory where id in (select service_code from services natural join members where mid = 21);
    self.cursor.execute('''SELECT fee FROM provider_directory WHERE id IN (SELECT service_code FROM services NATURAL JOIN members WHERE mid = ?)''',(mid,))
    total = 0.0
    #print self.cursor.fetchone()
    for fee in self.cursor:
      total += fee[0]
    return total
  

#PROVIDER DIRECTORY
  def get_providerdir(self):
    #nicely return stuffs
    self.cursor.execute('''SELECT id,service,fee FROM provider_directory''')
    returned = ""
    for id,service,fee in self.cursor:
      returned += "Service Code #: " + str(id) + " - Service: " + service + " - Fee: " + str(fee) +"\n"
    return returned

  def add_providerdir_item(self,service,fee):
    self.cursor.execute('''INSERT INTO provider_directory(id,service,fee) VALUES(null,?,?)''',(service,fee))
    self.db.commit()
    pass

  def remove_providerdir_item(self,id):
    self.cursor.execute('''DELETE FROM provider_directory WHERE id = ?''',(id,))
    self.db.commit()
    return

#MEMBERS AND THINGS

  def add_member(self,name,address,city,state,zipcode):
    #get next MID since they are neW
    #members have their own table
    self.cursor.execute('''INSERT INTO members(mid, name, address, city, state, zipcode, suspended) VALUES(null,?,?,?,?,?,0)''',(name,address,city,state,zipcode))
    self.cursor.execute('''SELECT max(mid) FROM members''')
    mid = self.cursor.fetchone()[0]
    self.db.commit()
    return mid

  def suspend_member(self, mid):
    mid = int(mid)
    self.cursor.execute('''UPDATE members SET suspended=1 WHERE mid=?''',(mid,))
    self.db.commit()
    return

  def get_member(self,mid):
    self.cursor.execute('''SELECT * from members WHERE mid=?''',(mid,))
    return self.cursor.fetchone()

##USERS AND THINGS
  
  def add_user(self,username,password,access):
    #1 - provider
    #2 - manager
    self.cursor.execute('''INSERT INTO users(id,username,password,access) VALUES(null,?,?,?)''',(username,password,access))
    self.db.commit()

  def delete_user(self,username):
    self.cursor.execute('''DELETE FROM users WHERE username = ?''',(username,))
    self.db.commit()
    return

  def auth(self,username, password):
    #self.cursor.execute('''''')
    #return 0 if not match
    #return 1 if provider
    #return 2 if manager
    self.cursor.execute('''SELECT password FROM users WHERE username = ?''',(username,))
    try:
      dbpass = self.cursor.fetchone()[0]
    except:
      return 0

    if(not dbpass or (dbpass != password)): #no password or passwords dont match
      return 0

    elif(dbpass == password):
      #successfullt authed, get access level
      self.cursor.execute('''SELECT access FROM users WHERE username = ?''',(username,))
      return self.cursor.fetchone()[0] #return access level

###PROVIDERS
#self.cursor.execute('''CREATE TABLE providers(id INTEGER PRIMARY KEY, name TEXT)''')

  def add_provider(self,name,address,city,state,zipcode):
    #get next MID since they are neW
    #members have their own table
    self.cursor.execute('''INSERT INTO providers(id, name, address, city, state, zipcode) 
        VALUES(null,?,?,?,?,?)''',(name,address,city,state,zipcode))
    self.cursor.execute('''SELECT max(id) FROM providers''')
    pid = self.cursor.fetchone()[0]
    self.db.commit()
    return pid

  def delete_provider(self,id):
    self.cursor.execute('''DELETE FROM providers WHERE id = ?''',(id,))
    self.db.commit()
    return

  def get_providers(self):
    self.cursor.execute('''SELECT id,name from providers''')
    returned = ""
    for id,name in self.cursor:
      returned += "Provider ID#: " + str(id) + " Provider Name: " + str(name) + "\n"
    return returned

  def lookup_provider(self,id):
    self.cursor.execute('''SELECT * from providers where id=?''',(id,))
    return self.cursor.fetchone()

###
  def test_populate(self):
    #self.cursor.execute()
    self.add_member("Ben","1234 Your Street","Portland","OR",12334)
    self.add_member("Chris","12345 Your Street","Portland","OR",12312)
    self.add_member("John","12345 Your Street","Portland","OR",14241)
    self.add_member("Wilbur","12345 Your Street","Portland","OR",15115)
    self.add_member("Sally","12345 Your Street","Portland","OR",15515)
    susan = self.add_member("Susan","12346 Your Street","Portland","OR",99999)
    self.suspend_member(susan)
    self.add_providerdir_item("Patient Mental Care",125.00)
    self.add_providerdir_item("Chocolate leaning package",250.00)
    self.add_providerdir_item("Cocoa Theraphy", 900.50)
    #returned = self.get_providerdir()
    self.add_service(susan,2)
    self.add_service(susan,3)
    self.add_provider("BEN's shop","12314 fifth street","Portland","OR","91234")
    self.add_provider("K's shop","12314 fifth street","Portland","OR","91234")
    #print(self.get_providers())
    #add users
    self.add_user("manager","manager",2)
    self.add_user("provider","provider",1)
    #print("success: %s" % self.auth("ben","ben"))
    #print(self.get_member(1))

#END DB CLASS

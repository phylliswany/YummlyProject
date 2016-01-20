import MySQLdb

class MysqlWrapper:
	def __init__(self, login):
		self.login = login
		self.db = None

	def connect(self):
		db = MySQLdb.connect(
			host = self.login.get('host', ""),
			user = self.login.get('user', ""),
			passwd = self.login.get('pass', ""),
			db = self.login.get('database', ""))
		return db

	def read_query(self, sql, var):
		self.db = self.connect()
		cursor = self.db.cursor()	
		cursor.execute("USE yummly_database")
		# print sql%var
		cursor.execute(sql, var)
		results = cursor.fetchall()
		cursor.close()
		self.db.commit()
		self.db.close()
		return results

	def write_query(self, sql, var):
		self.db = self.connect()
		cursor = self.db.cursor()
		cursor.execute("USE yummly_database")
		cursor.execute(sql, var)
		cursor.close()
		self.db.commit()
		self.db.close()

	
			
		

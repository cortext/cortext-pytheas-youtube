from flask_pymongo import PyMongo

# mongo = PyMongo()

class Database:

	# def __init__(self, app):
	# 	self.app = app

	def init_mongo(self, app):
		return PyMongo(app)
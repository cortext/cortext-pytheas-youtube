import logging
from flask_pymongo import PyMongo

# mongo = PyMongo()
logger = logging.getLogger(__name__)
print('test in db.py')
logger.debug('test ?')

class Database:

	# def __init__(self, app):
	# 	self.app = app

	def init_mongo(self, app):

		return PyMongo(app)
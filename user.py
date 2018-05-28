import json
from pprint import pprint
from uuid import uuid4
##########################################################################
# User
##########################################################################
class User():
    cortext_fields = ['id','username','access_token','email']

    def __init__(self, mongo_curs, id=None):
        self.db = mongo_curs.db
        if id:
            self.id_pytheas = id
            self.get()

    def get(self):
        try:
            current_user = self.db.users.find_one_or_404({ 'id_pytheas': self.id_pytheas})
            self.username = current_user['username']
            print('get user : ', current_user['username'])
        except BaseException as e:
            print('user not found : ', e)
        return

    def view(self):
        return str(self.username + ' : ' + self.id_pytheas)

    def create(self):
        self.id_pytheas = str(uuid4().hex)
        self.db.users.insert_one(
            {
                'id_pytheas' : self.id_pytheas,
                'username' : self.username,
                'id_cortext' : self.id_cortext,
                #[...] for each corxtext fields
            }
        )
        return

    def create_or_replace_user_cortext(self, dataUser):
        dataUser = dataUser.json()
        self.username = dataUser['username']
        self.id_cortext = dataUser['id']
        
        try:
            current_user = self.db.users.find_one_or_404({ 'id_cortext': self.id_cortext})
            print('get cortext user : ', current_user['username'])
            if (current_user):
                # self.udpate(dataUser)
                self.db.users.update_one(
                  { 'id_cortext' : self.id_cortext },
                  { '$set': { 'username': dataUser['username']} }
                )
        except BaseException as e:
            print('user not found or error : ', e)
            self.create()
            return 'user not found or error : '+ str(e)
        return

    def update(self, dataUser):
        user_update = self.db.users.update_one(
          { 'id_pytheas' : self.id_pytheas },
          { '$set': { 'username': dataUser['username']} }
        )
        return user_update

    def delete():
        return
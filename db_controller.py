from peewee import *
import datetime
import peewee

user = 'root'
password = 'root'
db_name = 'main'

dbhandle = SqliteDatabase("main.db")


class BaseModel(Model):
    class Meta:
        database = dbhandle


class Users(BaseModel):
    id = PrimaryKeyField(null=False)
    login = CharField(max_length=100)
    password = CharField(max_length=20)
    name = CharField(max_length=50)
    status = CharField(max_length=20, default="offline")

    created_at = DateTimeField(default=datetime.datetime.now())

    class Meta:
        db_table = "users"
        order_by = ('created_at',)

    @staticmethod
    def reg(reg_data):
        if len(reg_data) != 4:
            return False
        try:
            user = Users.select().where(Users.login == reg_data[1]).get()
            return False
        except DoesNotExist as de:
            new_user = Users(
                login=reg_data[1],
                password=reg_data[2],
                name=reg_data[3]
            )
            new_user.save()
            return new_user

    @staticmethod
    def auth(auth_data):
        if len(auth_data) != 3:
            return False
        try:
            user = Users.select().where(Users.login == auth_data[1]).get()
            if user.password == auth_data[2]:
                return user
            else:
                return False
        except DoesNotExist as de:
            return False





class Message(BaseModel):
    id = PrimaryKeyField(null=False)
    sender = ForeignKeyField(Users, to_field='id', on_delete='cascade',
                               on_update='cascade')
    recipient = ForeignKeyField(Users, to_field='id', on_delete='cascade',
                                on_update='cascade')

    sending_time = DateTimeField(default=datetime.datetime.now())
    text = CharField(max_length=300)
    message_type = CharField(max_length=20)

if __name__ == '__main__':
    try:
        dbhandle.connect()
        Users.create_table()
    except peewee.InternalError as px:
        print(str(px))
    try:
        Message.create_table()
    except peewee.InternalError as px:
        print(str(px))

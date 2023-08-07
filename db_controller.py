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
    password_hash = CharField(max_length=20)
    name = CharField(max_length=50)
    status = CharField(max_length=20, default="offline")

    created_at = DateTimeField(default=datetime.datetime.now())

    class Meta:
        db_table = "users"
        order_by = ('created_at',)


class Message(BaseModel):
    id = PrimaryKeyField(null=False)
    sender = ForeignKeyField(Users, to_field='id', on_delete='cascade',
                               on_update='cascade')
    recipient = ForeignKeyField(Users, to_field='id', on_delete='cascade',
                                on_update='cascade')

    sending_time = DateTimeField(default=datetime.datetime.now())
    text = CharField(max_length=300)
    message_type = CharField(max_length=20)


class Views(BaseModel):
    id = PrimaryKeyField(null=False)
    message = ForeignKeyField(Message, to_field='id', on_delete='cascade',
                                on_update='cascade')
    user = ForeignKeyField(Users, to_field='id', on_delete='cascade',
                             on_update='cascade')


def reg(login, password_hash, name):
    try:
        user_object = Users.select().where(Users.login == login).get()
        return "login_busy"
    except DoesNotExist:
        new_user = Users(
            login=login,
            password_hash=password_hash,
            name=name
        )
        new_user.save()
        return new_user


def auth(login, password_hash):
    try:
        user_object = Users.select().where(Users.login == login).get()
        if user_object.password_hash == password_hash:
            return user_object
        else:
            return "invalid_authorization_data"
    except DoesNotExist:
        return "invalid_authorization_data"


def give_received_message_for_everyone(user):
    messages = Message.select().where(Message.message_type == "everyone")
    views = Views.select().where(Views.user == user)
    views_message = [view.message for view in views]
    messages_array = [message for message in messages]
    new_message = []
    for message in messages_array:
        if message not in views_message:
            new_message.append(message)
    for message in new_message:
        viewed_message = Views.create(message=message, user=user)
        viewed_message.save()
    if len(messages) != len(new_message):
        return new_message
    else:
        return new_message[-20:]


def give_received_message_ptp(user, sender):
    sender_object = Users.select().where(Users.login == sender)
    messages = Message.select().where(Message.message_type == "ptp", Message.sender == sender_object,
                                      Message.recipient == user)
    views = Views.select().where(Views.user == user)
    views_message = [view.message for view in views]
    messages_array = [message for message in messages]
    new_message = []
    for message in messages_array:
        if message not in views_message:
            new_message.append(message)
    for message in new_message:
        viewed_message = Views.create(message=message, user=user)
        viewed_message.save()
    return new_message


def give_all_message_everyone(user):
    messages = Message.select().where(Message.message_type == "everyone")
    return messages[-20:]


def give_all_message_ptp(user, sender):
    sender_object = Users.select().where(Users.login == sender)
    messages = Message.select().where(Message.message_type == "ptp", Message.sender == sender_object,
                                      Message.recipient == user)
    return messages


def give_new_message_everyone(user, last_call_time):
    messages = Message.select().where(Message.message_type == "everyone", Message.sending_time > last_call_time)
    return messages


def give_new_message_ptp(user, sender, last_call_time):
    sender_object = Users.select().where(Users.login == sender)
    messages = Message.select().where(Message.message_type == "ptp", Message.sender == sender_object,
                                      Message.recipient == user, Message.sending_time > last_call_time)
    return messages


def send_message(sender, message_type, text, recipient=None):
    if recipient is None:
        recipient = Users.select().where(Users.login == "admin").get()
    else:
        recipient = Users.select().where(Users.login == recipient).get()
    message = Message.create(sender=sender, message_type=message_type, text=' '.join(text), recipient=recipient)
    message.save()
    return message


if __name__ == '__main__':
    try:
        dbhandle.connect()
        Users.create_table()
        Message.create_table()
        Views.create_table()
    except peewee.InternalError as px:
        print(str(px))
    try:
        Message.create_table()
    except peewee.InternalError as px:
        print(str(px))

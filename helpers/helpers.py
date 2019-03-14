
import flask_login

from datetime import datetime
import pickle
import glob
import os


def createFlaskUser(nickname):
    '''Instantiate USER class required by flask_login.'''
    class User(flask_login.UserMixin):
        pass

    user = User()
    user.id = nickname
    return user


def saveUser(user, USERS):
    '''Save 'user' in USERS or just save USERS in file.'''
    if user:
        USERS[user] = []

    with open('storage/users.txt', 'wb') as ifile:
        pickle.dump(USERS, ifile)


def removeUser(user, USERS):
    '''Remove single user from USERS.'''
    USERS.pop(user)
    saveUser('', USERS)


def addOrRemoveRooms(add, username, room, USERS):
    '''Add or remove room from list of open rooms.'''
    if add:
        USERS[username].append(room)
    else:
        USERS[username].remove(room)

    saveUser('', USERS)


def saveChannel(channel, creator, description, CHANNELS):
    '''
    CHANNELS fields
    ---------------
    creator: the username of the creator.
    description: small description of the channel.
    list: list of 100 most recent messages.
    '''
    CHANNELS[channel] = [creator, description, []]
    with open('storage/channels.txt', 'wb') as ifile:
        pickle.dump(CHANNELS, ifile)


def saveMessage(msg, user, channel, CHANNELS):
    '''Saves a string including the user, timestamp, and message
    to corresponding channel list of messages (message history).
    If message list size is greater than 100 remove the first
    message from list.
    '''
    msgList = CHANNELS[channel][2]

    ts = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    msg_str = (user + ' (' + ts + '): ' + msg) if user else msg
    msgList.append(msg_str)

    if len(msgList) > 100:
        msgList.pop(0)

    CHANNELS[channel][2] = msgList

    with open('storage/channels.txt', 'wb') as ifile:
        pickle.dump(CHANNELS, ifile)

    return msg_str


def loadChannels():

    pfile = 'storage/channels.txt'
    if os.path.isfile(pfile):
        with open(pfile, 'rb') as ofile:
            return pickle.load(ofile)

    return dict()


def loadUsers():

    pfile = 'storage/users.txt'
    if os.path.isfile(pfile):
        with open(pfile, 'rb') as ofile:
            return pickle.load(ofile)

    return dict()


def resetChatData(path='./storage/*'):
    '''Delete files in server: users, data, and messages.
    It resets the server state.
    '''
    files = glob.glob(path)
    for f in files:
        os.remove(f)


import os
import helpers.helpers as helpers

from flask import Flask, request, render_template, redirect, url_for
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import flask_login


app = Flask(__name__)
#os.getenv("SECRET_KEY")
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)

# login manager
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

# GLOBALS
# call function to reset server state
helpers.resetChatData()
USERS = helpers.loadUsers()
CHANNELS = helpers.loadChannels()

# Flask-login loader function
@login_manager.user_loader
def user_loader(nickname):
    return helpers.createFlaskUser(nickname)


######################
#### FLASK ROUTES ####
######################

@app.route("/")
def init():
    return redirect(url_for('index'))


@app.route('/index', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':

        user = request.form['nickname']
        if user in USERS.keys():
            msg = 'Nickname already exists. Try another one.'
            return render_template("index.html", welcome='no', name=msg)

        else:
            # cookie is created for 1 year by default
            flask_login.login_user(helpers.createFlaskUser(user), remember=True)
            helpers.saveUser(user, USERS)
            return redirect(url_for('chats'))

    # GET Request
    if flask_login.current_user.is_authenticated:

        user = flask_login.current_user.id
        if user not in USERS.keys():
            # Logout user if server state has been reset
            flask_login.logout_user()
            return redirect(url_for('index'))

        if len(USERS[user]):
            # redirects user to last chatroom if he has joined one before
            room = USERS[user][-1]
            messages = CHANNELS[room][2]
            return redirect(url_for('room', user=user,
                                            chatroom=room,
                                            messages=messages))

        # redirect users to general menu
        return render_template("index.html", welcome='yes', name=user)

    else:
        return render_template("index.html", welcome='no', name='')


@app.route("/chats", methods=['GET', 'POST'])
@flask_login.login_required
def chats():

    user = flask_login.current_user.id

    if request.method == 'POST':

        roomname = request.form['room-name']
        description = request.form['description']

        if roomname in CHANNELS.keys():
            return render_template("chats.html", channels=CHANNELS, exists='y1')

        elif roomname == None or len(roomname) == 0:
            return render_template("chats.html", channels=CHANNELS, exists='y2')

        else:
            helpers.saveChannel(roomname, user, description, CHANNELS)
            return redirect(url_for('room', user=user,
                                            chatroom=roomname,
                                            messages=[]))

    # GET Request
    return render_template("chats.html", channels=CHANNELS, exists='n')


@app.route('/room/<string:chatroom>')
@flask_login.login_required
def room(chatroom):

    user = flask_login.current_user.id
    messages = CHANNELS[chatroom][2]
    return render_template("room.html", user=user,
                                        room=chatroom,
                                        messages=messages)


@app.route('/logout')
@flask_login.login_required
def logout():

    helpers.removeUser(flask_login.current_user.id, USERS)
    flask_login.logout_user()
    return redirect(url_for('index'))


############################
#### SOCKETIO functions ####
############################

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    alert = f'{username} has entered {room}!'
    join_room(room)

    if room not in USERS[username]:

        helpers.addOrRemoveRooms(True, username, room, USERS)
        msg_new = helpers.saveMessage(alert, '', room, CHANNELS)
        print(username + ' joined!')
        emit('receiveMessage', msg_new, room=room, broadcast=True)

    else:
        print(username + ' connected again.')


@socketio.on('message')
def handleMessage(data):
    msg = data['msg']
    room = data['room']
    user = flask_login.current_user.id

    print('Message sent: ' + msg)
    msg_new = helpers.saveMessage(msg, user, room, CHANNELS)
    emit('receiveMessage', msg_new, room=room, broadcast=True)


@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    alert = f'{username} has left the {room}!'

    helpers.addOrRemoveRooms(False, username, room, USERS)
    msg_new = helpers.saveMessage(alert, '', room, CHANNELS)
    emit('receiveMessage', msg_new, room=room, broadcast=True)

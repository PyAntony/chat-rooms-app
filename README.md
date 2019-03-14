# Project 2 – Flask-SocketIO-JavaScript (Chat application)

Chat application where users are free to create new channels/rooms.

## Usage

    - Clone repository & navigate to repository directory.
    - Run "pip3 install -r requirements.txt"
    - Run "export FLASK_APP=application.py"
    - Run "flask run"

### Requirements and Description

**- Display name:** 

accomplished using Flask-Login. Once the user logs in (creates a new nickname) a cookie is created and the user is remembered until logged out. User can be logged out if he changes his nickname or the cookie expires (1 year by default; time can be changed). A logged in user is said to be “authenticated” and can navigate protected URLs. In this case there is no password required, only the creation of a non-existent nickname. Users are stored in a Python dictionary named USERS; it’s keys are the users and its values are lists where the name of the rooms visited are stored.

**-  Channel creation and list:** 

channels (rooms) are displayed and created through GET and POST requests to the same endpoint ‘/chats’. Users can’t use already existent channel names. Channels information are stored in a Python dictionary called CHANNELS; its keys are the room names and its values are lists containing the creator name, the description of the room, and the list of messages.

**- Message view:**

up to 100 messages are displayed. Messages are stored in CHANNELS together with the user and the timestamp using the following function:
```python
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
```

**- Sending messages:**

messages are received and displayed without refreshing the web page. Alerts are also displayed when users enter or leave the room. This is accomplished mainly using the classical Flask-SocketIO-JavaScript scheme but also through the storage of messages and room visits. A user joins the room when entering, but doesn’t leave the room until he actually clicks on a button to either go back to the list of channels or change the nickname; this is when the room name is removed from his/her list of visits. The following example shows the interaction a user “antony” (on chrome) on the left and “Fred” (on chromium) on the right. The next image shows Fred clicking the “Change Nickname” button and leaving the room.

<br /><br />
<kbd>![interaction](https://github.com/PyAntony/project2-PyAntony/blob/master/images/interaction.png)</kbd>
<br /><br />
<kbd>![left](https://github.com/PyAntony/project2-PyAntony/blob/master/images/left.png)</kbd>
<br /><br />

Messages are lively displayed by first showing the history of messages (in ‘room.html’):
```html
<ul id="messagesList" style="list-style-type:none; padding-left: 0">
      {% for msg in messages %}
        <li>{{ msg }}</li>
      {% endfor %}
</ul>
```

And then appending new ‘li’ tags once a message is received from the socket:
```javascript
socket.on('receiveMessage', msg => {
          var node = document.createElement("li");
          node.innerHTML = msg;
          document.querySelector('#messagesList').appendChild(node);
});
```

**- Remembering the channel:**

Logged in users are easily redirected to his/her last visited room (if he hasn’t left) using the list of visits in USERS. This is accomplished inside the index function (‘/index’ route) from flask under the GET request:

```Python
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
```

**- Personal touch:**

database is persistent; the state of the database (users, channels, and messages) is stored in the ‘storage’ directory. To accomplish this the USERS and CHANNELS dictionaries are stored in pickle files after every modification. When the server is restarted the contents of this files are read. There is also a function to reset the state. These functions are called at the beginning of ‘application.py’:

```python
# GLOBALS
# call function to reset server state
helpers.resetChatData()
USERS = helpers.loadUsers()
CHANNELS = helpers.loadChannels()
```


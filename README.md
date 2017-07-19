## Chatery

##### Simple Chat Application usable in Mobile & Desktop Browsers.

### Usage:

Simply fill in your username and you can start chatting. The user is allowed to upload an image to be displayed in the chatroom.

Twitter support is available where the user can login using twitter.
The user can tweet and retweet directly from the chatroom if logged in using Twitter.

**Send Private Message to Someone**

@Username: Message (or just click on display picture of the user)

**Twitter Integration**

Twitter related features would only work if the user is logged in using twitter.

**Tweet**

tweet:twitter message (or click on twitter icon)

**ReTweet**

Click on RT icon.


### Implementation Details

Implemented Using:-

1. CherryPy -> WebSockets
2. Rivet.js -> Frontend data binding and integration.


Setting up dev instance:-

1. sudo apt-get install python3-pip
2. sudo pip3 install virtualenv
3. virtualenv chatery
4. Navigate to catery->bin
5. source activate
6. Navigate to chatery (application directory)
7. pip install -r requirements.txt
8. python app.py


This should get an instance running on your dev instance on 127.0.0.1:9000

Following flags are available
- [--host HOST]
- [-p PORT]
- [--ssl-port SSL_PORT]
- [--ssl]
- [--cert CERT]
- [--key KEY]
- [--chain CHAIN]


#### Mini Docs
- dbutils -> Package that manages all the database related operations & queries
- app.py -> File that manages WebSockets & the core of the chat application
- assets -> Contains images,js files & html files.(UI Part of the application)





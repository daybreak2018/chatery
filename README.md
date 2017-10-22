## Chatery

##### Simple Chat Application usable in Mobile & Desktop Browsers. [http://35.185.246.235/][http://35.185.246.235/]

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
    ./install.sh

Run Instance
    Edit Caddyfile and edit the first line to provide the correct tld/ip
    ./run.sh

Following flags are available
- [--host HOST]
- [-p PORT]
- [--ssl-port SSL_PORT]
- [--ssl]
- [--cert CERT]
- [--key KEY]
- [--chain CHAIN]
- [--tz TIMEZONE]

#### Mini Docs
- dbutils -> Package that manages all the database related operations & queries
- app.py -> File that manages WebSockets & the core of the chat application
- assets -> Contains images,js files & html files.(UI Part of the application)

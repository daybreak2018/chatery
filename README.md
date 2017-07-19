Simple Chat Application usable in Mobile & Desktop Browsers.
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


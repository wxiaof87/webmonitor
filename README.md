# init database
user@server$ sqlite3 test.db 

sqlite> .read tables.sql

# set parameters
edit util.py and change sender, password, recipient

# start server
user@server$ python3 server.py

# open browser
open http://127.0.0.1:8000/ in browser


# Sharder

This is another implementation of the sharder from the
[data8xhub](https://github.com/berkeley-dsep-infra/data8xhub) repository. A
sharder is an application which assigns objects to bins (e.g. users to
JupyterHub instances) by applying some assignment policy. 

sharder.py is a python program which maintains a database of object-bin
assignments. When a request for an object-bin paring is made, if the pairing
already exists, the bin name is returned. If it does not exist, sharder.py
implements the sharder policy, assign the object to a bin (forever), and returns
the bin name.

The current sharder policy is "emptiest bin" and the logic is mostly implemented
in SQL. When a new object of a given kind is added, the database is queried to
see how many of that kind are assigned to each bin, and a new record is added to
the bin with the fewest assignments.


## Implementation

The sharder is meant to be run as an (tornado) web application, integrated with
nginx and protected behind some form of authentication. Incoming requests
contain a username (from authentication) which the sharder uses, together with a
list of hubs, to make a permanent user-hub assignment.

All incoming requests start on Nginx which checks for a cookie (set by the
application) to decide the next hop. If the cookie is set, it will specify the
name of a hub and nginx simply sends the user to that hub. If the cookie is not
set, the request is sent to the sharder which will try to find an existing
assignment. If it does, it will set the cookie to that value and redirect back
to nginx. If it does not, it will implement the sharding policy, add a record
for the new assignment, set the cookie, and send the user back to nginx.

## Running the Sharder

### As an application

A docker-compose file will be provided to spin up nginx, postgresql and tornado,
implementing the full sharder application stack. For the moment
```
python3.6 request-sharder.py
```
Will initialize a sqlite database (with the right behaviour for multiple
connections) and setup a tornado webserver. You can make requests against the
webserver with the REMOTE_USER header set, e.g.
```
  curl -H 'REMOTE_USER: iana 127.0.0.1:8888
```
The output of the request-sharder application should let you know the result of
the assignment.

### Standalone/pytest

test_sharder.py defines an in-memory sqlite database to test the sharder
application. The tests demonstrate how to add new rows to the database and check
that they are "fairly" assigned according to the sharder policy.
```
 $ pytest
 ...
test_sharder.py ...                                              [100%]

======================= 3 passed in 0.76 seconds =======================
```

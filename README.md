# MimoV2

## INDEX
Phase I
build a in memo api server and finish to-do list function

Phase II
integrate with SQLITE
1. use flask-migrate to manage the db migrate, upgrade which is a impl of Alembic
2. has write the script to do db action
3. python manage_db.py db migrate + upgrade, then the db schema will be changed
4. python manage_db.py db migrate --message 'some message you want'
5. sqlite is not support the rename of column, so I have to do this db change manually

usage of Coverage.py
1. coverage run test.py | this command finish the data collect
2. coverage report | this command show the coverage rate in CLI
3. coverage html -d covhtml | generate a html format report
4. in above way, the report will include third-party lib, use --source or --omi to workaround it
    * coverage run --source  ./project test_view.py

Phase III
deploy to server
1. integrate with docker
2. nginx + uWSGI learning
3. simple demo of deploy to server


##TODO LIST
* apache or nginx
* migrate to docker
* build status, once check in to git, give a feed back
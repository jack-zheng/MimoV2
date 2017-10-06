# MimoV2

## TODO
Phase I
build a in memo api server and finish to-do list function

Phase II
integrate with sqlite
1. use flask-migrate to manage the db migrate, upgrade which is a impl of Alembic
2. has write the script to do db action
3. python manage_db.py db migrate + upgrade, then the db schema will be changed
4. python manage_db.py db migrate --message 'some message you want'

Phase III
deploy to server
# MimoV2

## INDEX
Phase I
build a in memo api server and finish to-do list function

Phase II
integrate with SQLITE
1. use flask-migrate to manage the db migrate, upgrade which is a impl of Alembic
2. has write the script to do db action
3. usage of alembic db management
    *. when first time run, use: python manage_db.py db init
    *. python manage_db.py db migrate --message 'some message you want'
    *. python manage_db.py db upgrade, then the db schema will be changed
    *. python manage_db.py db history, to check the change history
    *. when OS is windows, mirgate with --message will be failed
4. SQLITE is not support the rename of column, so I have to do this db change manually
5. cause I used key word 'desc' as column name, so it gives a comma wrap to it

usage of Coverage.py
1. coverage run test.py | this command finish the data collect
2. coverage report | this command show the coverage rate in CLI
3. coverage html -d covhtml | generate a html format report
4. in above way, the report will include third-party lib, use --source or --omi to workaround it
    * coverage run --source  ./project test_view.py

Phase III
deploy to server
1. integrate with docker
    * flask + docker
    * nginx + docker
2. nginx + uWSGI learning
3. simple demo of deploy to server


##TODO LIST
* apache or nginx
* migrate to docker
* build status, once check in to git, give a feed back

---------
## Command Reminder
*. get tasks: curl http://localhost:5000/todo/api/v1/tasks
*. post tasks: curl -i -H "Content-Type: application/json" -X POST -d '{"title":"Read a book"}' http://localhost:5000/todo/api/v1/tasks
*. post tasks:  curl -i -H "Content-Type: application/json" -X PUT -d '{"title":"Read a book02", "id":1}' http://localhost:5000/todo/api/v1/tasks

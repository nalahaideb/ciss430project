# file: makefile
.ONESHELL:
run:
	python3 -m venv venv
	source venv/bin/activate
	export FLASK_APP=flask_app.py
	export FLASK_ENV=development
	firefox localhost:5000 &
	flask --app flask_app.py --debug run
RETARD_MODE:
	rm venv -r
	python3 -m venv venv
	source venv/bin/activate
	pip install flask
	pip install --upgrade pip
	pip install flask-debugtoolbar
	pip install pymysql
	pip install pandas
	pip install numpy
	pip install bcrypt
	pip install flask-login
	pip install pytz
	deactivate

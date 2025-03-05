# file: makefile
.ONESHELL:
run:
	python3 -m venv venv
	source venv/bin/activate
	export FLASK_APP=flask_app.py
	export FLASK_ENV=development
	firefox localhost:5000 &
	flask --app flask_app.py --debug run

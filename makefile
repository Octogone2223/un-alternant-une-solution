loaddata:
	@echo "Extract data..."
	python	.\manage.py loaddata .\authentication\fixtures\schools.json
	python	.\manage.py loaddata .\job\fixtures\jobCodes.json
	python	.\manage.py loaddata .\course\fixtures\courses.json
	python	.\manage.py loaddata .\course\fixtures\refCourseJobCodes.json
	python	.\manage.py loaddata .\course\fixtures\refSchoolCourses.json


loaddataprod:
	@echo "Extract data..."
	python	manage.py loaddata .\authentication\fixtures\schools.json
	python	manage.py loaddata .\job\fixtures\jobCodes2.json
	python	manage.py loaddata .\course\fixtures\courses.json
	python	manage.py loaddata .\course\fixtures\refCourseJobCodes.json
	python	manage.py loaddata .\course\fixtures\refSchoolCourses.json

blackall:
	@echo "Black code..."
	python -m black ./

removeimport:
	@echo "Autokflake..."
	autoflake --in-place --remove-unused-variables --remove-all-unused-imports --recursive .

pycodestyle:
	@echo "Pycodestyle..."
	pycodestyle --statistics --ignore=E501 .
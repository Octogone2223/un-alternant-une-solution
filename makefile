loaddata:
	@echo "Extract data..."
	python	.\manage.py loaddata .\authentication\fixtures\schools.json
	python	.\manage.py loaddata .\job\fixtures\jobCodes.json
	python	.\manage.py loaddata .\course\fixtures\courses.json
	python	.\manage.py loaddata .\course\fixtures\refCourseJobCodes.json
	python	.\manage.py loaddata .\course\fixtures\refSchoolCourses.json


loaddataprod:
	@echo "Extract data..."
	python manage.py loaddata authentication/fixtures/schools.json
	python manage.py loaddata authentication/fixtures/company.json
	python manage.py loaddata job/fixtures/jobCodes.json
	python manage.py loaddata job/fixtures/job.json
	python manage.py loaddata course/fixtures/courses.json
	python manage.py loaddata course/fixtures/refCourseJobCodes.json
	python manage.py loaddata course/fixtures/refSchoolCourses.json

loadalldataprod:
	@echo "Extract data..."
	python manage.py loaddata core/fixtures/all_prod.json

blackall:
	@echo "Black code..."
	python -m black ./

removeimport:
	@echo "Autokflake..."
	autoflake --in-place --remove-unused-variables --remove-all-unused-imports --recursive .

pycodestyle:
	@echo "Pycodestyle..."
	pycodestyle --statistics --ignore=E501 .
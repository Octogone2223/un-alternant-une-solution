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
	python	manage.py loaddata .\job\fixtures\jobCodes.json
	python	manage.py loaddata .\course\fixtures\courses.json
	python	manage.py loaddata .\course\fixtures\refCourseJobCodes.json
	python	manage.py loaddata .\course\fixtures\refSchoolCourses.json
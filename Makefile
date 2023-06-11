# ----------------------------------
#          PACKAGE ACTIONS
# ----------------------------------
merge_tables_from_bq:
	python -c 'from Dash_Work.data.utils_masha import merge_tables_from_bq; merge_tables_from_bq()'

temp_upload:
	python -c 'from Dash_Work.backend.data.utils_masha import temp_upload; temp_upload()'

get_jobs_and_load_to_bg:
	python -c 'from Dash_Work.backend.api.all_jobs_api import get_jobs_and_load_to_bg; get_jobs_and_load_to_bg()'

get_all_job_details:
	python -c 'from Dash_Work.backend.api.general_api import get_all_job_details; get_all_job_details()'

# ----------------------------------
#          INSTALL & TEST
# ----------------------------------
install_requirements:
	@pip install -r requirements.txt

check_code:
	@flake8 scripts/* Dash_Work/*.py

black:
	@black scripts/* Dash_Work/*.py

test:
	@coverage run -m pytest tests/*.py
	@coverage report -m --omit="${VIRTUAL_ENV}/lib/python*"

ftest:
	@Write me

clean:
	@rm -f */version.txt
	@rm -f .coverage
	@rm -fr */__pycache__ */*.pyc __pycache__
	@rm -fr build dist
	@rm -fr Dash_Work-*.dist-info
	@rm -fr Dash_Work.egg-info

install:
	@pip install . -U

all: clean install test black check_code

count_lines:
	@find ./ -name '*.py' -exec  wc -l {} \; | sort -n| awk \
        '{printf "%4s %s\n", $$1, $$2}{s+=$$0}END{print s}'
	@echo ''
	@find ./scripts -name '*-*' -exec  wc -l {} \; | sort -n| awk \
		        '{printf "%4s %s\n", $$1, $$2}{s+=$$0}END{print s}'
	@echo ''
	@find ./tests -name '*.py' -exec  wc -l {} \; | sort -n| awk \
        '{printf "%4s %s\n", $$1, $$2}{s+=$$0}END{print s}'
	@echo ''

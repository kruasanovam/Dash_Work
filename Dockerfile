FROM python:3.10.6-buster
COPY requirements_api.txt /requirements.txt
RUN pip install -r requirements.txt
COPY Dash_Work/backend/api/fast.py /Dash_Work/backend/api/fast.py
COPY key.json /key.json
COPY setup.py setup.py
COPY Dash_Work/params.py /Dash_Work/params.py
RUN pip install -e .
CMD uvicorn Dash_Work.backend.api.fast:app --host 0.0.0.0 --port $PORT

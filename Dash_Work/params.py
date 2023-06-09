import os

##################  CONSTANTS  #####################
LOCAL_DATA_PATH_ALL_JOBS = os.path.join(os.path.expanduser('~'),
                                        "code", "LennartSchulze", "Dash_Work", "data",
                                        "raw_generated", "all_jobs")

LOCAL_DATA_PATH_JOB_DETAILS = os.path.join(os.path.expanduser('~'),
                                        "code", "LennartSchulze", "Dash_Work", "data",
                                        "raw_generated", "job_details")

LOCAL_DATA_PATH_VALID_ORTS = os.path.join(os.path.expanduser('~'),
                                        "code", "LennartSchulze", "Dash_Work", "data",
                                        "source_data")

##################  GCP DETAILS  #####################
GCP_PROJECT = 'wagon-bootcamp-384015'
BQ_DATASET = 'dash_work'

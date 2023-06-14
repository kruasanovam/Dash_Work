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

LOCAL_PROJECT_PATH = os.path.join(os.path.expanduser('~'))

##################  GCP DETAILS  #####################
GCP_PROJECT = 'wagon-bootcamp-384015'
BQ_DATASET = 'dash_work'

##################  STREAMLIT APP VARS  #####################
SECTORS = ["All Sectors",
                  "Arbeitnehmerüberlassung, Zeitarbeit",
                  "Einzelhandel, Großhandel, Außenhandel",
                  "Management, Beratung, Recht, Steuern",
                  "Bau, Architektur",
                  "Gesundheit, Soziales",
                  "Metall, Maschinenbau, Anlagenbau",
                  "Arbeitsvermittlung, privat",
                  "Hotel, Gaststätten, Tourismus, Kunst, Kultur, Freizeit",
                  "Sicherheits-, Reinigungs-, Reparatur- und weitere Dienstleistungen",
                  "Logistik, Transport, Verkehr",
                  "IT, Computer, Telekommunikation",
                  "Rohstoffverarbeitung, Glas, Keramik, Kunststoff, Holz",
                  "Elektro, Feinmechanik, Optik, Medizintechnik",
                  "Nahrungs- / Genussmittelherstellung",
                  "Öffentlicher Dienst, Organisationen",
                  "Banken, Finanzdienstleistungen, Immobilien, Versicherungen",
                  "Bildung, Erziehung, Unterricht",
                  "Fahrzeugbau, Fahrzeuginstandhaltung",
                  "Abfallwirtschaft, Energieversorgung, Wasserversorgung",
                  "Chemie, Pharma, Biotechnologie",
                  "Landwirtschaft, Forstwirtschaft, Gartenbau",
                  "Papier, Druck, Verpackung",
                  "Konsum- und Gebrauchsgüter",
                  "Werbung, Öffentlichkeitsarbeit",
                  "Wissenschaft, Forschung, Entwicklung",
                  "Medien, Informationsdienste",
                  "Rohstoffgewinnung, Rohstoffaufbereitung",
                  "Luftfahrttechnik, Raumfahrttechnik"]

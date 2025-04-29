
""" confg.py: AD Integration Config """

# config.py
import os
from dotenv import load_dotenv

load_dotenv()

ORGANISATION_URL = os.getenv("ORGANISATION_URL")
ORGANISATION = ORGANISATION_URL.split("/")[-1]
PERSONAL_ACCESS_TOKEN = os.getenv("PERSONAL_ACCESS_TOKEN")
RETRIEVAL_ACCESS_TOKEN = os.getenv("RETRIEVAL_ACCESS_TOKEN")
PROJECT_NAME = os.getenv("PROJECT_NAME")
ISSUE_TYPE = os.getenv("ISSUE_TYPE")

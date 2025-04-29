[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/zqYhAx1c)

# COMP3932 Synoptic Project (EPA)
WOODHAM25-FINAL

# OVERVIEW
This project introduces 'Flik', a bug reporting platform designed to help clients during UAT raise high-quality, actionable bugs tickets.
These tickets are processed with natural language processing technologies (NLP) to provide a summary, priority and tags for the ticket, which are used to match a ticket to a developer.
A tickets legitimacy is also assessed against defined documentation, and any legitimate tickets check against previously raised tickets to provide developers with potential insights into resolution.
The tickets are sent directly to a defined Azure DevOps project board.

# Requirements
For this system you will need to install the 'requirements.txt' file 
- pip install -r requirements.txt.
It is recommended these dependencies are installed in a Python virtual environment
- python -m venv <environment-name>
- Activate your virtual environment via:
    - <environment-name>\Scripts\activate
To support the NLP technologies, you must open a Python shell and download the following
- import nltk
- nltk.download('punkt')  # or nltk.download() to open a full GUI

You will also need:
- Python 3.11
- An Azure DevOps subscription and access to https://dev.azure.com/comp3932-flik
    - Access to Azure is required to see the formatted tickets. Access can be granted by reaching out to the project owner (sc21nw@leeds.ac.uk)

# Model Requirements
The fine-tuned models used for NLP processing are too large to be tracked in GitHub.
They are provided in an additional .zip archive and available at: https://leeds365-my.sharepoint.com/:f:/g/personal/sc21nw_leeds_ac_uk/ElGRt6X0FUVBkxNxjgvnktABCoZ5qfRTN7jHGH_OF3g5tA?e=NuYn2u
- This is available to staff at the University of leeds with a valid '@leeds.ac.uk' domain. 
- After extracting the file contents, you will see:
    1. fine_tuned_assigner
    2. fine_tuned_prioritiser
- Navigate to 'synoptic-project-nwoodham72/flik-foundation/bert/models'
- Move the models to this location

# Setup & Instructions
1. Check the required dependencies are installed 
2. Navigate to 'synoptic-project-nwoodham72/flik-foundation'
3. Enter 'flask run' on the command line to start a Flask application
4. The application will be available on localhost: http://127.0.0.1:5000/
5. An 'admin' site is available for the application to visualise the database tables: http://127.0.0.1:5000/admin

# Accounts 
There are 3 different roles within the application with different permissions.
Permissions can be found in Appendix C1, Figure C.2

Credentials are provided below:
1. manager
    - Email: nathanmw72@gmail.com
    - Password: manager
2. developer
    - Email: sc21nw@leeds.ac.uk
    - Password: developer
3. client
    - Email: client@client.com 
    - Password: client 

You can also register a new account. NB: new manager and developer accounts require an email that is defined in Azure DevOps.
To create an account of one of these types, please contact the project owner (sc21nw@leeds.ac.uk) to allow access to the Azure DevOps board.
You can create a client account with no additional overhead or access required. 

# ESSENTIAL NOTES
- Install all dependencies in a virtual environment
- Make sure the virtual environment is running before using the application 
- Ensure the models are installed and located correctly in the project folder
- Contact the sc21nw@leeds.ac.uk for access permissions
# MyUNSW_Extension

MyUNSW_Extension is an enhanced utility tool designed to interact with the UNSW student database, offering extended functionalities over the standard myUNSW portal. Built with Python and leveraging PostgreSQL with psycopg2 for database interactions, this tool is tailored for academic administrators and students, providing detailed insights and analytics derived from the data of over 60,000+ UNSW students.

## Features

- **Academic Transcripts:** Generate detailed academic transcripts for students, providing more information than regular myUNSW transcripts.
- **Degree Progression Checks:** Perform comprehensive checks on students' progression through their programs or streams, aiding in academic planning and advising.
- **Program and Stream Rules:** Access a compiled list of rules and requirements for specific programs or streams, assisting in academic guidance.
- **Overseas Student Tracking:** Monitor and report on the proportion of overseas students, facilitating demographic studies and university planning.
- **Subject Satisfaction Tracking:** Evaluate and report satisfaction levels within any given subject, aiding in curriculum development and teaching improvement.

## Technologies

- **Python:** Core scripting and logic implementation.
- **PostgreSQL:** Backend database for storing and managing student records.
- **SQL and PL/pgSQL:** Used for creating views and functions within the PostgreSQL database.
- **psycopg2:** PostgreSQL adapter for Python, enabling database connections and operations.

## Installation

### Prerequisites

Ensure you have Python and PostgreSQL installed on your system. Python 3.6 or later is recommended. Also, install psycopg2 using pip:

```bash
pip install psycopg2
```

### Database Setup

Configure your PostgreSQL database to connect to the UNSW student records. Ensure the creation of the necessary tables, views, and functions as defined in the project's SQL scripts.

### Configuration

Update the `config.py` file (or create it based on the provided template) with your database connection details, including host, database name, user, and password.

### Running Scripts

Once the database is configured, and the application is set up, you can run the Python scripts to interact with the database and utilize the extended functionalities.

## Usage

The MyUNSW_Extension provides several functionalities to assist with managing and retrieving information related to student records, degree progression, and course satisfaction. Below are the usage instructions for each functionality available within the extension. Navigate to the directory containing the scripts and run the desired functionality with the appropriate command line arguments as shown:

### Functionality

- **Print a Student's Transcript:**
    ```bash
    Usage: python transcript.py zID
    ```
    Replace `zID` with the student's unique identifier.

- **Perform a Degree Progression Check for a Student:**
    ```bash
    Usage: python progressionCheck.py zID [Program Stream]
    ```
    Replace `zID` with the student's unique identifier. Optionally, specify the Program and Stream codes to check progression against specific academic requirements.

- **Print Program or Stream Rules:**
    ```bash
    Usage: python program+streamRules.py (ProgramCode|StreamCode)
    ```
    Replace `(ProgramCode|StreamCode)` with the actual code of the Program or Stream whose rules you want to print.

- **Track the Proportion of Overseas Students:**
    No command line arguments are needed for this functionality. Simply execute the script:
    ```bash
    python overseasStudents.py
    ```

- **Track Satisfaction in a Given Subject:**
    ```bash
    Usage: python courseSatisfaction.py SubjectCode
    ```
    Replace `SubjectCode` with the code of the subject for which you want to track satisfaction levels.

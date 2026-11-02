# Absence
Et Python bibliotek til at håndtere sygefravær i OPUS

## Installation

### Forudsætninger

- Python 3.12 eller nyere  
- uv


### Opsætning

1. Klon repository’et:
```bash
git clone https://github.com/nkAPIs/Absence.git
cd Absence
uv sync
````
### Brug af biblioteket

#### Standard installation
1. installer whl fil:
```uv
 uv add Absence@git+https://github.com/nkAPIs/Absence.git
```

2. importer Absence:
```python
from Absence.src.Absence import Absence
```
3. Opret .env fil
```bash
CLIENT_CERT_PASSWORD="<certifikat password>"
CLIENT_CERT_P12="<fuld sti til .P12 certifikat fil>"
BASE_URL="https://opus.integration.kmd.dk/lpt/"
CLIENT_ID = <number eks. 123 kommune kode til OPUS>
VENDOR_UUID="A0369F2D21711ED999CDA1F855B02B34"
WSDL_PATH="sti til placering af wsdl filer eks. /usr/tmp/wsdl/"
```

### Funktioner
+ set_sick_leave(start_date, end_date, personnel_number)
 
    opretter sygefravær på medarbejder.

    start_date: start dato for fravær. eks. 2025-10-23
    end_date: slut dato for fravær . eks. 9999-12-31  ==> åbent fravær
    personnel_number: medarbejder nummer på person der skal sygemeldes.
    
    **Retur værdier**
    
    Ingen fejl
    ```bash
    [{
        'StatusType': None,
        'MessageText': None
    }]
    ```
    Fejl kollision på dagen
    ```bash
    [{
        'StatusType': 'E',
        'MessageText': 'Indføjning ikke mulig pga. kollision'
    }, {
        'StatusType': 'W',
        'MessageText': 'Kollision med Fravær (2001) / Sygdom (IT2001/SY) fra 22.10.2025 til 31.12.9999'
    }]
    ```
    kollision afkorter fravær
    ```bash
    [{
        'StatusType': None,
        'MessageText': None
    }, {
        'StatusType': 'W',
        'MessageText': 'Fravær afkortet til 06.11.2025 pga. kollision med FE den 07.11.2025.'
    }]

    ```

- end_sick_leave(end_date, personnel_number)
    
    Slutter sygefravær for medarbejder (raskmelder)
    Tager seneste dato for aktiv sygemelding.
    end_date: slut dato for fravær . eks. 2025-10-23  ==> slut dato for fravær
    personnel_number: medarbejder nummer på person der skal sygemeldes.

    
    **Retur værdier**
    
    Ingen fejl
    ```bash
    [{
        'StatusType': None,
        'MessageText': None
    }]
    ```
    Kan ikke finde fravær
    ```bash
    [{
    'StatusType': 'E',
    'MessageText': 'Teknisk fejl. Fraværet du ønsker at ændre/slette, kunne ikke findes.'
    }]
    ```

    Hvis medarbejder ikke findes og startdato dermed er None
    kastes en *ValueError("No existing sick leave found for the given personnel number.")*

## Eksempel kode
```python
### test.py
### importing necessary modules and loading environment variables
import os
from dotenv import load_dotenv
from Absence.src.Absence.absence import Absence, AbsenceType
from datetime import datetime


### loading environment variables from a .env file
### Make sure to create a .env file with the required variables
load_dotenv()
### initializing the Absence class with environment variables
absence = Absence(
    client_cert_p12=os.getenv("CLIENT_CERT_P12"),
    client_cert_password=os.getenv("CLIENT_CERT_PASSWORD"),
    client_id=os.getenv("CLIENT_ID"),
    vendor_uuid=os.getenv("VENDOR_UUID"),
    base_url=os.getenv("BASE_URL"),
    wsdl_path=os.getenv("WSDL_PATH")
)

#### fetching absence attendance for a specific personnel number and date range
response = absence.get_absence_attendance_by_period(
    start_date="2025-01-01",
    end_date="2025-10-22",
    personnel_number="123456"
)
print(response)
### setting sick leave for a personnel number
response = absence.set_sick_leave(start_date="2025-10-22", end_date="9999-12-31", personnel_number="123456")
print(response)

### ending sick leave for a personnel number
response = absence.end_sick_leave(end_date="2025-10-22",personnel_number="123456")
print(response)

### setting child sick leave for a personnel number
response = absence.set_child_sick_leave(start_date="2025-10-22", end_date="2025-10-23", personnel_number="123456")
print(response)
```



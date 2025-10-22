### test.py
### importing necessary modules and loading environment variables
import os
from dotenv import load_dotenv
from Absence.src.absence import Absence
from Absence.src.absence import AbsenceType
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

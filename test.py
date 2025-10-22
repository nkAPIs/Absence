import os
from dotenv import load_dotenv
from Absence.src.absence import Absence
from Absence.src.absence import AbsenceType

absence = Absence(
    client_cert_p12=os.getenv("CLIENT_CERT_P12"),
    client_cert_password=os.getenv("CLIENT_CERT_PASSWORD"),
    client_id=os.getenv("CLIENT_ID"),
    vendor_uuid=os.getenv("VENDOR_UUID"),
    base_url=os.getenv("BASE_URL"),
    wsdl_path=os.getenv("WSDL_PATH")
)

# response = absence.get_absence_attendance_by_period(
#     start_date="2025-01-01",
#     end_date="2025-10-20",
#     personnel_number="122743"
# )
# print(response)
# response = absence.set_absence_attendance(
#     start_date="2025-10-22",
#     end_date="9999-12-31",
#     personnel_number="122743",
#     absence_type=AbsenceType.SICK_LEAVE
# )
# print(response)
# response = absence.set_absence_attendance(
#     start_date="2025-10-22",
#     end_date="2025-10-23",
#     personnel_number="122743",
#     absence_type=AbsenceType.CHILD_SICK_LEAVE
# )

response = absence.set_sick_leave("2025-10-22", "9999-12-31", "122743")
print(response)
response = absence.end_sick_leave("2025-10-22", "9999-12-31", "122743")
print(response)

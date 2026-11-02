### test.py
### importing necessary modules and loading environment variables
import os
from dotenv import load_dotenv
import Absence

from Absence.src.Absence.absence import Absence
from Absence.src.Absence.absence import AbsenceType
import json
from datetime import date

def json_default(obj):
    if isinstance(obj, date):
        return obj.isoformat()   # Convert to "YYYY-MM-DD"
    raise TypeError(f"Type {type(obj)} not serializable")


### loading environment variables from a .env file
### Make sure to create a .env file with the required variables
load_dotenv()
### initializing the Absence class with environment variables
print(os.getenv("WSDL_PATH"))
absence = Absence(
    client_cert_p12=os.getenv("CLIENT_CERT_P12"),
    client_cert_password=os.getenv("CLIENT_CERT_PASSWORD"),
    client_id=os.getenv("CLIENT_ID"),
    vendor_uuid=os.getenv("VENDOR_UUID"),
    base_url=os.getenv("BASE_URL"),
    wsdl_path=os.getenv("WSDL_PATH")
)

emps = ["120862",
"178672",]

for emp in emps:
    result = absence.get_leave_data(personnel_number=emp, all_data=False, filtered_leave_codes=True, only_active_leave=False)
    print(json.dumps(result, ensure_ascii=False, indent=4, default=json_default))


# {
#   "cc": "mfjan@naestved.dk",
#   "id": "AAMkAGE5ZmZkMTIxLTg3YzEtNDk3ZS1hNjQ2LTUwNjhjN2RlOWMzNABGAAAAAABOcgXq-8WTRJzmKvjlhQlJBwAPIiaDk3AeQ6zSAZtiSflCAAAAAAEMAAAPIiaDk3AeQ6zSAZtiSflCAAQVs0vKAAA=",
#   "body": "***",
#   "from": "marcst@naestved.dk",
#   "name": "Mette Fladberg Jannerup",
#   "send_to": "kaern@naestved.dk;_idm_PG_BornogUngeTeamSyd_5621@naestved.dk;underretning@naestved.dk",
#   "subject": "Barn syg",
#   "mail_group": "_idm_PG_BornogUngeTeamSyd_5621@naestved.dk",
#   "manager_upn": "kaern@naestved.dk",
#   "on_behalf_of": "frarob@naestved.dk",
#   "received_date": "2026-11-02T07:09:10Z",
#   "employee_number": "120862"
# }
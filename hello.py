
from zeep import Client, Transport
from requests_pkcs12 import Pkcs12Adapter
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    # === CERTIFICATE CONFIG ===
    P12_FILE = os.getenv("CLIENT_CERT_P12")
    P12_PASSWORD = os.getenv("CLIENT_CERT_PASSWORD")

    # === WSDL + ENDPOINT CONFIG ===
    WSDL_PATH = "/Users/lakas/git/Absence/Absence/src/wdsl/GetAbsenceAttendanceByPeriod_OS_SIService_v.3.5.wsdl"
    ENDPOINT_URL = "https://opus-api-prod.prod01.apimanagement.eu10.hana.ondemand.com/lpt/get-absence-attendance-by-period"


    # === SECURE SESSION ===
    session = requests.Session()
    session.mount("https://", Pkcs12Adapter(pkcs12_filename=P12_FILE, pkcs12_password=P12_PASSWORD))
    transport = Transport(session=session)

    # === LOAD CLIENT ===
    client = Client(wsdl=WSDL_PATH, transport=transport)

    for service in client.wsdl.services.values():
        for port in service.ports.values():
            print(f"Service: {service.name}")
            print(f" Port: {port.name}")
            print(" Operations:")
            for op_name, op in port.binding._operations.items():
                print(f"  - {op_name}")

    service = client.create_service(
        "{urn:kmd.dk:LPT:VACAB:external}GetAbsenceAttendanceByPeriod_OS_SIBinding",
        ENDPOINT_URL
    )
    # === REQUEST PAYLOAD ===
    request = {
        "ClientID": "370",
        "VendorUUID": "A0369F2D21711ED999CDA1F855B02B34",
        "StartDate": "2025-01-01",
        "EndDate": "2025-10-20",
        "PersonnelNumber": "122743"
    }
    


    # ✅ Use the correct operation name
    try:
        response = service.GetAbsenceAttendanceByPeriod_OS_SI(**request)
        print("Response received:")
        print(response)
    except Exception as e:
        print("SOAP call failed:")
        print(e)

if __name__ == "__main__":
    main()
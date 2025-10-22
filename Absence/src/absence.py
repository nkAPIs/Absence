from zeep import Client, Transport
from requests_pkcs12 import Pkcs12Adapter
import requests


class Absence:
    def __init__(self, client_cert_p12, client_cert_password, client_id, vendor_uuid, base_url, wsdl_path):
        # === SECURE SESSION ===
        self.client_cert_p12 = client_cert_p12
        self.client_cert_password = client_cert_password
        self.client_id = client_id
        self.vendor_uuid = vendor_uuid
        self.base_url = base_url #"https://opus-api-prod.prod01.apimanagement.eu10.hana.ondemand.com/lpt/"
        self.wsdl_path = wsdl_path
        self.session = requests.Session()
        self.session.mount("https://", Pkcs12Adapter(pkcs12_filename=client_cert_p12, pkcs12_password=client_cert_password))
        self.transport = Transport(session=self.session)

    def _get_client(self, wsdl_path):
        return Client(wsdl=wsdl_path, transport=self.transport)

       
    def get_absence_attendance_by_period(self, start_date, end_date, personnel_number):
        client = self._get_client(wsdl_path=f"{self.wsdl_path}GetAbsenceAttendanceByPeriod_OS_SIService_v.3.5.wsdl")
        request = {
            "ClientID": self.client_id,
            "VendorUUID": self.vendor_uuid,
            "StartDate": start_date,
            "EndDate": end_date,
            "PersonnelNumber": personnel_number
        }
        service = client.create_service(
            "{urn:kmd.dk:LPT:VACAB:external}GetAbsenceAttendanceByPeriod_OS_SIBinding",
            f"{self.base_url}get-absence-attendance-by-period"
        )
        
        response = service.GetAbsenceAttendanceByPeriod_OS_SI(**request)
        return response
        
    def set_absence_attendance(self, start_date, end_date, personnel_number, absence_type):
        client = self.get_client(wsdl_path=f"{self.wsdl_path}SetAbsenceAttendance_OS_SIService_v.3.5.wsdl")
        request = {
            "ClientID": self.client_id,
            "StartDate": start_date,
            "EndDate": end_date,
            "Operation": "C",  # C = Create, U = Update, D = Delete   ??????????
            "PersonnelNumber": personnel_number,
            "AbsenceAttendanceType": absence_type,
            "ExternalID": "SOAPUI#001",
            "VendorUUID": "A0369F2D21711ED999CDA1F855B02B34"
        }


        service = client.create_service(
            "{urn:kmd.dk:LPT:VACAB:external}SetAbsenceAttendance_OS_SI",
            f"{self.base_url}set-absence-attendance"
        )

        

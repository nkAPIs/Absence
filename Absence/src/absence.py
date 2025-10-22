from zeep import Client, Transport
from requests_pkcs12 import Pkcs12Adapter
import requests
from enum import Enum
class AbsenceType(Enum):
    SICK_LEAVE = "SY"
    CHILD_SICK_LEAVE = "BS"
    
class OperationType(Enum):
    INSERT = "INS"
    UPDATE = "MOD"
    DELETE = "DEL"

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

    def _get_request(self, operation: OperationType, start_date, end_date, personnel_number, absence_type: AbsenceType):

        if operation == OperationType.INSERT:
            return {
                "ClientID": self.client_id,
                "StartDate": start_date,
                "EndDate": end_date,
                "Operation": operation.value,
                "PersonnelNumber": personnel_number,
                "AbsenceAttendanceType": absence_type.value,
                "VendorUUID": "A0369F2D21711ED999CDA1F855B02B34"
            }
        elif operation == OperationType.UPDATE:
            return {
                "ClientID": self.client_id,
                "StartDate": start_date,
                "OriginalStartDate": start_date,
                "EndDate": end_date,
                "OriginalEndDate": end_date,
                "Operation": operation.value,
                "PersonnelNumber": personnel_number,
                "AbsenceAttendanceType": absence_type.value,
                "VendorUUID": "A0369F2D21711ED999CDA1F855B02B34"
            }
        elif operation == OperationType.DELETE:
            return {
                "ClientID": self.client_id,
                "StartDate": start_date,
                "EndDate": end_date,
                "Operation": operation.value,
                "PersonnelNumber": personnel_number,
                "AbsenceAttendanceType": absence_type.value,
                "VendorUUID": "A0369F2D21711ED999CDA1F855B02B34"
            }
        else:
            raise ValueError("Invalid operation type")
                    
                
    def set_absence_attendance(self, start_date, end_date, personnel_number, absence_type: AbsenceType, operation: OperationType):
        client = self._get_client(wsdl_path=f"{self.wsdl_path}SetAbsenceAttendance_OS_SIService_v.3.5.wsdl")
        request = self._get_request(operation, start_date, end_date, personnel_number, absence_type)

        service = client.create_service(
            "{urn:kmd.dk:LPT:VACAB:external}SetAbsenceAttendance_OS_SIBinding",
            f"{self.base_url}set-absence-attendance"
        )
        response = service.SetAbsenceAttendance_OS_SI(**request)
        return response
    ############################################################################################
    #### Convenience Methods ####
    ############################################################################################
    def set_child_sick_leave(self, start_date, end_date, personnel_number):
        return self.set_absence_attendance(
            start_date=start_date,
            end_date=end_date,
            personnel_number=personnel_number,
            absence_type=AbsenceType.CHILD_SICK_LEAVE,
            operation=OperationType.INSERT
        )
        
    def set_sick_leave(self, start_date, end_date, personnel_number):
        return self.set_absence_attendance(
            start_date=start_date,
            end_date=end_date,
            personnel_number=personnel_number,
            absence_type=AbsenceType.SICK_LEAVE,
            operation=OperationType.INSERT
        )   
        
    def end_sick_leave(self, start_date, end_date, personnel_number):
        return self.set_absence_attendance(
            start_date=start_date,
            end_date=end_date,
            personnel_number=personnel_number,
            absence_type=AbsenceType.SICK_LEAVE,
            operation=OperationType.UPDATE
        )
        
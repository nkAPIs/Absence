from zeep import Client, Transport
from requests_pkcs12 import Pkcs12Adapter
import requests
from enum import Enum
from zeep.helpers import serialize_object
from datetime import datetime, timedelta, date

class AbsenceType(Enum):
    SICK_LEAVE = "SY"
    CHILD_SICK_LEAVE = "BS"
    
class OperationType(Enum):
    INSERT = "INS"
    UPDATE = "MOD"
    DELETE = "DEL"

class Absence:
    def __init__(self, client_cert_p12:str, client_cert_password:str, client_id:str, vendor_uuid:str, base_url:str, wsdl_path:str, leave_codes:list[str]=None):
        # === SECURE SESSION ===
        self.client_cert_p12 = client_cert_p12
        self.client_cert_password = client_cert_password
        self.client_id = client_id
        self.vendor_uuid = vendor_uuid
        self.base_url = base_url #"https://opus.integration.kmd.dk/lpt/"
        self.wsdl_path = wsdl_path
        self.session = requests.Session()
        self.session.mount("https://", Pkcs12Adapter(pkcs12_filename=client_cert_p12, pkcs12_password=client_cert_password))
        self.transport = Transport(session=self.session)
        if leave_codes is None:
            self.leave_codes = {
                "BAO",    # BA M-F-MM orlov inden 1år
                "BIF",    # Barn indl. efter fødsel.
                "BA",     # Barsel
                "BAF",    # Barsel fædre
                "BUF",    # BU over en md. m.fe u.dp
                "BUD",    # BU over en md. med dp
                "BUM",    # BU over en md. uden dp
                "BD",     # BU under en md. med dp
                "ORR",    # Orlov intet løntræk
                "ORL",    # Orlov med løn
                "OR",     # Orlov u/løn-med pension
                "ORU",    # Orlov u/løn-over en måned
                "ORP",    # Orlov u/løn-uden pension
            }
        else:
            self.leave_codes = leave_codes
            
    def _get_client(self, wsdl_path):
        return Client(wsdl=wsdl_path, transport=self.transport)


    def export_rawdata(self, response, filtered_leave_codes=False):
        items = []

        if response is None or response.AbsenceAttendance is None or response.AbsenceAttendance.item is None:
            return items

        if filtered_leave_codes:
            items_or = [
                itm for itm in response["AbsenceAttendance"]["item"]
                if itm["Key"]["AbsenceAttendanceType"] in self.leave_codes
            ]
        else:
            items_or = [itm for itm in response["AbsenceAttendance"]["item"]]        
                
        for itm in items_or:
            items.append({
                'PersonnelNumber': itm.Item.PersonnelNumber,
                'StartDate': itm.Item.StartDate,
                'EndDate': itm.Item.EndDate,
                'AbsenceAttendanceType': itm.Item.AbsenceAttendanceType,
                'AbsenceAttendanceTypeText': itm.Item.AbsenceAttendanceTypeText,
            })
        return items

    def _make_start_end_dates(self):
        start_datetime = datetime.now()
        end_datetime = start_datetime + timedelta(days=365)
        start_date = datetime.strptime(start_datetime.strftime("%Y-%m-%d"), "%Y-%m-%d").date()
        end_date = datetime.strptime(end_datetime.strftime("%Y-%m-%d"), "%Y-%m-%d").date()
        return start_date, end_date
    
    def get_leave_data(self, personnel_number, all_data=False, filtered_leave_codes=False, only_active_leave=False):
        results = []

        start_date, end_date = self._make_start_end_dates()
        response = self.get_absence_attendance_by_period(start_date, end_date, personnel_number)
        
        
        
        if response.ReturnStatus is None and response is not None and response.AbsenceAttendance is not None and response.AbsenceAttendance.item is not None:

            if all_data:
                return self.export_rawdata(response, filtered_leave_codes)

            items_or = [
                    itm for itm in response["AbsenceAttendance"]["item"]
                    if itm["Key"]["AbsenceAttendanceType"] in self.leave_codes
                    # if itm["Key"]["AbsenceAttendanceType"].startswith("OR") or itm["Key"]["AbsenceAttendanceType"] in self.not_leave_codes
                ]

            # If only active leave is requested, filter out items that are not today in period
            if only_active_leave:
                items_or = [
                    itm for itm in items_or
                    if self._is_today_in_period(itm.Item['StartDate'], itm.Item['EndDate'])
                ]
            # Add the items to the results
            for i in items_or:
                results.append({
                        'PersonnelNumber': personnel_number,
                        'IsOnLeave': self._is_today_in_period(i.Item['StartDate'], i.Item['EndDate']),
                        'StartDate': start_date,
                        'EndDate': end_date,
                        'AbsenceAttendanceType': i.Item['AbsenceAttendanceType'],
                        'AbsenceAttendanceTypeText': i.Item['AbsenceAttendanceTypeText'],
                    })
        #
        # If no results, return an empty list
        if len(results) > 0:
            return results
        return [{
            'PersonnelNumber': personnel_number,
            'IsOnLeave': False,
            'StartDate': '',
            'EndDate': '',
            'AbsenceAttendanceType': '',
            'AbsenceAttendanceTypeText': '',
        }]

    def _is_today_in_period(self, start_date_str: str, end_date_str: str) -> bool:
        today = date.today()

        start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end = datetime.strptime(end_date_str, "%Y-%m-%d").date()

        return start <= today <= end
    
    def get_absence_attendance_by_period(self, start_date, end_date, personnel_number):
        client = self._get_client(wsdl_path=f"{self.wsdl_path}GetAbsenceAttendanceByPeriod_OS_SIService_v.3.6.wsdl")
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

    def _get_request(self, operation: OperationType, start_date, end_date, personnel_number, absence_type: AbsenceType, original_enddate=None):

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
                "OriginalEndDate": original_enddate,
                "Operation": operation.value,
                "PersonnelNumber": personnel_number,
                "AbsenceAttendanceType": absence_type.value,
                "OriginalAbsenceAttendanceType": absence_type.value,
                "VendorUUID": "A0369F2D21711ED999CDA1F855B02B34"
            }
        # elif operation == OperationType.DELETE:
        #     return {
        #         "ClientID": self.client_id,
        #         "StartDate": start_date,
        #         "EndDate": end_date,
        #         "Operation": operation.value,
        #         "PersonnelNumber": personnel_number,
        #         "AbsenceAttendanceType": absence_type.value,
        #         "VendorUUID": "A0369F2D21711ED999CDA1F855B02B34"
        #     }
        else:
            raise ValueError("Invalid operation type")
                    
                
    def set_absence_attendance(self, start_date, end_date, personnel_number, absence_type: AbsenceType, operation: OperationType, original_enddate=None):
        client = self._get_client(wsdl_path=f"{self.wsdl_path}SetAbsenceAttendance_OS_SIService_v.3.6.wsdl")
        request = self._get_request(operation, start_date, end_date, personnel_number, absence_type, original_enddate)
        
        service = client.create_service(
            "{urn:kmd.dk:LPT:VACAB:external}SetAbsenceAttendance_OS_SIBinding",
            f"{self.base_url}set-absence-attendance"
        )
        response = service.SetAbsenceAttendance_OS_SI(**request)
        return response
    
    def _get_start_end_dates_for_personnel(self, personnel_number, absence_type: AbsenceType):
        response = self.get_absence_attendance_by_period(
            start_date="2000-01-01",
            end_date="9999-12-31",
            personnel_number=personnel_number
        )
        data = serialize_object(response)

        items = data.get("AbsenceAttendance", {}).get("item", [])

        # Filter only specified absence types
        filtered_items = [i["Item"] for i in items if i["Item"].get("AbsenceAttendanceType") == absence_type.value]

        if filtered_items:
            # Sort by StartDate descending
            latest = max(filtered_items, key=lambda x: datetime.strptime(x["StartDate"], "%Y-%m-%d"))
            return latest["StartDate"], latest["EndDate"]
        else:
            return None, None

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
        
    def end_sick_leave(self, end_date, personnel_number):
        original_startdate, original_enddate = self._get_start_end_dates_for_personnel(personnel_number, AbsenceType.SICK_LEAVE)
        if not original_startdate or not original_enddate:
            raise ValueError("No existing sick leave found for the given personnel number.")
        
        return self.set_absence_attendance(
            start_date=original_startdate,
            end_date=end_date,
            personnel_number=personnel_number,
            absence_type=AbsenceType.SICK_LEAVE,
            operation=OperationType.UPDATE,
            original_enddate=original_enddate
        )
    
    
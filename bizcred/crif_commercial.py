from bizcred import modules as mods
from django.contrib.auth.models import User
from bizcred.modules.company_details import CompanyDetails
from bizcred import methods, enums
import requests, json, datetime, pytz, xmltodict
import xml.etree.cElementTree as ET
from django.conf import settings
from dicttoxml import dicttoxml


def crif_institution_stage_1(request, uid, inst_user):
    if inst_user.is_crif_generated == False:
        user_data = User.objects.get(id=inst_user.user.id)
        phone_mod = mods.phone.Phone.objects.get(user=user_data)
        address = mods.address.Address.objects.get(user=user_data)
        general = mods.general.General.objects.get(user=user_data)
        company_details = CompanyDetails.objects.get(user=user_data)
        company_add_details = mods.additional_company_details.AdditionalCompanyDetails.objects.get(user=user_data)
        company_auth_details = mods.additional_company_details.AuthAdditionalCompanyDetails.objects.get(user=user_data)
        tz = pytz.timezone('Asia/Calcutta')
        date = datetime.datetime.now(tz)
        current_date = date.strftime("%d-%m-%Y %H:%M:%S")
        orderid = methods.generate_orderid()
        cin = ''
        llpin = ''

        parent = ET.Element("BBC-COMMERCIAL-REQUEST-FILE")
        tree = ET.ElementTree(parent)
        header = ET.Element("HEADER-SEGMENT")
        pro_type = ET.SubElement(header, "PRODUCT-TYP").text = 'BBC_COMMERCIAL'
        pro_ver = ET.SubElement(header, "PRODUCT-VER").text = '1.0'
        req_mbr = ET.SubElement(header, "REQ-MBR").text = settings.COM_MERCHANT_ID
        sub_mbr_id = ET.SubElement(header, "SUB-MBR-ID").text = settings.COM_CUSTOMER_NAME
        inq_dt_tm = ET.SubElement(header, "INQ-DT-TM").text = current_date
        user_id = ET.SubElement(header, "USER-ID").text = settings.COM_USER_ID
        pwd = ET.SubElement(header, "PWD").text = settings.COM_PASSWORD
        res_frmt = ET.SubElement(header, "RES-FRMT").text = 'XML'
        request_stage = ET.SubElement(header, "REQUEST-STAGE").text = '1'
        commercial = ET.SubElement(header, "COMMERCIAL")
        cir = ET.SubElement(commercial, "CIR").text = 'True'
        score = ET.SubElement(commercial, "SCORE").text = 'True'
        inquiry = ET.Element("INQUIRY")
        app_segment = ET.SubElement(inquiry, "APPLICATION-SEGMENT")
        order_id = ET.SubElement(app_segment, "ORDER-ID").text = orderid
        coom_cir = ET.SubElement(app_segment, "CONSENT-TO-PULL-COMM-CIR").text = 'Y'
        auth_by = ET.SubElement(app_segment, "AUTHORIZATION-BY-ENTITY").text = 'Y'
        report_flag = ET.SubElement(app_segment, "REPORT-FLAG").text = 'Y'
        alert_flag = ET.SubElement(app_segment, "ALERT-FLAG").text = 'Y'
        com_entity_segment = ET.SubElement(inquiry, "COMM-ENTITY-SEGMENT")
        entity_name = ET.SubElement(com_entity_segment, "ENTITY-NAME").text = company_details.org_name
        legal_constitution = ET.SubElement(com_entity_segment, "LEGAL-CONSTITUTION").text = '11'
        email = ET.SubElement(com_entity_segment, "EMAIL").text = user_data.email
        ids = ET.SubElement(com_entity_segment, "IDS")
        id = ET.SubElement(ids, "ID")
        id_type = ET.SubElement(id, "TYPE").text = 'ID07'
        value = ET.SubElement(id, "VALUE").text = company_add_details.pan_number
        id1 = ET.SubElement(ids, "ID")
        if len(company_details.company_register_no) > 7:
            id_type = ET.SubElement(id1, "TYPE").text = 'ID08'
            value = ET.SubElement(id1, "VALUE").text = company_details.company_register_no
        else:
            id_type = ET.SubElement(id1, "TYPE").text = 'ID11'
            value = ET.SubElement(id1, "VALUE").text = company_details.company_register_no
        if company_add_details.gst_number:
            id2 = ET.SubElement(ids, "ID")
            id_type = ET.SubElement(id2, "TYPE").text = 'ID10'
            value = ET.SubElement(id2, "VALUE").text = company_add_details.gst_number
        phones = ET.SubElement(com_entity_segment, "PHONES")
        phone = ET.SubElement(phones, "PHONE")
        phone_type = ET.SubElement(phone, "TELE-NO-TYPE").text = 'P01'
        phone_no = ET.SubElement(phone, "TELE-NO").text = address.tel_number # '4562469914'
        com_address_segment = ET.SubElement(inquiry, "COMM-ADDRESS-SEGMENT")
        office_address = ET.SubElement(com_address_segment, "ADDRESS")
        id_type = ET.SubElement(office_address, "TYPE").text = 'D13'
        address_line = ET.SubElement(office_address,
                                     "ADDRESS-LINE").text = address.unit_number + ' ' + address.street_address
        city = ET.SubElement(office_address, "CITY").text = address.city
        state = ''
        for k in enums.IndiaStateCodes:
            if enums.IndiaStateCodes[k] == enums.IndiaStates(address.state).name:
                state = k
        state = ET.SubElement(office_address, "STATE").text = state
        pin = ET.SubElement(office_address, "PIN").text = address.pin_code
        indv_assoc_segment = ET.SubElement(inquiry, "INDV-ASSOCIATION-SEGMENT")
        indv_name = ET.SubElement(indv_assoc_segment, "INDV-NAME")
        fname = ET.SubElement(indv_name, "FIRST-NAME").text = user_data.first_name
        mname = ET.SubElement(indv_name, "MIDDLE-NAME").text = general.father_husband_no
        lname = ET.SubElement(indv_name, "LAST-NAME").text = user_data.last_name
        if company_auth_details.din_number:
            assoc_entity = ET.SubElement(indv_assoc_segment, "ASSOCIATION-WITH-ENTITY").text = '001'
        else:
            assoc_entity = ET.SubElement(indv_assoc_segment, "ASSOCIATION-WITH-ENTITY").text = '002'
        ids = ET.SubElement(indv_assoc_segment, "IDS")
        id_indv = ET.SubElement(ids, "ID")
        id_type = ET.SubElement(id_indv, "TYPE").text = 'ID07'
        value = ET.SubElement(id_indv, "VALUE").text = company_auth_details.pan_number
        if assoc_entity == '001':
            id_indv1 = ET.SubElement(ids, "ID")
            id_type = ET.SubElement(id_indv1, "TYPE").text = 'ID09'
            value = ET.SubElement(id_indv1, "VALUE").text = company_auth_details.din_number
        phones = ET.SubElement(indv_assoc_segment, "PHONES")
        phone = ET.SubElement(phones, "PHONE")
        phone_type = ET.SubElement(phone, "TELE-NO-TYPE").text = 'P03'
        phone_no = ET.SubElement(phone, "TELE-NO").text = phone_mod.phone_number
        indv_address_segment = ET.SubElement(inquiry, "INDV-ADDRESS-SEGMENT")
        indv_address = ET.SubElement(indv_address_segment, "ADDRESS")
        id_type = ET.SubElement(indv_address, "TYPE").text = 'D01'
        address_line = ET.SubElement(indv_address,
                                     "ADDRESS-LINE").text = address.unit_number + ' ' + address.street_address
        city = ET.SubElement(indv_address, "CITY").text = address.city
        state = ''
        for k in enums.IndiaStateCodes:
            if enums.IndiaStateCodes[k] == enums.IndiaStates(address.state).name:
                state = k
        state = ET.SubElement(indv_address, "STATE").text = state
        pin = ET.SubElement(indv_address, "PIN").text = address.pin_code

        parent.append(header)
        parent.append(inquiry)
        tree.write("test.xml")
        print(" stage 1 order id ************************",orderid)
        file_path = settings.BASE_DIR + '/test.xml'
        headers = {
            'isEncrypted': 'N',
            'Mbrid': settings.COM_MERCHANT_ID,
            'productType': 'BBC_COMMERCIAL',
            'productVersion': '1.0',
            'Content-type': 'application/xml'
        }
        with open(file_path) as f:
            # response1 = requests.post('https://test.crifhighmark.com/BBC/comm/1', data=f.read(), headers=headers)
            response1 = requests.post(settings.CRIF_COM_STAG_API_1, data=f.read(), headers=headers)
            data_dict = xmltodict.parse(response1.text)
            json_data = json.dumps(data_dict)
            parsedData = json.loads(json_data)
            reportid =  parsedData['BBC-COMMERCIAL-RESPONSE-FILE']['COMMERCIAL-CREDIT-REPORT']['INQUIRY-STATUS']['INQUIRY'][
                    'REPORT-ID']
            print(" parsedData stage 1 ************************", parsedData )
            print(" report id stage 1 ************************", reportid )

        return reportid, orderid, inst_user

        # stage-2 api


def crif_institution_stage_2(request, reportid, orderid, user):
    tz = pytz.timezone('Asia/Calcutta')
    date = datetime.datetime.now(tz)
    current_date = date.strftime("%d-%m-%Y %H:%M:%S")

    parent2 = ET.Element("BBC-COMMERCIAL-REQUEST-FILE")
    tree = ET.ElementTree(parent2)
    header2 = ET.Element("HEADER-SEGMENT")
    pro_type = ET.SubElement(header2, "PRODUCT-TYP").text = 'BBC_COMMERCIAL'
    pro_ver = ET.SubElement(header2, "PRODUCT-VER").text = '1.0'
    req_mbr = ET.SubElement(header2, "REQ-MBR").text = settings.COM_MERCHANT_ID
    sub_mbr_id = ET.SubElement(header2, "SUB-MBR-ID").text = settings.COM_CUSTOMER_NAME
    inq_dt_tm = ET.SubElement(header2, "INQ-DT-TM").text = current_date
    user_id = ET.SubElement(header2, "USER-ID").text = settings.COM_USER_ID
    pwd = ET.SubElement(header2, "PWD").text = settings.COM_PASSWORD
    res_frmt = ET.SubElement(header2, "RES-FRMT").text = 'XML'
    request_stage = ET.SubElement(header2, "REQUEST-STAGE").text = '2'
    commercial = ET.SubElement(header2, "COMMERCIAL")
    cir = ET.SubElement(commercial, "CIR").text = 'TRUE'
    score = ET.SubElement(commercial, "SCORE").text = 'TRUE'
    consumer = ET.SubElement(header2, "CONSUMER")
    cir = ET.SubElement(consumer, "CIR").text = 'TRUE'
    score = ET.SubElement(consumer, "SCORE").text = 'TRUE'
    inquiry2 = ET.Element("INQUIRY")
    app_segment = ET.SubElement(inquiry2, "APPLICATION-SEGMENT")
    order_id = ET.SubElement(app_segment, "ORDER-ID").text = orderid
    coom_cir = ET.SubElement(app_segment, "CONSENT-TO-PULL-COMM-CIR").text = 'Y'
    auth_by = ET.SubElement(app_segment, "AUTHORIZATION-BY-ENTITY").text = 'Y'
    report_flag = ET.SubElement(app_segment, "REPORT-FLAG").text = 'Y'
    alert_flag = ET.SubElement(app_segment, "ALERT-FLAG").text = 'Y'
    report_id = ET.SubElement(app_segment, "REPORT-ID").text = reportid
    user_otp = ET.SubElement(app_segment, "USER-OTP").text = 'NULL'

    print("---------------------------------------------------------------")
    print('stage 2 date ', current_date)
    print('stage 2 ', reportid)
    print('stage 2 ',orderid)
    print("---------------------------------------------------------------")
    parent2.append(header2)
    parent2.append(inquiry2)
    tree.write("test2.xml")
    headers2 = {
        'isEncrypted': 'N',
        'Mbrid': settings.COM_MERCHANT_ID,
        'productType': 'BBC_COMMERCIAL',
        'productVersion': '1.0',
        'Content-type': 'application/xml'
    }
    file_path2 = settings.BASE_DIR + '/test2.xml'
    with open(file_path2) as f:
        data = f.read()
    # response2 = requests.post('https://test.crifhighmark.com/BBC/comm/2', data=data, headers=headers2)
    response2 = requests.post(settings.CRIF_COM_STAG_API_2, data=data, headers=headers2)

    print(" response2.text stage 2 ************************", response2.text)
    print(" report id stage 2 ************************", reportid)

def crif_institution_stage_3(request, reportid, orderid, user):
    tz = pytz.timezone('Asia/Calcutta')
    date = datetime.datetime.now(tz)
    current_date = date.strftime("%d-%m-%Y %H:%M:%S")

    parent3 = ET.Element("BBC-COMMERCIAL-REQUEST-FILE")
    tree = ET.ElementTree(parent3)
    header3 = ET.Element("HEADER-SEGMENT")
    pro_type = ET.SubElement(header3, "PRODUCT-TYP").text = 'BBC_COMMERCIAL'
    pro_ver = ET.SubElement(header3, "PRODUCT-VER").text = '1.0'
    req_mbr = ET.SubElement(header3, "REQ-MBR").text = settings.COM_MERCHANT_ID
    sub_mbr_id = ET.SubElement(header3, "SUB-MBR-ID").text = settings.COM_CUSTOMER_NAME
    inq_dt_tm = ET.SubElement(header3, "INQ-DT-TM").text = current_date
    user_id = ET.SubElement(header3, "USER-ID").text = settings.COM_USER_ID
    pwd = ET.SubElement(header3, "PWD").text = settings.COM_PASSWORD
    res_frmt = ET.SubElement(header3, "RES-FRMT").text = 'XML'
    request_stage = ET.SubElement(header3, "REQUEST-STAGE").text = '3'
    commercial = ET.SubElement(header3, "COMMERCIAL")
    cir = ET.SubElement(commercial, "CIR").text = 'TRUE'
    score = ET.SubElement(commercial, "SCORE").text = 'TRUE'
    consumer = ET.SubElement(header3, "CONSUMER")
    cir = ET.SubElement(consumer, "CIR").text = 'TRUE'
    score = ET.SubElement(consumer, "SCORE").text = 'TRUE'
    inquiry3 = ET.Element("INQUIRY")
    app_segment = ET.SubElement(inquiry3, "APPLICATION-SEGMENT")
    order_id = ET.SubElement(app_segment, "ORDER-ID").text = orderid
    coom_cir = ET.SubElement(app_segment, "CONSENT-TO-PULL-COMM-CIR").text = 'Y'
    auth_by = ET.SubElement(app_segment, "AUTHORIZATION-BY-ENTITY").text = 'Y'
    report_flag = ET.SubElement(app_segment, "REPORT-FLAG").text = 'Y'
    alert_flag = ET.SubElement(app_segment, "ALERT-FLAG").text = 'Y'
    report_id = ET.SubElement(app_segment, "REPORT-ID").text = reportid

    print("---------------------------------------------------------------")
    print('stage 3 date ', current_date)
    print('stage 3 reportid ',reportid)
    print('stage 3 orderid ',orderid)
    print("---------------------------------------------------------------")
    parent3.append(header3)
    parent3.append(inquiry3)
    tree.write("test3.xml")
    headers3 = {
        'isEncrypted': 'N',
        'Mbrid': settings.COM_MERCHANT_ID,
        'productType': 'BBC_COMMERCIAL',
        'productVersion': '1.0',
        'Content-type': 'application/xml'
    }
    file_path3 = settings.BASE_DIR + '/test3.xml'
    with open(file_path3) as f:
        data = f.read()
    # response3 = requests.post('https://test.crifhighmark.com/BBC/comm/3', data=data, headers=headers3)
    response3 = requests.post(settings.CRIF_COM_STAG_API_3, data=data, headers=headers3)
    print('steg 3 responce ', response3)

    if response3.status_code == 200:
        user.is_crif_generated = True
        user.save()
        user_data = User.objects.get(id=user.user.id)
        data_dict = xmltodict.parse(response3.text)
        json_data = json.dumps(data_dict)
        parsedData = json.loads(json_data)
        report = mods.crif_data.B2CReport.objects.create(
            user=user_data,
            orderid=orderid,
            data=parsedData
        )
        report.save()
        obj = mods.crif_data.B2CReport.objects.get(user=user_data)
        crif_score = 0
        if obj.data['BBC-COMMERCIAL-RESPONSE-FILE']['COMMERCIAL-CREDIT-REPORT']['COMMERCIAL-REPORT']['SCORES']:
            crif_score = obj.data['BBC-COMMERCIAL-RESPONSE-FILE']['COMMERCIAL-CREDIT-REPORT']['COMMERCIAL-REPORT']['SCORES'][
                    'SCORE']['SCORE-VALUE']
        veloce_master = mods.veloce_score_master.VeloceScoreMaster.objects.create(
            user=user_data,
            crif_score=crif_score
        )
        veloce_master.save()

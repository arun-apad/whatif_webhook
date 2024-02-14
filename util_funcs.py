import http.client
import json
import sqlite3
import datetime
import time
from datetime import datetime

headers = {
    'Authorization': 'App bd8212e927694160fd8a3d13738103c7-fe347b7b-9f06-4cd5-b803-cc57b898d507',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'x-agent-id': '6141d3ef-213b-47f0-98e0-e57bb496e0a2'
    }

connection = sqlite3.connect('database.db')
compliance_text = """Please be aware that there are exclusions and conditions applying to your policy. You must comply with them to have the full protection of your policy and provide the right documents in your claims process.
If you are enquiring about trip cancellation or curtailment due to the insolvency of the booking provider, or airline, please contact them in the first instance before submitting a claim. We're unable to assess your claim until you've received a decision from them."""


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def read_latest(request_json):
    conversation_id = request_json["conversationId"]
    conn = get_db_connection()
    posts = conn.execute("SELECT * FROM events where conversation_id = ? ORDER BY incoming_date DESC LIMIT 1", [conversation_id]).fetchall()
    conn.close()
    try:
        return (posts[0][2])
    except IndexError:
        return ("Other")
    

def read_latest_policy(request_json):
    conversation_id = request_json["conversationId"]
    conn = get_db_connection()
    posts = conn.execute("SELECT * FROM events where conversation_id = ? ORDER BY incoming_date DESC LIMIT 1", [conversation_id]).fetchall()
    conn.close()
    return (posts[1][2])

def insert_event(request_json, text):
    conversation_id  = request_json["conversationId"]
    incoming_event = text
    incoming_date = datetime.now()
    outgoing_answer = "Let's start"
    outgoing_date = datetime.now()
    message_id = request_json["id"]
    cur = connection.cursor()

    cur.execute("INSERT INTO events (conversation_id, incoming_event, incoming_date, outgoing_answer, outgoing_date, message_id) VALUES (?, ?, ?, ?, ?, ?)",
                (conversation_id, incoming_event, incoming_date, outgoing_answer, outgoing_date, message_id)
                )
    result = cur.fetchall();
    print("========================================================")
    print(result)
    connection.commit()
    #connection.close()

def to_agent(request_json):
    response = {}
    response['agentId'] = ""
    conn = http.client.HTTPSConnection("qgjr3q.api.infobip.com")
    
    values = json.loads(json.dumps(request_json))
    conversationId = values["conversationId"]
    conn = http.client.HTTPSConnection("qgjr3q.api.infobip.com")
    conid = "/ccaas/1/conversations/"+str(conversationId)
    #conn.request("DELETE", "/ccaas/1/conversations/4cacb59f-5103-426c-a64b-199ae9c9036c/assignee", payload, headers)
    conn.request("DELETE", conid, json.dumps(response), headers)
    res = conn.getresponse()
    data = res.read()

def terminate(request_json):
    response = {}
    
    values = json.loads(json.dumps(request_json))
    conversationId = values["conversationId"]
    response['status'] = "SOLVED"
    
    conn = http.client.HTTPSConnection("qgjr3q.api.infobip.com")
    conid = "/ccaas/1/conversations/"+str(conversationId)
    conn.request("PUT", conid, json.dumps(response), headers)
    res = conn.getresponse()
    data = res.read()
    

    return(data)

def create_text(request_json, contentType, text):
    response = {}
    content = {}
    
    values = json.loads(json.dumps(request_json))
    conversationId = values["conversationId"]
    response['to'] = values["from"]
    response['from'] = values["to"]
    #response['id'] = values["id"]
    response['channel'] = values["channel"]
    #response['direction'] = values["direction"]
    response['contentType'] = contentType
    #response['createdAt'] = values["createdAt"]
    #response['text'] = values['content']['text']
    #content['buttonType'] = "LIVECHAT"
    response['content'] = content
    response['content']['text'] = text
    
    conn = http.client.HTTPSConnection("qgjr3q.api.infobip.com")
    
    conid = "/ccaas/1/conversations/"+str(conversationId)+"/messages"
    conn.request("POST", conid, json.dumps(response), headers)
    res = conn.getresponse()
    data = res.read()
    

    return(data)

def create_button(request_json, contentType, text, textbuttons):
    response = {}
    content = {}
    button = {}

    buttons = []
    for tb in textbuttons:
        d = {}
        d['title'] = tb
        d["type"] = "POSTBACK"
        d["payload"] = "yes"
        buttons.append(d)
        


    values = json.loads(json.dumps(request_json))
    conversationId = values["conversationId"]
    response['to'] = values["from"]
    response['from'] = values["to"]
    #response['id'] = values["id"]
    response['channel'] = values["channel"]
    #response['direction'] = values["direction"]
    response['contentType'] = contentType
    #response['createdAt'] = values["createdAt"]
    #response['text'] = values['content']['text']
    content['buttonType'] = "LIVECHAT"
    response['content'] = content
    button['text'] = text
    response['content']['button'] = button
    response["content"]["button"]["buttonPayloads"]= buttons 
    
    conn = http.client.HTTPSConnection("qgjr3q.api.infobip.com")
    conid = "/ccaas/1/conversations/"+str(conversationId)+"/messages"
    conn.request("POST", conid, json.dumps(response), headers)
    res = conn.getresponse()
    data = res.read()
    

    return(data)



def IsOOH():
    today = datetime.now().strftime('%A')
    hour = datetime.now().hour
    print(today)
    print(hour)
    #hour = 17

    match today:
            case "Monday":
                if hour < 9 or hour >16:
                    return(True)
            case "Tuesday":
                if hour < 9 or hour >16:
                    return(True)   
            case "Wednesday":
                if hour < 9 or hour >16:
                    return(True)
            case "Thursday":
                if hour < 9 or hour >16:
                    return(True)  
            case "Friday":
                if hour < 9 or hour >16:
                    return(True)  
            case "Saturday":
                return(True) 
            case "Sunday":
                return(True)
            case other:
                return(False)

def event(intent, request_json):
    match intent:
        case "Start the chat":
            if IsOOH():
                contentType = "TEXT"
                text = """This live chat is now closed and your message won't be delivered. The live chat is available during UK Office Hours (09:00 to 11:00 and 14:00 to 17:00), Monday - Friday exlcuding Bank Holidays.
If you’re currently abroad and require emergency assistance please call +44 (0) 2038 599 317.
If you would like to submit a new claim, the fastest and easiest way to claim is online on our website, puffin.uk.axa.travel/claim/claim_home. We will guide you through the process step by step."""
                payload1 = create_text(request_json, contentType, text)
                insert_event(request_json, "OOH")
                return [payload1]
            else:
                contentType = "BUTTON"
                textbuttons = ["General Enquiry", "Medical Assistance", "A New Claim", "An Existing Claim"]
                text = "How we can help you today ?  Please select one of the options"
                payload = create_button(request_json, contentType, text, textbuttons)
                insert_event(request_json, intent)
                return [payload]
        case "Medical Assistance":
            contentType = "TEXT"
            text = "We're sorry to hear you are in need of emergency medical assistance, please ring +44 (0) 2038 599 317. Please note, this chat is to answer general enquiries you have about your insurance."
            payload1 = create_text(request_json, contentType, text)
            time.sleep(2)
            contentType = "BUTTON"
            textbuttons = ["General Enquiry", "A New Claim", "An Existing Claim"]
            text = "Can we help you with any other questions today"
            payload = create_button(request_json, contentType, text, textbuttons)
            insert_event(request_json, intent)
            return [payload, payload1]
        case "A New Claim":
            contentType = "TEXT"
            text = "The fastest and easiest way to claim is online on our website, puffin.uk.axa.travel/claim/claim_home. We will guide you through the process step by step. Please note, this chat is to answer general enquiries you have about your insurance."
            payload1 = create_text(request_json, contentType, text)
            time.sleep(2)
            contentType = "BUTTON"
            textbuttons = ["General Enquiry", "Medical Assistance", "An Existing Claim"]
            text = "Can we help you with any other questions today"
            payload = create_button(request_json, contentType, text, textbuttons)
            insert_event(request_json, intent)
            return [payload, payload1]
        case "An Existing Claim":
            contentType = "BUTTON"
            textbuttons = ["Online", "Phone"]
            text = "Please tell us how  you first raised your claim"
            payload = create_button(request_json, contentType, text, textbuttons)
            insert_event(request_json, intent)
            return [payload]
        case "Online":
            contentType = "TEXT"
            text = "If you'd like see the progress on your current claim, or need to upload any previously claimed documents, please log into your account on puffin.uk.axa.travel/claim/claim_home."
            payload1 = create_text(request_json, contentType, text)
            time.sleep(2)
            contentType = "BUTTON"
            textbuttons = ["General Enquiry", "Medical Assistance", "A New Claim"]
            text = "Can we help you with any other questions today"
            payload = create_button(request_json, contentType, text, textbuttons)
            insert_event(request_json, intent)
            return [payload, payload1]
        case "Phone":
            contentType = "TEXT"
            text = "To ask a question about a claim your raised over the phone, you can speak to one of our agents by ringing +44 (0) 2038 599 317."
            payload1 = create_text(request_json, contentType, text)
            time.sleep(2)
            contentType = "BUTTON"
            textbuttons = ["General Enquiry", "Medical Assistance", "A New Claim"]
            text = "Can we help you with any other questions today"
            payload = create_button(request_json, contentType, text, textbuttons)
            insert_event(request_json, intent)
            return [payload, payload1]
        case "General Enquiry":
            contentType = "TEXT"
            text = """Please note that by using this chat, you give AXA Partners consent to process and hold any information supplied by you and/or about you, to handle your enquiry. We may also use this information for quality and training purposes, and to improve our products or services.  
We request that you do not provide us with sensitive or special category data, such as medical or health information, in this chat. If you do input this type of information, one of our agents may ask to speak to you via phone.
For more information about how we process personal data, please see the AXA Partners privacy policy at https://www.axapartners.co.uk/en/privacy-policy"""
            payload1 = create_text(request_json, contentType, text)
            time.sleep(2)
            contentType = "TEXT"
            text = "To help us answer your query quicker, we need some information from you. Please can you tell us your first and last name."
            payload2 = create_text(request_json, contentType, text)
            insert_event(request_json, "name_intent")
            return [payload1, payload2]
        case "start_click_flow":
            contentType = "BUTTON"
            textbuttons = ["Cancellation or Curtailment", "Trip Disruption", "Travel Documents Theft", "Winter Sports", "Other"]
            text = "Thank you, please can you tell us how we can help you"
            payload = create_button(request_json, contentType, text, textbuttons)
            insert_event(request_json, intent)
            return [payload]
        case "Cancellation or Curtailment":
            contentType = "BUTTON"
            textbuttons = ["Medical Incident", "Call as a witness/ Jury Service", "Work or Studies related"]
            text = "Please tell us if it is related to:"
            payload = create_button(request_json, contentType, text, textbuttons)
            insert_event(request_json, intent)
            return [payload]
        case "Medical Incident":
            contentType = "BUTTON"
            textbuttons = ["Illness", "Injury", "Death", "Complication of pregnancy"]
            text = "What best describes your situation?"
            payload = create_button(request_json, contentType, text, textbuttons)
            insert_event(request_json, intent)
            return [payload]
        case "Illness":
            contentType = "TEXT"
            text = """Our policy could provide coverage in the unfortunate event that you, your travel companion, a close relative, or a colleague falls ill and you need to cancel or shorten your trip. We understand the importance of offering support during challenging times. 
If you have already consulted with a doctor and obtained a doctor's notice, kindly follow the provided link to easily upload your documents and initiate the reimbursement process: puffin.uk.axa.travel"""
            payload1 = create_text(request_json, contentType, text)
            time.sleep(2)
            text = compliance_text
            payload2 = create_text(request_json, contentType, text)
            textbuttons = ["Yes", "No"]
            text = """Have we answered your question today?"""
            time.sleep(2)
            contentType = "BUTTON"
            payload3 = create_button(request_json, contentType, text, textbuttons)
            insert_event(request_json, intent)
            return [payload1, payload2, payload3]
        case "Injury":
            contentType = "TEXT"
            text = """ Our policy could provide coverage in the unfortunate event that you, your travel companion, a close relative, or a colleague sustains an injury due to an accident and you need to cancel or shorten your trip. We understand the importance of offering support during challenging times. 
If you have already consulted with a doctor and obtained a doctor's notice, kindly follow the provided link to easily upload your documents and initiate the reimbursement proces: puffin.uk.axa.travel"""
            payload1 = create_text(request_json, contentType, text)
            time.sleep(2)
            text = compliance_text
            payload2 = create_text(request_json, contentType, text)
            textbuttons = ["Yes", "No"]
            text = """Have we answered your question today??"""
            contentType = "BUTTON"
            time.sleep(2)
            payload3 = create_button(request_json, contentType, text, textbuttons)
            insert_event(request_json, intent)
            return [payload1, payload2, payload3]
        case "Death":
            contentType = "TEXT"
            text = """Our policy could provide coverage in the unfortunate event of the death of you, your travel companion, a close relative, or a colleague, and you need to cancel or shorten your trip. We understand the importance of offering support during challenging times. 
If you have obtainted a death certificate, kindly follow the provided link to easily upload your documents and initiate the reimbursement proces: puffin.uk.axa.travel"""
            payload1 = create_text(request_json, contentType, text)
            time.sleep(2)
            text = compliance_text
            payload2 = create_text(request_json, contentType, text)
            textbuttons = ["Yes", "No"]
            text = """Have we answered your question today?"""
            contentType = "BUTTON"
            time.sleep(2)
            payload3 = create_button(request_json, contentType, text, textbuttons)
            insert_event(request_json, intent)
            return [payload1, payload2, payload3]
        case "Complication of pregnancy":
            contentType = "TEXT"
            text = """Our policy could provide coverage in the unfortunate event of pregnancy complications for you, your travel companion, a close relative, or a colleague, and you need to cancel or shorten your trip. We understand the importance of offering support during challenging times. 
If you have already consulted with a doctor and obtained a doctor's notice, kindly follow the provided link to easily upload your documents and initiate the reimbursement proces: puffin.uk.axa.travel"""
            payload1 = create_text(request_json, contentType, text)
            time.sleep(2)
            text = compliance_text
            payload2 = create_text(request_json, contentType, text)
            time.sleep(2)
            textbuttons = ["Yes", "No"]
            text = """Have we answered your question today?"""
            contentType = "BUTTON"
            payload3 = create_button(request_json, contentType, text, textbuttons)
            insert_event(request_json, intent)
            return [payload1, payload2, payload3]
        case "Call as a witness/ Jury Service":
            contentType = "TEXT"
            text = """We understand that jury service attendance or being called as a witness at a Court of Law (other than in an advisory or professional capacity) can happen unexpectedly. That's why our policy provides coverage for you and your travel companions in such situations. We're here to support you through any unforeseen circumstances and ensure that you have a smooth travel experience.
If you have already obtained a confirmation from the Clerk of the Courts office then kindly follow the provided link to easily upload your documents and initiate the reimbursement proces: puffin.uk.axa.travel"""
            payload1 = create_text(request_json, contentType, text)
            time.sleep(2)
            text = compliance_text
            payload2 = create_text(request_json, contentType, text)
            time.sleep(2)
            textbuttons = ["Yes", "No"]
            text = """Have we answered your question today?"""
            contentType = "BUTTON"
            payload3 = create_button(request_json, contentType, text, textbuttons)
            insert_event(request_json, intent)
            return [payload1, payload2, payload3]
        case "Work or Studies related":
            contentType = "BUTTON"
            textbuttons = ["Withdrawn Annual Leave", "Loss of Employment"]
            text = "What best describes your situation?"
            payload = create_button(request_json, contentType, text, textbuttons)
            insert_event(request_json, intent)
            return [payload]
        case "Withdrawn Annual Leave":
            contentType = "TEXT"
            text = """Our policy could provide coverage for cancellation, specifically if the Foreign, Commonwealth & Development Office (FCDO), Ministry of Foreign Affairs (MFA), or another regulatory authority advises against travel to the area you were planning to visit. This coverage applies if the advice is issued after you booked your trip, arranged travel insurance with us, and is not related to a pandemic. We understand the importance of staying informed and prioritising your safety while travelling.
Please follow the provided link to easily upload your documents and initiate the reimbursement proces: puffin.uk.axa.travel"""
            payload1 = create_text(request_json, contentType, text)
            time.sleep(2)
            text = compliance_text
            payload2 = create_text(request_json, contentType, text)
            time.sleep(2)
            textbuttons = ["Yes", "No"]
            text = """Have we answered your question today?"""
            contentType = "BUTTON"
            payload3 = create_button(request_json, contentType, text, textbuttons)
            insert_event(request_json, intent)
            return [payload1, payload2, payload3]
        case "Loss of Employment":
            contentType = "TEXT"
            text = """Our policy could provide coverage in the unfortunate event of redundancy for either yourself or your travel companion. We understand the financial impact and uncertainty that can arise from such situations. Rest assured, we are here to provide support and help alleviate the potential financial burden during this challenging time. 
If you have already obtained a confirmation from your employer/your travelling companion's employer of reduncancy stating the period of employementor leave cancelled, then kindly follow the provided link to easily upload your documents and initiate the reimbursement proces: puffin.uk.axa.travel"""
            payload1 = create_text(request_json, contentType, text)
            time.sleep(2)
            text = compliance_text
            payload2 = create_text(request_json, contentType, text)
            time.sleep(2)
            textbuttons = ["Yes", "No"]
            text = """Have we answered your question today?"""
            contentType = "BUTTON"
            payload3 = create_button(request_json, contentType, text, textbuttons)
            insert_event(request_json, intent)
            return [payload1, payload2, payload3]
        case "Trip Disruption":
            contentType = "BUTTON"
            textbuttons = ["Restriction or denial of entry by regulators", "Compulsory quarantaine"]
            text = "Please tell us if it is related to:"
            payload = create_button(request_json, contentType, text, textbuttons)
            insert_event(request_json, intent)
            return [payload]
        case "Restriction or denial of entry by regulators":
            contentType = "TEXT"
            text = """Our policy could provide coverage for cancellation, specifically if the Foreign, Commonwealth & Development Office (FCDO), Ministry of Foreign Affairs (MFA), or another regulatory authority advises against travel to the area you were planning to visit. This coverage applies if the advice is issued after you booked your trip, arranged travel insurance with us, and is not related to a pandemic. We understand the importance of staying informed and prioritising your safety while travelling.
Please follow the provided link to easily upload your documents and initiate the reimbursement proces: puffin.uk.axa.travel"""
            payload1 = create_text(request_json, contentType, text)
            time.sleep(2)
            text = compliance_text
            payload2 = create_text(request_json, contentType, text)
            time.sleep(2)
            textbuttons = ["Yes", "No"]
            text = """Have we answered your questions today?"""
            contentType = "BUTTON"
            payload3 = create_button(request_json, contentType, text, textbuttons)
            insert_event(request_json, intent)
            return [payload1, payload2, payload3]
        case "Compulsory quarantaine":
            contentType = "TEXT"
            text = """Our policy could provide coverage for cancellation or cutting short a trip due to various circumstances, including compulsory personal quarantine. We understand that unexpected circumstances can arise, and we are committed to providing coverage and assistance to our you during these situations.
Please follow the provided link to easily upload your documents and initiate the reimbursement process: puffin.uk.axa.travel"""
            payload1 = create_text(request_json, contentType, text)
            time.sleep(2)
            text = compliance_text
            payload2 = create_text(request_json, contentType, text)
            time.sleep(2)
            textbuttons = ["Yes", "No"]
            text = """Have we answered your question today?"""
            contentType = "BUTTON"
            payload3 = create_button(request_json, contentType, text, textbuttons)
            insert_event(request_json, intent)
            return [payload1, payload2, payload3]
        case "Travel Documents Theft":
            contentType = "TEXT"
            text = """Our policy could provide coverage for the cancellation or cutting short of a trip if your passport and/or visa are stolen within 72 hours before your scheduled departure. This coverage applies if you are traveling outside of your home area or during your trip and are unable to continue your journey as a result. We understand the inconvenience and potential disruption caused by such incidents, and our policy aims to offer support and assistance during these circumstances.
If you have already obtained an original Police report including crime reference number or incident report, within 24 hours of the incident or as soon as possible after that, then kindly follow the provided link to easily upload your documents and initiate the reimbursement process: puffin.uk.axa.travel"""
            payload1 = create_text(request_json, contentType, text)
            time.sleep(2)
            text = compliance_text
            payload2 = create_text(request_json, contentType, text)
            time.sleep(2)
            textbuttons = ["Yes", "No"]
            text = """Have we answered your question today?"""
            contentType = "BUTTON"
            payload3 = create_button(request_json, contentType, text, textbuttons)
            insert_event(request_json, intent)
            return [payload1, payload2, payload3]
        case "Winter Sports":
            contentType = "BUTTON"
            textbuttons = ["Avalanche, Landslide Closure or catastrophe", "Piste Closure", "Equipment"]
            text = "Please tell us if it is related to:"
            payload = create_button(request_json, contentType, text, textbuttons)
            insert_event(request_json, intent)
            return [payload]
        case "Avalanche, Landslide Closure or catastrophe":
            contentType = "TEXT"
            text = """Should you require coverage for cancellation or cutting short of your trip related to winter sports, it is important to ensure that you have paid the premium for the additional cover. Please review the sports and other activities section of the policy wording to confirm that the activities you plan to participate in as part of your winter sports trip are covered.
If you have purchased an annual multi-trip policy, coverage for winter sports activity is limited to either 17 or 24 days during the insurance period. The specific limit applicable to your policy will be displayed in your policy schedule.
This applies in the event that skiing facilities in your resource (excluding cross-country skiing) are closed due to factors such as an avalanche. 
Please follow the provided link to easily upload your documents and initiate the reimbursement process: puffin.uk.axa.travel"""
            payload1 = create_text(request_json, contentType, text)
            time.sleep(2)
            text = compliance_text
            payload2 = create_text(request_json, contentType, text)
            time.sleep(2)
            textbuttons = ["Yes", "No"]
            text = """Have we answered your question today?"""
            contentType = "BUTTON"
            payload3 = create_button(request_json, contentType, text, textbuttons)
            insert_event(request_json, intent)
            return [payload1, payload2, payload3]
        case "Piste Closure":
            contentType = "BUTTON"
            textbuttons = ["Due to adverse weather conditions", "Due to excess or insufficient snow"]
            text = "What best describes your situation?"
            payload = create_button(request_json, contentType, text, textbuttons)
            insert_event(request_json, intent)
            return [payload]
        case "Due to adverse weather conditions":
            contentType = "TEXT"
            text = """Should you require coverage for cancellation or cutting short of your trip related to winter sports, it is important to ensure that you have paid the premium for the additional cover. Please review the sports and other activities section of the policy wording to confirm that the activities you plan to participate in as part of your winter sports trip are covered.
If you have purchased an annual multi-trip policy, coverage for winter sports activity is limited to either 17 or 24 days during the insurance period. The specific limit applicable to your policy will be displayed in your policy schedule.
This applies in the event that skiing facilities in your resource (excluding cross-country skiing) are closed due to factors such as an avalanche. 
Please follow the provided link to easily upload your documents and initiate the reimbursement process: puffin.uk.axa.travel"""
            payload1 = create_text(request_json, contentType, text)
            time.sleep(2)
            text = compliance_text
            payload2 = create_text(request_json, contentType, text)
            time.sleep(2)
            textbuttons = ["Yes", "No"]
            text = """Have we answered your question today?"""
            contentType = "BUTTON"
            payload3 = create_button(request_json, contentType, text, textbuttons)
            insert_event(request_json, intent)
            return [payload1, payload2, payload3]
        case "Due to excess or insufficient snow":
            contentType = "TEXT"
            text = """Should you require coverage for cancellation or cutting short of your trip related to winter sports, it is important to ensure that you have paid the premium for the additional cover. Please review the sports and other activities section of the policy wording to confirm that the activities you plan to participate in as part of your winter sports trip are covered.
If you have purchased an annual multi-trip policy, coverage for winter sports activity is limited to either 17 or 24 days during the insurance period. The specific limit applicable to your policy will be displayed in your policy schedule.
This applies in the event that skiing facilities in your resource (excluding cross-country skiing) are closed due to factors such as an avalanche. 
Please follow the provided link to easily upload your documents and initiate the reimbursement process:  puffin.uk.axa.travel"""
            payload1 = create_text(request_json, contentType, text)
            time.sleep(2)
            text = compliance_text
            payload2 = create_text(request_json, contentType, text)
            time.sleep(2)
            textbuttons = ["Yes", "No"]
            text = """Have we answered your question today?"""
            contentType = "BUTTON"
            payload3 = create_button(request_json, contentType, text, textbuttons)
            insert_event(request_json, intent)
            return [payload1, payload2, payload3]
        case "Equipment":
            contentType = "BUTTON"
            textbuttons = ["Loss", "Damage", "Theft"]
            text = "Please tell us if it is related to:"
            payload = create_button(request_json, contentType, text, textbuttons)
            insert_event(request_json, intent)
            return [payload]
        case "Loss":
            contentType = "TEXT"
            text = """Our policy could provide coverage for the following scenarios:
a) Accidental loss to your personal ski equipment is included. However, please be aware that coverage for hired ski equipment is subject to reduction as outlined in the Table of Benefits. Additionally, there is a specified maximum limit for each individual item, pair, or set of items, as detailed in the Table of Benefits under the single article limit.
b) In the event of loss to your owned ski equipment, including temporary loss during transit exceeding 24 hours, we will cover the expenses associated with hiring replacement ski equipment.
It is crucial to thoroughly review the policy wording to gain a comprehensive understanding of the coverage, taking note of any relevant exclusions or limitations. 
We understand the importance of offering support during challenging times. If you have already filed a loss report, kindly follow the provided link to easily upload your documents and initiate the reimbursement process: puffin.uk.axa.travel"""
            payload1 = create_text(request_json, contentType, text)
            time.sleep(2)
            text = compliance_text
            payload2 = create_text(request_json, contentType, text)
            time.sleep(2)
            textbuttons = ["Yes", "No"]
            text = """Have we answered your question today?"""
            contentType = "BUTTON"
            payload3 = create_button(request_json, contentType, text, textbuttons)
            insert_event(request_json, intent)
            return [payload1, payload2, payload3]
        case "Damage":
            contentType = "TEXT"
            text = """Our policy could provide coverage for the following scenarios:
a) Accidental damage to your personal ski equipment is included. However, please be aware that coverage for hired ski equipment is subject to reduction as outlined in the Table of Benefits. Additionally, there is a specified maximum limit for each individual item, pair, or set of items, as detailed in the Table of Benefits under the single article limit.
b) In the event of  damage to your owned ski equipment we will cover the expenses associated with hiring replacement ski equipment.
It is crucial to thoroughly review the policy wording to gain a comprehensive understanding of the coverage, taking note of any relevant exclusions or limitations. You can find your policy wording here on page XX: LINK POLICY (alternative: You can find your policy wording in your Puffin E-Mail or download here: DOWNLOAD)
We understand the importance of offering support during challenging times. If you have already filed a loss report, kindly follow the provided link to easily upload your documents and initiate the reimbursement process: puffin.uk.axa.travel"""
            payload1 = create_text(request_json, contentType, text)
            time.sleep(2)
            text = compliance_text
            payload2 = create_text(request_json, contentType, text)
            time.sleep(2)
            textbuttons = ["Yes", "No"]
            text = """Have we answered your question today?"""
            contentType = "BUTTON"
            payload3 = create_button(request_json, contentType, text, textbuttons)
            insert_event(request_json, intent)
            return [payload1, payload2, payload3]
        case "Theft":
            contentType = "TEXT"
            text = """Our policy offers coverage for the following scenarios:
a) Theft of your personal ski equipment is included. However, please be aware that coverage for hired ski equipment is subject to reduction as outlined in the Table of Benefits. Additionally, there is a specified maximum limit for each individual item, pair, or set of items, as detailed in the Table of Benefits under the single article limit.
b) In the event  theft to your owned ski equipment we will cover the expenses associated with hiring replacement ski equipment.
It is crucial to thoroughly review the policy wording to gain a comprehensive understanding of the coverage, taking note of any relevant exclusions or limitations. 
We understand the importance of offering support during challenging times. If you have already filed a loss report, kindly follow the provided link to easily upload your documents and initiate the reimbursement process: puffin.uk.axa.travel"""
            payload1 = create_text(request_json, contentType, text)
            time.sleep(2)
            text = compliance_text
            payload2 = create_text(request_json, contentType, text)
            time.sleep(2)
            textbuttons = ["Yes", "No"]
            text = """Have we answered your question today?"""
            contentType = "BUTTON"
            payload3 = create_button(request_json, contentType, text, textbuttons)
            insert_event(request_json, intent)
            return [payload1, payload2, payload3]
        case "Other":
            contentType = "TEXT"
            text = "Please can you let us know what your general enquiry is about?"
            payload = create_text(request_json, contentType, text)
            insert_event(request_json, "Other")
            return [payload]
        case "free_text":
                #Identify intent
                contentType = "TEXT"
                text = "Checking for intents via AXABOT Integration"
                payload = create_text(request_json, contentType, text)
                payload1 = to_agent(request_json)
                insert_event(request_json, intent)
                return [payload, payload1]
        case "Yes":
            contentType = "TEXT"
            text = "Thank you for your time today. Please kindly complete our customer survey, it would be much appreciated."
            payload1 = create_text(request_json, contentType, text)
            payload2 = terminate(request_json)
            insert_event(request_json, intent)
            return [payload1, payload2]
        case "No":
            contentType = "TEXT"
            text = "Thank you for your feedback. To help with your question, we are now connecting you with an agent"
            payload = create_text(request_json, contentType, text)
            payload = to_agent(request_json)
            insert_event(request_json, intent)
            return [payload]
        case _:
            if IsOOH():
                contentType = "TEXT"
                text = """This live chat is now closed and your message won't be delivered. The live chat is available during UK Office Hours (09:00 to 11:00 and 14:00 to 17:00), Monday - Friday exlcuding Bank Holidays.
If you’re currently abroad and require emergency assistance please call +44 (0) 2038 599 317.
If you would like to submit a new claim, the fastest and easiest way to claim is online on our website, puffin.uk.axa.travel/claim/claim_home. We will guide you through the process step by step."""
                payload1 = create_text(request_json, contentType, text)
                insert_event(request_json, "OOH")
                return [payload1]
            
            print(read_latest(request_json)+str("+++++++"))

            
            
            if read_latest(request_json) == "name_intent":
                contentType = "TEXT"
                text = "Thank you, please can you tell us your policy number. This should be exactly how it appears on your policy documentation."
                payload = create_text(request_json, contentType, text)
                insert_event(request_json, "policy_intent")
                return [payload]

            if read_latest(request_json) == "policy_intent":
                event("start_click_flow", request_json)
                insert_event(request_json, "start_click_flow")
                return [payload]
            
            if read_latest(request_json) == "Other":
                insert_event(request_json, "free_text")
                event("free_text", request_json)
                #Identify intent
                contentType = "TEXT"
                text = "AXABOT Integration"
                payload = create_text(request_json, contentType, text)
                payload1 = to_agent(request_json)
                return [payload, payload1]
            
            
            
            contentType = "TEXT"
            text = "Thank you for your input. To help with your question, we are now connecting you with an agent"
            payload = create_text(request_json, contentType, text)
            payload = to_agent(request_json)
            insert_event(request_json, intent)
            return [payload]
        


#print(event("Start the chat", request_json))







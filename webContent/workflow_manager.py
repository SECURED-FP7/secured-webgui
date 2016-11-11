#
# The Offline workflow manager (WFM)
# 
# Dependencies: pip install json2xml dicttoxml termcolor
#
# Formal usage: ./workflow_manager.py <username> <password/token> <upr_url> <spm_url> <psar_url>
# Example usage: ./workflow_manager.py adrian badpassword http://195.235.93.146:8081 130.192.225.109 http://195.235.93.146:8080

import json
import base64
import requests
import dicttoxml
import upr_client  # SECURED component
import psarClient  # SECURED component
import workflow_manager  # SECURED component
import xml.etree.ElementTree as ET
from sys import argv
from time import sleep
from termcolor import colored
from lxml import etree, objectify
from lxml.etree import XMLSyntaxError


class WorkflowManager(object):
    DEBUG = True

    def dbprint(self, string):
        if self.DEBUG == True:
            print string

    # Get the right PSA for the MSPL requirements
    def get_psa_assoc(mspl):
        f = open('xmlSchema/PSA_Review.xml', 'r')
        psa_xml = f.read()
        f.close()
        mspl_capabilities = []
        tree = ET.fromstring(mspl)
        root = tree
        for child in root:
            for a in child:
                if (str(a.tag).endswith("capability")):
                    for b in a:
                        mspl_capabilities.append(b.text)

        tree = ET.fromstring(psa_xml)
        root = tree
        for child in root:
            for a in child:
                psa_name = a.attrib['name']
                for b in a:
                    if str(b.tag).endswith("capability"):
                        psa_capabilities = []
                        right_psa = False
                        for c in b:
                            if str(c.tag).endswith("capability_list"):
                                psa_capabilities.append(c.text)
                        for mspl_cap in mspl_capabilities:
                            if mspl_cap in psa_capabilities:
                                right_psa = True
                            else:
                                right_psa = False
                        if right_psa == True:
                            return str(psa_name)
        return None

    # Extract the capabilities from an MSPL file and return as a list
    def get_capability_from_mspl(self, mspl):
        capabilities = ""
        tree = ET.fromstring(mspl)
        root = tree
        for child in root:
            for a in child:
                if (str(a.tag).endswith("capability")):
                    for b in a:
                        print "Discovered capability: " + str(b.text)
                        capabilities = capabilities + str(b.text)
        return capabilities

    def get_subject_xml_file(self, upr_url):
        upr = upr_client.UPRClient(str(upr_url))
        r = upr.get_user_list()
        if r.status_code != 200:
            raise Exception("ERROR: Could not contact the UPR")
        users = r.json()

        output = "<?xml version='1.0' encoding='UTF-8'?>"
        output += """<tns:associationList xmlns:tns='http://www.example.org/AssociationList'
            xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' 
            xsi:schemaLocation='http://www.example.org/AssociationList  
            ../../java/schema/AssociationList_Schema.xsd '>"""

        for user in users:
            output += "<tns:associations Name='" + str(
                    user['user_id']) + "'><tns:IP ip_value='0.0.0.0/0.0.0.0'/></tns:associations>"

        output += "</tns:associationList>"
        return output

    def get_market_psa_xml(self, user, psar_url):
        # Why is this one line? His majesty, the SPM, gets very unhappy about whitespace. TODO: clean this up
        xml = """<?xml version="1.0" encoding="UTF-8"?><tns:Mapping xmlns:tns="http://www.example.org/Refinement_Schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.example.org/Refinement_Schema Refinement_Schema.xsd ">"""

        psar = psarClient.Client(str(psar_url))
        print "INFO: This normal user will have access to the full PSA catalogue"
        print str(psar_url)
        r = psar.get_image_list(is_generic=False)
        if r.status_code != 200:
            print "ERROR get_market_psa_xml: OH NO. When getting PSAs, the PSAR returned " + str(r.status_code)
            raise Exception('No PSAs could be found')
        psa_list = r.json()
        # Where "psa" is the PSA_ID
        xml += "<tns:psa_list>"
        for psa in psa_list:

            r = psar.get_psa_capabilities(psa['psa_id'])
            if r.status_code == 200:
                xml += '<tns:psa  name="' + psa['psa_id'] + '">'
                xml += '<tns:PSA_info />'
                xml += '<tns:PSA_characteristic cost="' + str(psa['cost']) + '" latency="' + \
                   str(psa['latency']) + '" rating="' + str(psa['rating']) + '" />'
 
                cap_list = r.json()['capabilities']
                xml += '<tns:capability>'
                for c in cap_list:
                    xml += '<tns:capability_list>' + c + '</tns:capability_list>'
                xml += '</tns:capability>'
                xml += '</tns:psa>'
            else:
                print colored(str(r.status_code) + " NO CAPABILITIES FOUND FOR PSA: " + str(psa), 'red')
                
        xml += '</tns:psa_list></tns:Mapping>'
        return xml

    # Should collect slightly different input depending on if HSPL is given or an SG
    def collectInput(self, refinement_type, hspl_xml, user_sg, user_psa_xml, psa_market_xml,
                     subject_xml, content_xml, target_xml, opt_profile_string, max_evals):
        if user_sg == None:
            print "ERROR: No service graph produced"
            raise AssertionError

        data = {}
        data['refinement_type'] = str(refinement_type)
        data['hspl_mspl'] = str(hspl_xml)
        print str(hspl_xml)
        data['sPSA_SG'] = str(user_sg)
        data['user_PSA'] = str(user_psa_xml)
        data['market_PSA'] = str(psa_market_xml)
        data['subject_string'] = str(subject_xml)
        data['content_string'] = str(content_xml)
        data['target_string'] = str(target_xml)
        data['optimizationType_string'] = str(opt_profile_string)
        data['maxEvaluationsNo_string'] = str(max_evals)
        parent_json = {}
        parent_json['input'] = data
        json_data = json.dumps(parent_json)

        # Perform santisation to keep the SPM happy
        json_data = json_data.replace("\\n", "")
        json_data = json_data.replace("\\r", "")
        json_data = json_data.replace("\\t", "")
        json_data = json_data.replace("\\/", "")
        return json_data

    # Takes JSON and returns as an XML
    def convertToXML(data):
        obj = json.loads(data)
        xml = dicttoxml.dicttoxml(obj)
        return xml

    # This should only be used by users of type NORMAL
    # Returns an XML string
    def convertPSAlist_normal(self, userID, upr_url, psar_url):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
            <tns:Mapping xmlns:tns="http://www.example.org/Refinement_Schema" 
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
            xsi:schemaLocation="http://www.example.org/Refinement_Schema Refinement_Schema.xsd ">"""

        psa_list = []
        psar = psarClient.Client(str(psar_url))
        upr = upr_client.UPRClient(str(upr_url))
        r = upr.get_user_groups(userID)
        data = r.json()
        print "\n\n"
        userGroups = r.json()
        #self.dbprint("DEBUG: Here are the groups belonging to " + str(userID) + ": " + str(userGroups))
        for g in userGroups:
            print "Finding PSAs for group " + str(g)
            r = upr.get_group_psa(g['group'])
            if r.status_code != 200:
                print "convertPSAlist: OH NO. When getting Group PSAs the UPR returned " + str(r.status_code)
            else:
                data = r.json()
                print str(r.json())
                for psa in data:
                    psa_list.append(str(psa['psa_id']))

        # Debug function
        print "Debug: Here are the PSAs of the group: "
        for x in psa_list:
            print "     " + str(x) + " "

        # The default for a normal user is to get the full PSAs from the PSA repository
        # If the UPR group specifies a list of PSAs then that will override the following condition
        if len(psa_list) == 0:
            print "INFO: This normal user will have access to the full PSA catalogue"
            r = psar.get_image_list(is_generic=False)
            if r.status_code != 200:
                print "ERROR convertPSAlist: OH NO. When getting PSAs, the PSAR returned " + str(r.status_code)
                raise Exception('No PSAs could be found')
            data = r.json()
            for psa in data:
                psa_list.append(str(psa['psa_id']))
            print "INFO: There are " + str(len(psa_list)) + " PSAs in the PSAR"

        xml += '<tns:psa_list>'

        # Where "psa" is the PSA_ID
        for psa in psa_list:
            par = psar.get_psa_opt_par(psa)
            par_data = psar.get_image_list(id=psa)

            if par_data.status_code != 200:
                print par_data.status_code
                print "ERROR: No OPTIMISATION PROFILE FOUND FOR PSA: " + str(psa)
                return

            if len(par_data.json()) == 0:
                print colored("ERROR: PSA not found: " + str(psa),'red')
                return

            par = par_data.json()[0] # PSA ID should be unique
            latency = par['rating']

            r = psar.get_psa_capabilities(psa)
            if r.status_code == 200:
                xml += '<tns:psa  name="' + psa + '">'
                xml += '<tns:PSA_info />'
                xml += '<tns:PSA_characteristic cost="' + str(par['cost']) + '" latency="' + \
                   str(par['latency']) + '" rating="' + str(par['rating']) + '" />'
 
                cap_list = r.json()['capabilities']
                xml += '<tns:capability>'
                for c in cap_list:
                    xml += '<tns:capability_list>' + c + '</tns:capability_list>'
                xml += '</tns:capability>'
                xml += '</tns:psa>'
            else:
                print colored(str(r.status_code) + " NO CAPABILITIES FOUND FOR PSA: " + str(psa), 'red')
                

        xml += '</tns:psa_list></tns:Mapping>'
        return xml

    # This function concerns the SG definition and is used only
    # for the expert and enthusiastic users, while for the normal
    # user we have not the SG but only a list of PSAs (the new function).
    # Result returns an XML...
    # TODO: Rename this function to something more sensible
    # New function developed by Fulvio Valenza
    def convertSG(self, psa_list_json, mspl_psa_assoc, psar_url):
        output = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
		        <tns:Mapping xmlns:tns=\"http://www.example.org/Refinement_Schema\" 
		                     xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" 
		                     xsi:schemaLocation=\"http://www.example.org/Refinement_Schema\">
		                     <tns:service_graph>"""
        max_number = len(psa_list_json)

        psar = psarClient.Client(str(psar_url))

        i = 0
        for psa in psa_list_json:
            mspl_id = []
            r = psar.get_image_list(id=psa['psa_id'])
            if r.status_code != 200:
                print "ERROR getting PSA information: HTTP " + str(r.status_code)
                continue

            try:
                thejson = r.json()[0]
                generic = thejson['is_generic']
                psa_id = thejson['psa_id']
                order = psa['running_order'] # TODO: need to use this as the serviceID
            except IndexError:
                print "ERROR!!!: This PSA does not exist: " + str(psa['psa_id'])
                continue
            
            if generic == True:
                print "Generic"
                output += "<tns:service serviceID=\"id" + str(i) + "\" "

                for a in mspl_psa_assoc:
                    if a['psa_id'] == psa_id:
                        output += ' MSPL_ID="' + str(a['mspl']) + "\""

                output += ">"

                capability_list = psar.get_psa_capabilities(psa_id)

                for c in capability_list.json()['capabilities']:
                    output += "<tns:capability>" + c + "</tns:capability>"

                # End generic

            else:
                print "Not generic"
                output += "<tns:service serviceID=\"id" + str(i) + "\"> "
                output += "<tns:PSA name=\"" + str(psa_id) + "\">"
                output += "<tns:PSA_info />"
                opt_par_r = psar.get_psa_opt_par(psa_id)
                if opt_par_r.status_code != 200:
                    raise Exception("ERROR: No optimisation profile for this PSA ID: " + str(psa_id))

                opt_par = opt_par_r.json()

                output += "<tns:PSA_characteristic cost=\"" + str(opt_par['cost']) + "\" latency=\" " \
                          + str(opt_par['latency']) + "\" rating=\"" + str(opt_par['rating']) + "\"/>"

                # Build the capability tags
                output += "<tns:capability>"
                capability_list = psar.get_psa_capabilities(psa_id)
                for c in capability_list.json()['capabilities']:
                    output += "<tns:capability_list>" + c + "</tns:capability_list>"
                output += "</tns:capability>"

                for a in mspl_psa_assoc:
                    if a['psa_id'] == psa_id:
                        mspl_id[:a['mspl']]

                if len(mspl_id) > 0:
                    output += "<tns:MSPL_list>"
                    for mspl in mspl_id:
                        output += " <tns:mspl_list id=\"" + mspl + "\"/>"

                    output += "</tns:MSPL_list>"
                output += "</tns:PSA>"
                # End non-generic

            output += "</tns:service>"
            i = i + 1

        output += " <tns:rootService>id0</tns:rootService>"
        output += " <tns:endService>id" + str(max_number - 1) + "</tns:endService>"

        i = 0
        while (i < max_number - 1):
            output += "<tns:edge>"
            output += " <tns:src_Service>" + "id" + str(i) + "</tns:src_Service>"
            output += " <tns:dst_Service>" + "id" + str(i + 1) + "</tns:dst_Service>"
            output += " <tns:networkFields/>"
            output += "</tns:edge>"
            i = i + 1

	if max_number==1:
	    output += "<tns:edge>"
            output += "<tns:src_Service>" + "id0</tns:src_Service>"
            output += "<tns:dst_Service>" + "id0</tns:dst_Service>"
            output += "<tns:networkFields/>"
            output += "</tns:edge>"

        output = output + " </tns:service_graph></tns:Mapping>"
        print output
        return output

    def convert_GGUI_syntax_to_HSPL(self, hspljson):
        """
        The GUI used to define policies currently has a limitation where
        it does not produce proper well-formed XML according to the HSPL
        schema. This function tries to sanitise the GUI representation and
        produce a valid XML version.
        """

        output = """<?xml version='1.0' encoding='UTF-8'?>
		        <tns:Mapping xmlns:tns='http://www.example.org/Refinement_Schema' 
		            xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' 
		            xsi:schemaLocation=
		            'http://www.example.org/Refinement_Schema Refinement_Schema.xsd '>"""
        output += "<tns:hspl_list>"
        i = 0
        while (i < len(hspljson)):
            output += "<tns:hspl subject='" + str(hspljson[i]['target']) + "' id='hspl" + str(hspljson[i]['id']) + "'>"
            pieces = str(hspljson[i]['hspl']).split(';')
            action = pieces[1]
            obj = pieces[2]

            self.dbprint(obj)

            # BEGIN HACKS
            obj = obj.replace("Internet traffic", "Internet_traffic")
            obj = obj.replace("intranet traffic", "Intranet_traffic")
            action = action.replace("is/are authorized to access", "authorise_access")
            action = action.replace("is/are not authorized to access", "no_authorise_access")
            action = action.replace("reduce(s)", "reduce")
            action = action.replace("remove(s)", "remove")
            action = action.replace("protect(s) confidentiality", "prot_conf")
            # END HACKS

            output += "<tns:action>" + str(action) + "</tns:action>"
            output += "<tns:objectH>" + str(obj) + "</tns:objectH>"
            output += "<tns:fields"

            time_list = []
            url_list = []
            target_list = []
            content_list = []
            purpose_list = []
            resource_list = []
            up_bandwidth_list = []
            dl_bandwidth_list = []
            country_list = []

            if (len(pieces) > 3):

                j = 3
                while (j < len(pieces)):
                    print "Going through all the fields"
                    field = str(pieces[j])
                    field = field.translate(None, "()")
                    # self.dbprint( field
                    data = field.split(",")
                    k = 0

                    while k < (len(data) - 1):
                        if data[k] == "time_period":
                            time_list.append(data[k + 1])
                        elif data[k] == "specific_URL":
                            url_list.append(data[k + 1])
                        elif data[k] == "traffic_target":
                            target_list.append(data[k + 1])
                        elif data[k] == "type_Content":
                            content_list.append(data[k + 1])
                        elif data[k] == "purpose":
                            purpose_list.append(data[k + 1])
                        elif data[k] == "resource_values":
                            resource_list.append(data[k + 1])
                        elif data[k] == "uplink_bandwidth_value":
                            up_bandwidth_list.append(data[k + 1])
                        elif data[k] == "downlink_bandwidth_value":
                            dl_bandwidth_list.append(data[k + 1])
                        elif data[k] == "country":
                            country_list.append(data[k + 1])
                        else:
                            pass
                        k = k + 1
                    j = j + 1

            if len(dl_bandwidth_list) > 0 or len(up_bandwidth_list) > 0:
                output += " "
                for v in dl_bandwidth_list:
                    output += " downlink_bandwidth_value="
                    output += "\"" + str(v) + "\""
                for v in up_bandwidth_list:
                    output += " uplink_bandwidth_value="
                    output += "\"" + str(v) + "\""

            if len(country_list) > 0:
                for v in country_list:
                    output += " country='" + str(v) + "'"
            
            output += ">"

            if len(time_list) > 0:
                output += "<tns:time_period time-zone='UTC'>"
                for v in time_list:
                    output += "<tns:interval_time><tns:time_hours start-time='"
                    times = v.split("-")
                    firstTime = times[0]
                    secondTime = times[1]
                    output += str(firstTime) + ":00' end-time='"
                    output += str(secondTime) + ":00' />"
                    output += "</tns:interval_time>"
                output += "</tns:time_period>"

            if len(url_list) > 0:
                output += "<tns:specific_URL>"
                for v in url_list:
                    output += "<tns:URL>"
                    output += str(v)
                    output += "</tns:URL>"
                output += "</tns:specific_URL>"

            if len(target_list) > 0:
                output += "<tns:traffic_target>"
                for v in target_list:
                    output += "<tns:target_name>"
                    output += str(v)
                    output += "</tns:target_name>"
                output += "</tns:traffic_target>"

            if len(content_list) > 0:
                output += "<tns:type_content>"
                for v in content_list:
                    output += "<tns:content_name>"
                    output += str(v)
                    output += "</tns:content_name>"
                output += "</tns:type_content>"

            if len(purpose_list) > 0:
                output += "<tns:purpose>"
                for v in purpose_list:
                    output += "<tns:purpose_name>"
                    output += str(v)
                    output += "</tns:purpose_name>"
                output += "</tns:purpose>"

            if len(resource_list) > 0:
                output += "<tns:resource_values>"
                for v in url_list:
                    output += "<tns:name_resurces>"
                    output += str(v)
                    output += "</tns:name_resurces>"
                output += "</tns:resource_values>"

            output += "</tns:fields>"
            output += "</tns:hspl>"

            i = i + 1

        output += "</tns:hspl_list> </tns:Mapping>"

        f = open("hspl.xml", "w")
        f.write(output)
        f.write("\n")
        f.close()
        print "Converted HSPL"
        return output

    # On failure, returns None
    # On success, returns a tuple of the Application Graph in XML format + the list of MSPLs
    def H2M(self, user, password, upr_url, spm_url, psar_url, editor_id=None):

        # Delete old data
        self.delete_ag(user, editor_id, password, upr_url)

        print "Username is " + str(user) + ". Editor is " + str(editor_id)
        upr = upr_client.UPRClient(str(upr_url))
        cred = upr.auth_user(user, password)
        if cred.status_code != 200:
            self.dbprint("unauthorised")
        else:
            self.dbprint("successful authentication")

        if editor_id == None:
            editor_id = user

        r = upr.get_user_list(user_id=user)
        if r.status_code != 200:
            self.dbprint("error getting user list")
        else:
            print "Username is " + user + " " + str(r.text)
            data = r.json()
            if data['creator'] != None:
                self.dbprint("Creator: " + str(data['creator']))
            # editor_id = data['creator']
            else:
                self.dbprint("User has no parent creator")

        r = upr.get_user_type(user_id=user)
        if r.status_code == 404:
            self.dbprint("error getting user type")
        else:
            data = r.json()
            usertype = data['type']
            self.dbprint("User type: " + usertype)

            # If normal user, delete all MSPLs
            if usertype == "normal":
                self.delete_all_mspl(user, password, upr_url, editor_id)

            r = upr.get_user_opt_profile(user)
            if r.status_code != 200:
                self.dbprint("error could not find optimisation profile")

            data = r.json()
            opt_profile = data['optimization_profile']
            self.dbprint("Optimisation profile: " + str(opt_profile))

            # This is a hack, will clean later.
            if True:

                r = upr.get_user_list(user_id=user)
                if r.status_code != 200:
                    raise Exception("UPR error code " + str(r.status_code))

                data = r.json()
                admin = data['is_admin']

                if (admin == True):
                    print str(user) + " is an admin"
                    print "Getting created users"
                    r = upr.get_created_users(user)
                    if r.status_code == 200:
                        data = r.json()
                        users = data['users']
                        print str(user) + " has created " + str(len(users)) + " users"

                        # For every user that the admin has created...
                        token = ""
                        for child in users:
                            print "Running workflow manager for " + str(child)
                            print "Just about to run nested WFM...current user is " + str(user)
                            wfm = workflow_manager.WorkflowManager(child, token, upr_url, spm_url, psar_url)
                    else:
                        print colored(
                                "ERROR getting created users for " + str(user) + " with UPR status" + str(
                                        r.status_code))
                else:
                    print str(user) + " is NOT an admin"

                if editor_id == None or editor_id == user:
                    editor_id = user
                    print str(user) + ": I AM MYSELF"

                r = upr.get_hspl(target=user, editor=editor_id)

                if r.status_code != 200:
                    self.dbprint("something went wrong when getting the HSPL: HTTP " + str(r.status_code))
                else:
                    new = json.loads(json.dumps(r.json()))
                    self.dbprint(r.json())
                    if len(new) == 0:
                        print "No HSPLS"
                        if usertype != "expert":
                            self.dbprint(colored("ERROR: No HSPLs found for this user", 'red'))
                            return None

                    self.dbprint("Converting HSPL")
                    hspl_list_xml = self.convert_GGUI_syntax_to_HSPL(r.json())
                    self.dbprint(hspl_list_xml)
                    self.validate_hspl(hspl_list_xml)
                    market_psa_list_xml = self.get_market_psa_xml(user, psar_url)
                    print str(market_psa_list_xml)

                    r = upr.get_user_psa(user, is_active=True)
                    h2m_input = ""

                    subject_xml = self.get_subject_xml_file(upr_url)

                    f = open('xmlSchema/Target_Review.xml', 'r')
                    target_xml = f.read()
                    f.close()

                    f = open('xmlSchema/Content_Review.xml', 'r')
                    content_xml = f.read()
                    f.close()

                    user_sg = None
                    psa_xml = None
                    active_psa_list_xml = ""

                    # TODO: Below is for the expert user, call convertPSAlist for normal user
                    if usertype == "expert":

                        r = upr.get_user_mspl_psa(user)
                        mspl_psa_assoc = r.json()

                        r = upr.get_user_psa(user, is_active=True)
                        market_psa_list_json = r.json()
                        print "Converting SG for expert"

                        user_sg = self.convertSG(market_psa_list_json, mspl_psa_assoc, psar_url)
                        psa_xml = market_psa_list_json
                    else:
                        user_sg = self.convertPSAlist_normal(user, upr_url, psar_url)
                        psa_xml = user_sg
                        active_psa_list_xml = psa_xml

                        # Force this optimisation for all users 
                        opt_profile = "MIN_BUY_COSTMAX_RATING"

                        # Decoded version for debugging
                        h2m_input = self.collectInput("POLICY_HSPL", hspl_list_xml, user_sg, market_psa_list_xml,
                                                  market_psa_list_xml, subject_xml, content_xml, target_xml,
                                                  opt_profile, "0")

                        f = open('h2m_input_decoded.json', 'w')
                        debug = f.write(h2m_input)
                        f.close()

                    # Base64 encoding # comment these to disable base64
                    hspl_list_xml = base64.b64encode(hspl_list_xml)
                    user_sg = base64.b64encode(user_sg)  # Expert/enthusiastic user
                    psa_xml = base64.b64encode(str(psa_xml))
                    active_psa_list_xml = base64.b64encode(active_psa_list_xml)
                    market_psa_list_xml = base64.b64encode(market_psa_list_xml)
                    subject_xml = base64.b64encode(subject_xml)
                    content_xml = base64.b64encode(content_xml)
                    target_xml = base64.b64encode(target_xml)
                    
                    if usertype == "normal":
                        h2m_input = self.collectInput("POLICY_HSPL", hspl_list_xml, user_sg, psa_xml,
                                                      market_psa_list_xml, subject_xml, content_xml, target_xml,
                                                      opt_profile, "0")
                    if usertype == "expert":
                        r = upr.get_mspl(target=str(user), editor=str(editor_id))
                        if r.status_code != 200:
                            print "ERROR: Could not retrieve MSPLs for expert user " + str(user) + " with error " + str(r.status_code)
                            return None

                        # At this point, the MSPLs should already be in base64 format?
                        mspl_list_xml = []
                        mspl_list_json = r.json()
                        concat_mspl = ""
                        print str(r.json())

                        howmany = json.loads(json.dumps(r.json()))
                        if len(howmany) == 0:
                            print "ERROR: No MSPLs available for th expert user: " + str(user)
                            return None

                        for mspl in mspl_list_json:
                            print "Getting MSPL policy..."
                            mspl_list_xml.append(mspl['mspl'])
                            concat_mspl = concat_mspl + base64.b64decode(mspl['mspl'])

                        print "Performing for expert..."
                        #print "\n\n"
                        #print str(concat_mspl)
                        #print "\n\n"
                        concat_mspl = base64.b64encode(concat_mspl)
                            
                        h2m_input = self.collectInput("APPLICATION_MSPL_SG", concat_mspl, user_sg, market_psa_list_xml,
                                                      market_psa_list_xml, subject_xml, content_xml, target_xml,
                                                      opt_profile, "0")


                    print  "Contacting the SPM H2M service"

                    f = open("h2m_input.json", "w")
                    f.write(h2m_input)
                    f.close()

                    headers = {'content-type': 'application/json'}
                    counter = 0
                    print "Calling H2M"
                    while counter < 3:
                        try:
                            r = requests.post("http://" + spm_url + \
                                              ":8181/restconf/operations/h2mservice:h2mrefinement",
                                              auth=('admin', 'admin'), headers=headers,
                                              data=h2m_input, timeout=None)
                            break
                        except Exception:
                            counter = counter + 1
                            if counter < 3:
                                continue
                            self.dbprint("Connection to server timed out...")
                            sleep(1)
                            self.dbprint("Retrying...")
                            return None

                    self.dbprint(r.status_code)
                    print "SPM replied with " + str(r.status_code)
                    if r.status_code == 200:
                        data = r.json()
                        application_graph = base64.b64decode(data['output']['application_graph'])

                        try:
                            problem = data['output']['remediation']
                            self.dbprint("Policies need reconciliation")
                            self.dbprint("SPM returned " + str(r.json()))
                            is_reconciled = False

                            b64_mspl_list = []
                            ag = ""

                            # If policies are not enforceable, abort and back away very slowly...
                            try:
                                b64mspl_list = data['output']['MSPL']
                                ag = data['output']['application_graph']
                            except KeyError:
                                print colored("POLICY NOT ENFORCEABLE", 'red')
                                return None

                            self.dbprint("There are " + str(len(b64mspl_list)) + " MSPLs")
                            for mspl in b64mspl_list:
                                capability = self.get_capability_from_mspl(base64.b64decode(mspl))
                                print "CAPABILITY IS " + str(capability)
                                r = upr.create_mspl(user, editor_id, capability, is_reconciled, mspl)
                                print "Uploading unreconciled MSPLs"
                                if r.status_code != 201:
                                    self.dbprint("     Error storing MSPL set in UPR with error code " + \
                                                 + str(r.status_code))
                                else:
                                    self.dbprint("     Successfully stored MSPL set in UPR")
                                    self.dbprint("     Policies of " + str(user) + " still require reconciliaton")
                                    r = upr.post_ag(user, editor_id, ag)
                                    if r.status_code != 201:
                                        print colored("UPR returned error code when storing AG: " + str(r.status_code), 'red')
                                    else:
                                        print colored("Successfully stored user AG in UPR", 'green')
                                    '''
                                    # TODO: Need to store MSPL-PSA associations
                                    # psa_id = get_psa_assoc(mspl)
                                    if (psa_id != None):
                                        # TODO: FINISH T HIS BIT
                                        #r = post_mspl_psa_assoc()
                                        if r.status_code != 201:
                                            print "COULD NOT CREATE USER-MSPL-PSA assoc!!!!!"
                                        else:
                                            self.dbprint("      Stored user-mspl-psa association")
                                    '''

                            return None
                        except KeyError:
                            pass

                        b64mspl_list = data['output']['MSPL']
                        ag = data['output']['application_graph']

                        # Store resulting MSPL set and AG in the UPR

                        self.dbprint("There are " + str(len(b64mspl_list)) + " MSPLs")
                        mspl_list = []
                        for mspl in b64mspl_list:
                            raw_mspl = base64.b64decode(mspl)
                            mspl_list.append(raw_mspl)

                            # Store MSPL in UPR.
                            # TODO: store capability in capability field for expert users
                            is_reconciled = False
                            capability = self.get_capability_from_mspl(base64.b64decode(mspl))
                            r = upr.create_mspl(user, editor_id, capability, is_reconciled, mspl)
                            if r.status_code != 201:
                                self.dbprint("     Error creating MSPL with code " + str(r.status_code))
                            else:
                                self.dbprint(
                                        colored("     Successfully stored MSPL in UPR: response " + str(r.status_code),
                                                'green'))
                                r = upr.post_ag(user, editor_id, ag)
                                if r.status_code != 201:
                                    print colored("UPR returned error code when storing AG: " + str(r.status_code), 'red')
                                else:
                                    print colored("Successfully stored user AG in UPR", 'green')
 

                        # TODO: perhaps need to store each MSPL in the UPR
                        return (application_graph, mspl_list, editor_id)
                    else:
                        print("Error in H2M service response: " + str(r.text))
                        self.dbprint("\nIf you see the above, copy and paste to Fulvio Valenza and Marco")
                        return None

            else:
                self.dbprint("ERROR: unsupported user")
                return None

    def delete_ag(self, user, editor_id, password, upr_url):
        upr = upr_client.UPRClient(str(upr_url))
        r = upr.delete_user_ag(user, editor_id)
        print "Deleting AG from UPR...status code " + str(r.status_code)
        return r

    def delete_all_mspl(self, user, password, upr_url, editor_id):
        upr = upr_client.UPRClient(str(upr_url))
        if (editor_id == None):
            r = upr.get_mspl(target=user, editor=user)
        else:
            r = upr.get_mspl(target=user, editor=editor_id)
        if r.status_code != 200:
            raise Exception("WFM could not delete MSPL policies from the UPR " + str(r.status_code))

        data = r.json()
        for mspl in data:
            try:
                mspl_id = mspl['mspl_id']
                r = upr.delete_mspl(mspl_id)
                if r.status_code != 204:
                    print colored("Could not delete MSPL??? ERROR code from UPR: " + str(r.status_code), 'red')
            except KeyError:
                print "No MSPL ID? Show the following to Adrian: " + str(r.json())

    def __init__(self, user, password, upr_url, spm_url, psar_url, set_debug=False, editor_id=None):
        self.dbprint("Contacting UPR")

        if editor_id == None:
            upr = upr_client.UPRClient(str(upr_url))
            r = upr.get_user_creator(user)
            if r.status_code == 200:
                data = r.json()
                creator = data['creator']
                if creator != None:
                    wfm = workflow_manager.WorkflowManager(user, password, upr_url, spm_url, psar_url,
                                                           editor_id=creator)

        if set_debug == True:
            self.DEBUG = True

        mspl_list_xml = None
        
        mspl_list_xml = WorkflowManager.H2M(self, user, password, upr_url, spm_url, psar_url, editor_id)

        
        #print "Fatal error during workflow manager"

        if (mspl_list_xml) is None:
            self.dbprint("ERROR: This is the end. My only friend, the end.")
            return None
        else:
            if (len(mspl_list_xml) > 1):
                self.dbprint("H2M Workflow finished")
            else:
                self.dbprint("ERROR: No application graph?")
                return None

    # Checks to see if the HSPL is valid according to the SECURED HSPL schema
    def validate_hspl(self, hspl_list_xml):
        """
        :param hspl_list_xml: The XML of HSPLs
        """
        try:
            xsd_file = 'xmlSchema/hspl.xsd'
            schema = etree.XMLSchema(file=xsd_file)
            parser = objectify.makeparser(schema=schema)
            objectify.fromstring(hspl_list_xml, parser)
            self.dbprint(("YEAH!, my xml file has validated"))
        except XMLSyntaxError:
            self.dbprint("Oh NO!, the GUI HSPL does not validate")
            self.dbprint(
                    """To debug, use: xmllint --format --pretty 1 --load-trace --debug --schema hspl.xsd hspl.xml""")
            self.dbprint(
                    "\nIt might still work with the SPM. But beware, there be dragons. Bad things may happen!")


def main(argv):
    args = argv
    debug = None

    for a in args:
        if a == "--debug":
            debug = True
            args.remove('--debug')

    if len(args) != 6:
        print("Usage: workflow-manager.py <username> <password> <upr_address> <spm_address> <psar_url>")
        print("Optional flags:\n    --debug : Shows more detailed output")
        print("\nMy job is turn HSPL into LSPL, just like water into wine")
    else:
        script, user, password, upr_url, spm_url, psar_url = args
        print "Starting"
        wfm = workflow_manager.WorkflowManager(user, password, upr_url, spm_url, psar_url, set_debug=debug)


if __name__ == '__main__':
    main(argv)

#!/usr/bin/env python

#
# NED Policy Manager (a.k.a the online workflow manager)
#
# Dependencies: pip install json2xml dicttoxml termcolor
#
# Example usage: ./online_workflow_manager.py child child 195.235.93.146 130.192.1.102 testCoop

import os
import json
import base64
import inspect
import requests
import dicttoxml
import upr_client
from sys import argv
from time import sleep
from xml.dom import minidom
from termcolor import colored
from lxml import etree, objectify
from lxml.etree import XMLSyntaxError
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
import logging
import datetime as dt

# TODO: control if there are sessions open, if true close them
class MyFormatter(logging.Formatter):
    converter=dt.datetime.fromtimestamp
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s,%03d" % (t, record.msecs)
        return s


class AnalysisWorkflowManager(object):

	DEBUG = True
        DEBUG_MSG = ""

	def dbprint(self, string):
	    if self.DEBUG == True:
	            self.logger.info(string)

        def sanitize(string):
            s = string.replace("\\n", "")
            s = s.replace("\\r", "")
            s = s.replace("\\t", "")
            s = s.replace("\\/", "")
            return s
		    

        def spm_mifa(self, spm_url, mifa_input):
            #mifa_input = sanitize(mifa_input)
            self.dbprint("CMON MIFA")

            mifa_input = mifa_input.replace("\\n", "")
            mifa_input = mifa_input.replace("\\r", "")
            mifa_input = mifa_input.replace("\\t", "")
            mifa_input = mifa_input.replace("\\/", "")
            mifa_input = mifa_input.replace("\\\"", "\"")

	    rec_svc = ":8181/restconf/operations/reconciliation:muca"
	    url = "http://" + str(spm_url) + str(rec_svc)

	    self.dbprint("Contacting the SPM mifa service")

            r = ""
            headers = {'content-type': 'application/json'}

            counter = 0
	    while counter < 3:
		try:
                    if self.DEBUG == True:
                        #print str(rec_input)
                        self.dbprint( str(url) )
		    r = requests.post(url, auth=('admin', 'admin'),
			headers=headers, data=mifa_input, timeout=None)
		    return r
		except Exception:
		    counter = counter + 1
		    if counter < 3:
		    	continue
		    # Give up
		    self.dbprint("ERROR: Could not reach SPM at " + str(url))
		    raise Exception ('Could not reach SPM.')
            return None
	    
	    
	def spm_sfa(self, spm_url, sfa_input):
            print "cmon"
            #sfa_input = sanitize(sfa_input)
            sfa_input = sfa_input.replace("\\n", "")
            sfa_input = sfa_input.replace("\\t", "")
            sfa_input = sfa_input.replace("\\r", "")
            sfa_input = sfa_input.replace("\\/", "")

            print str(sfa_input)

            print "done"
	    rec_svc = ":8181/restconf/operations/reconciliation:sucas"
	    url = "http://" + str(spm_url) + str(rec_svc)

	    print "Contacting the SPM SFA service"

            r = ""
            headers = {'content-type': 'application/json'}

            counter = 0
            print "sfa..."
	    while counter < 3:
		try:
                    if self.DEBUG == True:
                        #print str(rec_input)
                        self.dbprint( str(url) )
		    r = requests.post(url, auth=('admin', 'admin'),
			headers=headers, data=sfa_input, timeout=None)
		    return r
		except Exception:
		    counter = counter + 1
		    if counter < 3:
		    	continue
		    # Give up
		    self.dbprint("ERROR: Could not reach SPM at " + str(url))
                    self.DEBUG_MSG = "ERROR: Could not reach SPM at " + str(url)
		    raise Exception ('Could not reach SPM.')
            return None
	    
	    
	def spm_ifa(self, spm_url, ifa_input):
	    ifa_svc = ":8181/restconf/operations/reconciliation:sucad"
	    url = "http://" + str(spm_url) + str(ifa_svc)

	    self.dbprint("Contacting the SPM IFA service")

            r = ""
            headers = {'content-type': 'application/json'}

            counter = 0
	    while counter < 3:
		try:
                    if self.DEBUG == True:
                        #print str(rec_input)
                        self.dbprint( str(url) )
		    r = requests.post(url, auth=('admin', 'admin'),
			headers=headers, data=ifa_input, timeout=None)
		    return r
		except Exception:
		    counter = counter + 1
		    if counter < 3:
		    	continue
		    # Give up
		    self.dbprint("ERROR: Could not reach SPM at " + str(url))
		    raise Exception ('Could not reach SPM.')
            return None
	    

        def get_capability_from_mspl(self, mspl):
            capabilities = ""
            tree = ET.fromstring(mspl)
            root = tree
            for child in root:
                for a in child:
                    if (str(a.tag).endswith("capability")):
                        for b in a:
                            self.dbprint("Found a capability: " + str(b.text))
                            capabilities = capabilities + str(b.text)
            return capabilities
	    

	def get_creator(self, user, upr):
		r = upr.get_user_creator(user)
		if (r.status_code != 200):
			self.dbprint( "ERROR getting creator of user during reconciliation" \
					+ ". Status code = " + str(r.status_code))
			raise Exception('Error getting creator of ' + str(user) \
					+ ". Error is " + str(r.status_code) \
					+ '. Does ' + str(user) + ' exist?') 
		data = r.json()
		return data['creator']
		
		
	def get_PolicyStack(self, user, upr, cooperative, coop, uncoop):
		mspls = []	
		coopList = []
                uncoopList = []
	
		
		creator = user
		
		# get all AG of user
		r = upr.get_user_ag(user)
		if r.status_code != 200:
			self.dbprint( "ERROR getting AG of user + " + str(user) + " with error code " + str(r.status_code))
		applicationGraphs = r.json()

		while creator != None:
			self.dbprint("")
			self.dbprint("Computing policy stack of layer : " + user+ " " +creator)

			#get all MSPLs of current stack layer
			r = upr.get_mspl(is_reconciled='false', target=str(user), editor=str(creator))
                        if r.status_code != 200:
                            raise Exception('Could not get policies for user!')
                        
                        mspl_list_json = r.json()

			for mspl in mspl_list_json:
				self.dbprint("Getting MSPL...")
				# add MSPL to msplList
                                mspls.append(mspl['mspl'])
			
			r = upr.get_user_list(user_id=creator)
			if (r.status_code != 200):
				self.dbprint("ERROR finding out cooperative data with + " \
						+ str(r.status_code))
				raise Exception ("Can't tell if cooperative: " \
						+ str(r.status_code) )
			data = r.json()
			creator_is_cooperative = data['is_cooperative']

			if cooperative and creator_is_cooperative:
                                try:
				    data = {}
				    data['id'] = str(coop)
				    data['ag'] = filter(lambda ag: ag['editor'].upper() == str(creator).upper(), applicationGraphs)[0]['ag'];
				    data['creator']  = creator
				    coopList.append(data)
				    coop += 1
				    self.dbprint("Adding to user's cooperative stack")
                                except IndexError:
                                    self.dbprint( colored("ERROR: USER " + str(creator) + " DOES NOT HAVE AN AG", 'red') )
                                    self.DEBUG_MSG = "ERROR: USER " + str(creator) + " DOES NOT HAVE AN AG"
			else:
				cooperative = False
                                try:
				    data = {}
				    data['id'] = str(uncoop)
				    data['ag'] = filter(lambda ag: ag['editor'].upper() == str(creator).upper(), applicationGraphs)[0]['ag'];
				    data['creator']  = creator
				    uncoopList.append(data)
				    uncoop += 1
				    self.dbprint("Adding to uncooperative stack")
                                except IndexError:
                                    self.dbprint( colored("ERROR: USER " + str(creator) + " DOES NOT HAV AN AG", 'red') )
			creator = self.get_creator(creator, upr)
			
		data = {}
		data['mspls'] = mspls
		data['coopList'] = coopList
		data['uncoopList'] = uncoopList
		data['cooperative'] = cooperative
		data['coop'] = coop
		data['uncoop'] = uncoop

                print "Finished policy stack"
                self.dbprint("Finished policy stack")
		
		return data
	
	def mifa(self, user, password, upr_url, spm_url):
		self.dbprint("Truth and MIFA...")
		upr = upr_client.UPRClient(str(upr_url))
	
	
		mspls = []	
		coopList = []
                uncoopList = []
                    
		data = self.get_PolicyStack(user, upr, True, 1, 1)
		mspls.extend(data['mspls'])
		coopList.extend(data['coopList'])

		coopList.reverse()
		
		# Prepare input 
		data = {}
		data['coop'] = coopList
		data['MSPL'] = mspls
		
		parent_json = {}
		parent_json['input'] = data
		mifa_input = json.dumps(parent_json, sort_keys=True, indent=4)

	
		self.dbprint(mifa_input)

                self.dbprint("Got to here")

                r = self.spm_mifa(spm_url, mifa_input)

                print str(r.status_code)

                if r.status_code != 200:
                    self.dbprint( "ERROR: SPM returned " + str(r.status_code) )
                    self.DEBUG_MSG = "ERROR: SPM returned " + str(r.status_code)
                    raise Exception ("SPM returned " + str(r.status_code))

                data = r.json()

                try:
                    report = data['output']['report']
                    print "RECONCILIATION!"
                    try:
                        r = upr.post_reconciliation_report(user, user, report)
                    except Exception as ex:
                        print "Some exception" + str(ex)
                    print "RESULT"
                    if r.status_code != 201:
                        self.dbprint (colored('ERROR saving report: ' + str(r.status_code), 'red'))
                    else:
                        self.dbprint( colored('MIFA report created', 'green'))
                    print "DONE: "
                    report = base64.b64decode(r.json()['reconciliation_report'])
                    return report
                except KeyError:
                    print "KEYERROR"
                    self.DEBUG_MSG = "No MIFA report"
                    self.dbprint( colored('No MIFA report', 'red')) 
		
                return None


        def ifa(self, user, password, upr_url, spm_url):
	    self.dbprint("Truth and IFA...")
	    upr = upr_client.UPRClient(str(upr_url))
	    
	    mspls = []	
	    
	    r = upr.get_mspl(is_reconciled='false', target=str(user), editor=str(user))
	    
	    if r.status_code != 200:
                raise Exception('Could not get policies for user!')
	    else:
		mspl_list_json = r.json()
		i = 1;
		for mspl in mspl_list_json:
		    self.dbprint("Getting MSPL...")
		    # add MSPL to msplList
		    mspls.append({'id':str(i), 'mspl':mspl['mspl']})
		    i += 1

		data = {}
		data['MSPL'] = mspls

		parent_json = {}
		parent_json['input'] = data
		ifa_input = json.dumps(parent_json, sort_keys=True, indent=4)

		self.dbprint(ifa_input)
    
		r = self.spm_ifa(spm_url, ifa_input)

		if r.status_code != 200:
		    self.dbprint( "ERROR: SPM returned " + str(r.status_code) )
                    self.DEBUG_MSG = "ERROR: SPM returned " + str(r.status_code)
                    raise Exception ("SPM returned " + str(r.status_code))

		data = r.json()

		try:
		    report = data['output']['report']
		    upr.post_reconciliation_report(user, user, report)
		except KeyError:
		    self.dbprint( colored('No IFA report', 'red'))
                    self.DEBUG_MSG = "No IFA report"
		    
		    
	def sfa(self, user, password, mspl, upr_url, spm_url):
                print "executing sfa"
	        self.dbprint("Truth and SFA...")
	        upr = upr_client.UPRClient(str(upr_url))
		data = {}
                mspl = mspl.replace("\\n", "")
                mspl = mspl.replace("\\r", "")
                mspl = mspl.replace("\\t", "")
                mspl = mspl.replace("\\/", "")
                mspl = mspl.replace("\\\"", "\"")

                mspl = base64.b64encode(mspl)
		data['MSPL'] = mspl
                

		parent_json = {}
		parent_json['input'] = data
		sfa_input = json.dumps(parent_json, sort_keys=True, indent=4)

		print "Sending to SPM" 
		r = self.spm_sfa(spm_url, sfa_input)
                print "SPM returned " + str(r.status_code)

                if r.status_code != 200:
                    self.dbprint( "ERROR: SPM returned " + str(r.status_code) )
                    self.DEBUG_MSG = "SPM returned " + str(r.status_code)
                    raise Exception ("SPM returned " + str(r.status_code))

                data = r.json()
                print "REPORT"

                try:
                    report = base64.b64decode(data['output']['report'])
                    #r = upr.post_reconciliation_report(user, user, report)
                    return report
                except KeyError:
                    self.dbprint( colored('No SFA report', 'red'))
                    self.DEBUG_MSG = "No SFA report"
  

	def __init__(self, debug=False):
	
		self.init_log()
	
		# If debug is enabled
		if (debug == True):
			self.DEBUG = True

                

	def init_log(self):
		self.logger = logging.getLogger(__name__)
		self.logger.setLevel(logging.DEBUG)

		fh = logging.FileHandler("WFM.log")
		fh.setLevel(logging.DEBUG)

		console = logging.StreamHandler()

		formatter = MyFormatter(fmt='%(asctime)s %(message)s',datefmt='%Y-%m-%d,%H:%M:%S.%f')
		fh.setFormatter(formatter)
		console.setFormatter(formatter)

		self.logger.addHandler(console)
		self.logger.addHandler(fh)
		#logging.basicConfig(filename=conf.LOG_FILE,level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
		self.logger.info("--------")
		self.logger.info("WFM running")
		self.logger.info("--------")


def main():
	args = argv
	set_debug = None

	for a in args:
		if a == "--debug":
			set_debug = True
               		args.remove('--debug')


	if len(args) != 7:
		print("workflow_manager_analysis.py {sfa, ifa, mifa} <username> <password>" + \
				"<upr_address> <spm_address> <MSPL_ID>")
	else:
		script, analysis_type, user, password, upr_url, spm_url, mspl_id = argv
		
		
		wfm = AnalysisWorkflowManager(debug=set_debug) 
		
		
		    
		if analysis_type == "SFA":
		    r = wfm.sfa(user, password, mspl_id, upr_url, spm_url)
		    
		if analysis_type == "IFA":
		    r = wfm.ifa(user, password, upr_url, spm_url)
		    
		if analysis_type == "MIFA":
		    r = wfm.mifa(user, password, upr_url, spm_url)

if __name__ == '__main__':
	main()

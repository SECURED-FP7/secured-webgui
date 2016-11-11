from django import forms
from django.db import models

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from operator import itemgetter
import upr_client
import constants
import requests
import json
import datetime
import psar_client
from lxml import etree
import base64

"""
USER model
"""
class Group(models.Model):
    name = models.CharField(max_length=255)


class User(models.Model):
    
    USERTYPE_CHOICES = (
        (1, 'Expert user'),
        (2, 'Normal user'),
        (3, 'Enthusiastic user')
    )
    
    username     = models.CharField(max_length=255, unique=True)
    password     = models.CharField(max_length=255)
    usertype     = models.IntegerField(choices=USERTYPE_CHOICES)
    group        = models.ForeignKey(Group, null=True)
    applications = models.ManyToManyField('Application', through='UserApplication', through_fields=('user', 'application'))
    

"""
STORE APPLICATION model
"""
class Capability(models.Model):
    name = models.CharField(max_length=255)


class Application(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField(null=True)
    capabilities = models.ManyToManyField(Capability)
    

"""
USER APPLICATION model
"""    
class MSPL(models.Model):
    user  = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    xml   = models.TextField()
    

class UserCapability(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    capability = models.ForeignKey(Capability, on_delete=models.CASCADE)
    enabled    = models.BooleanField(default=0)
    mspl       = models.ForeignKey(MSPL, null=True, on_delete=models.SET_NULL)
        
    
class UserApplication(models.Model):
    user         = models.ForeignKey(User, on_delete=models.CASCADE)
    application  = models.ForeignKey(Application, on_delete=models.CASCADE)
    capabilities = models.ManyToManyField(UserCapability)
    enabled      = models.BooleanField(default=0)
    order        = models.IntegerField()
    
    
class Optimization():
    
    OPT1_CHOICES = (
        (0, 'None', 'None'),
        (1, 'Minimize cost and latency', 'MIN_BUY_COSTMIN_LATENCY'),
        (2, 'Minimize transfer time and latency', 'MIN_TRANFER_COSTMIN_LATENCY'),
        (3, 'Minimize cost and maximize rating', 'MIN_BUY_COSTMAX_RATING')
    )
    
    OPT2_CHOICES = (
        (0, 'None'),
        (1, 'Optimize for speed'),
        (2, 'Optimize for latency'),
        (3, 'Minimize network bandwith consumption')
    )
        
    OPT3_CHOICES = (
        (0, 'None'),
        (1, 'Optimize for speed'),
        (2, 'Optimize for latency'),
        (3, 'Minimize network bandwith consumption')
    )
    
    user  = models.ForeignKey(User, on_delete=models.CASCADE)
    opt1 = models.IntegerField(choices=OPT1_CHOICES, default=0)
    opt2 = models.IntegerField(choices=OPT2_CHOICES, default=0)
    opt3 = models.IntegerField(choices=OPT3_CHOICES, default=0)
    
    @staticmethod
    def getOpt1List():
        list = []
        for opt in Optimization.OPT1_CHOICES:
            list.append({'id': opt[0], 'value': opt[1], 'constant': opt[2]})
        return list
    
    @staticmethod
    def getOpt2List():
        list = []
        for opt in Optimization.OPT2_CHOICES:
            list.append({'id': opt[0], 'value': opt[1]})
        return list
    
    @staticmethod
    def getOpt3List():
        list = []
        for opt in Optimization.OPT3_CHOICES:
            list.append({'id': opt[0], 'value': opt[1]})
        return list
    


"""
HSPL model
"""
class Condition():
    
    CONDITION_CHOICES = (
        (1, 'time_period', 'time period'),
        (2, 'traffic_target', 'traffic target'),
        (3, 'specific_URL', 'specific URL'),
        (4, 'type_Content', 'type of content'),
        (5, 'purpose', 'purpose'),
        (6, 'uplink_bandwidth_value', 'uplink bandwidth value'),
        (7, 'resource_values', 'resource value'),
	(8, 'downlink_bandwidth_value', 'downlink bandwidth value'),
	(9, 'country', 'country')
    )
    
    condition = models.IntegerField(choices=CONDITION_CHOICES)
    text = models.CharField(max_length=255, null=True)
    number = models.FloatField(null=True)
    datetime1 = models.TimeField(null=True)
    datetime2 = models.TimeField(null=True)


class HSPL():
    
    ACTION_CHOICES = (
        (1, 'no_authorise_access', 'is/are not authorized to access'),
        (2, 'authorise_access', 'is/are authorized to access'),
        (3, 'enable', 'enable(s)'),
        (4, 'remove', 'remove(s)'),
        (5, 'reduce', 'reduce(s)'),
        (6, 'check_over', 'check(s) over'),
        (7, 'count', 'count(s)'),
        (8, 'prot_conf', 'protect(s) confidentiality'),
        (9, 'prot_integr', 'protect(s) integrity'),
        (10, 'prot_conf_integr', 'protect(s) confidentiality integrity')
    )
    
    OBJECT_CHOICES = (
        (1, 'VoIP_traffic', 'VOIP traffic'),
        (2, 'P2P_traffic', 'P2P traffic'),
        (3, 'T3G4G_traffic', '3G/4G traffic'),
        (4, 'Internet_traffic', 'Internet traffic'),
        (5, 'Intranet_traffic', 'intranet traffic'),
        (6, 'DNS_traffic', 'DNS traffic'),
        (7, 'AllTraffic', 'all traffic'),
        (8, 'tacking_techniques', 'public identity'),
        (9, 'resource', 'Resource x'),
        (10, 'file_scanning', 'file scanning'),
        (11, 'email_scanning', 'email scanning'),
        (12, 'antivirus', 'antivirus'),
        (13, 'basic_prarental_control', 'basic parental control'),
        (14, 'advance_parental_control', 'advanced parental control'),
        (15, 'IDS_IPS', 'IDS/IPS'),
        (16, 'DDos_attack_protection', 'DDos attack protection'),
        (17, 'tacking_techniques', 'tracking techniques'),
        (18, 'advertisement', 'advertisement'),
        (19, 'bandwidth', 'bandwidth'),
        (20, 'security_status', 'security status'),
        (21, 'connection', 'connection'),
        (22, 'logging', 'logging'),
	(23, 'malware_detection', 'malware detection'),
	(24, 'antiPhishing', 'anti-phishing'),
	(25, 'anonimity', 'anonimity')
    )
    
    ENABLE_OBJECT = {1: [1,2,3,4,5,6,7,9], 
                     2: [1,2,3,4,5,6,7,9],
                     3: [10,11,12,13,14,15,16,22,23,24,25],
                     4: [8,17,18],
                     5: [19],
                     6: [20],
                     7: [6,21],
                     8: [1,2,3,4,5,6,7],
                     9: [1,2,3,4,5,6,7],
                     10: [1,2,3,4,5,6,7]}
    
    ENABLE_CONDITION = {1: [1,2],
                    2: [1,2],
                    3: [1,2],
                    4: [1,2,3,4],
                    5: [1,2,3,4],
                    6: [1,2,3,4],
                    7: [1,2,3,4],
                    8: [1,2,3],
                    9: [7],
                    10: [5],
                    11: [5],
                    12: [2],
                    13: [],
                    14: [1,4],
                    15: [2],
                    16: [2],
                    17: [3],
                    18: [3],
                    19: [1,3,6,8],
                    20: [],
                    21: [1,3],
                    22: [1,2,3,4,5],
		    23: [4,5],
		    24: [],
		    25: [9]}
    
    user      = models.ForeignKey(User, on_delete=models.CASCADE, default=0)
    subject   = models.CharField(max_length=100)
    action    = models.IntegerField(choices=ACTION_CHOICES)
    object    = models.IntegerField(choices=OBJECT_CHOICES)
    #condition = models.ManyToManyField(Condition)

    @staticmethod
    def getActionList():
        list = []
        for hspl in HSPL.ACTION_CHOICES:
            list.append({'id': hspl[0], 'value': hspl[1], 'string': hspl[2]})
        return list
    
    def getObjectList(self):
        list = []
        list_objects_id = self.ENABLE_OBJECT[self.action]
        for hspl in HSPL.OBJECT_CHOICES:
            if hspl[0] in list_objects_id:
                list.append({'id': hspl[0], 'value': hspl[1], 'string': hspl[2]})
        return list
    
    @staticmethod
    def getObjectListStatic(action):
        list = []
        list_objects_id = HSPL.ENABLE_OBJECT[int(action)]
        for hspl in HSPL.OBJECT_CHOICES:
            if hspl[0] in list_objects_id:
                list.append({'id': hspl[0], 'value': hspl[1], 'string': hspl[2]})
        return list

    def getConditionList(self):
        list = []
        list_conditions_id = self.ENABLE_CONDITION[self.object]
        for cond in Condition.CONDITION_CHOICES:
            if cond[0] in list_conditions_id:
                list.append({'id': cond[0], 'value': cond[1], 'string': cond[2]})
        return list

    @staticmethod
    def getConditionListStatic(object):
        list = [] 
        list_conditions_id = HSPL.ENABLE_CONDITION[int(object)]
        for cond in Condition.CONDITION_CHOICES:
            if cond[0] in list_conditions_id:
                list.append({'id': cond[0], 'value': cond[1], 'string': cond[2]})
        return list
    

class HSPLClass(object):

    def __init__(self, hsplObject):
	hsplString = hsplObject['hspl']

        stringList = hsplString.split(";", 3)
        subject = stringList[0]
	actionID = 0
        action = stringList[1]
        actionsList = HSPL.getActionList()
	for item in actionsList:
                if item['value'] == action:
                        actionID = item['id']
                        break

	self.actionString = action

        obj = stringList[2]
        objectsList = HSPL.getObjectListStatic(actionID)
        for item in objectsList:
                if item['value'] == obj:
                        objectID = item['id']
                        break
	
	self.objectString = obj
	self.condition = []
	try:
        	conditions = stringList[3]

		conditionsStringList = conditions.split(";")
	
		index = 1
		for newCondition in conditionsStringList:
			self.condition.append(ConditionClass(newCondition, index, objectID))
			index = index + 1
	except:
		self.condition = []
        
        self.user = hsplObject['editor']
	self.subject = subject
	self.action = actionID
	self.object = objectID
	
	self.id = hsplObject['id']

    def getObjectList(self):
        return HSPL.getObjectListStatic(self.action)

    def getConditionList(self):
	return HSPL.getConditionListStatic(self.object)

    def getString(self):
	phrase = ""
	phrase = self.subject + ";" + self.actionString + ";" + self.objectString
	for condition in self.condition:
		phrase = phrase + ";" + condition.conditionString
	return phrase

class ConditionClass(object):

    def __init__(self, conditionString, newID, objectID):
	
	self.id = newID
	self.conditionString = conditionString
	conditionList = conditionString.split(",")
	condition = conditionList[0].split("(")[1]
	conditionID = 0
	objectsList = HSPL.getConditionListStatic(objectID)
        for item in objectsList:
                if item['value'] == condition:
                        conditionID = item['id']
                        break
	self.condition = conditionID
	option = conditionList[1].split(")")[0]
	if (conditionID == 1):
		periods = option.split("-")
		time1 = periods[0]
		time2 = periods[1]
		
		firstTime = time1.split(":")
		self.datetime1 = datetime.time(hour = int(firstTime[0]), minute = int(firstTime[1]))
		
                secondTime = time2.split(":")
		self.datetime2 = datetime.time(hour = int(secondTime[0]), minute = int(secondTime[1]))		
	else:
		self.text = option
		

"""
NEW APPLICATION UPLOAD form
"""
class UploadForm(forms.Form):
    
    CHOICES = (
        (0, 'Inactive'),
        (1, 'Active')
    )
    
    appname = forms.CharField(label='App name', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
    status = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)
    manifest_id = forms.CharField(label='Manifest ID', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
    storage_id = forms.CharField(label='Storage ID', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
    plugin_id = forms.CharField(label='Plugin ID', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
    disk_format = forms.CharField(label='Disk format', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
    container_format = forms.CharField(label='Container format', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
    file_image = forms.FileField(required=True)
    
"""
API
"""

myClient = upr_client.UPRClient(constants.UPR_URL)
myPSARClient = psar_client.Client(constants.PSAR_URL)

class API():
    
    @staticmethod
    def authenticate(username, password):
        r = myClient.auth_user(username, password)
        if r.status_code == requests.codes.ok:
            return username
	return ''

    @staticmethod
    def getUserInfo(user_id):
	r = myClient.get_user_list(user_id)
	return r

    @staticmethod
    def getCreatedUsers(user_id):
	r = myClient.get_created_users(user_id)
	userList = json.loads(r.text)['users']
	return userList

    @staticmethod
    def getAssociatedGroups(user_id):
	r = myClient.get_user_groups(user_id)
	groupList = []
	groupJSON = json.loads(r.text)
        for group in groupJSON:
		groupList.append(group['group'])
	return groupList
    
    @staticmethod
    def getAllUserApplications(user_id, applications=None):
	if applications is None:
		applications = API.getStoreApplications(user_id=user_id)
	r = myClient.get_user_psa(user_id)
	finalList = []
	psaList = json.loads(r.text)
	for psa in psaList:
		app = {}
		app["id"] = psa["psa_id"]
		app['enabled'] = psa['active']
		app['running_order'] = psa['running_order']
		app["application"] = {}
		for application in applications:
			if application['id'] == app['id']:
				break
		app["application"]['name'] = application["name"]
		app["application"]['description'] = application["description"]
		app['application']['price'] = application['price']
		app['application']['is_capability'] = application['is_capability']
                app['application']['capabilities'] = application['capabilities']
		finalList.append(app)
	newList = sorted(finalList, key=itemgetter('running_order'))
        return newList
    
    @staticmethod
    def getCapabilities(user_id):
        capabilities_id = UserCapability.objects.filter(user_id=user_id).values_list('capability', flat=True).distinct()
        return Capability.objects.filter(id__in=capabilities_id)
    
    @staticmethod
    def saveEnabledAndOrderedApplications(user_id, ordered_apps, enabled_apps):
        #user_apps = UserApplication.objects.filter(user_id=user_id)
        appList = {}
	newList = []
	i = 1
	for appID in ordered_apps:
	    newApp = {}
	    newApp['psa_id'] = appID
	    if appID not in enabled_apps:
		newApp['active'] = False
		newApp['running_order'] = 0
	    else:
		newApp['active'] = True
		newApp['running_order'] = i
		i = i + 1
	    newList.append(newApp)
	appList['PSAList'] = json.dumps(newList)
	myClient.put_user_psa(user_id, data=json.dumps(appList))
                
    @staticmethod
    def getEnabledUserApplications(user_id):
	allCap = API.getAllCapabilities()
	capMap = {}
	for cap in allCap:
		capMap[cap['id']] = cap['name']
	r = myClient.get_user_psa(user_id)
        finalList = []
        psaList = json.loads(r.text)
        for psa in psaList:
		if psa['active'] == "True":
                	app = {}
	                app["id"] = psa["psa_id"]
        	        app['running_order'] = psa['running_order']
	                app["application"] = {}
	                rapp = myPSARClient.get_image_list(id=app["id"])
	                application = json.loads(rapp.text)[0]
	                app["application"]['name'] = application["psa_name"]
	                app['application']['price'] = application['cost']
			app['capabilities'] = []
	                capResp = myPSARClient.get_psa_capabilities(psa['psa_id'])
	                capList = json.loads(capResp.text)['capabilities']
			for cap in capList:
				newCap = {}
				newCap['id'] = cap
				newCap['name'] = capMap[cap]
				app['capabilities'].append(newCap)
	                finalList.append(app)
        newList = sorted(finalList, key=itemgetter('running_order'))
        return newList
        #return UserApplication.objects.filter(user_id=user_id, enabled=True).order_by("order")
    
    @staticmethod
    def getUserMSPL(user_id):
	r = myClient.get_mspl(target=user_id,editor=user_id,is_reconciled=False)
	msplList = json.loads(r.text)
	newList = []
	for mspl in msplList:
		newMspl = {}
		newMspl['id'] = mspl['mspl_id']
		newMspl['name'] = mspl['internalID']
		newMspl['capability'] = mspl['capability']
		newMspl['xml'] = base64.b64decode(mspl['mspl'])
		newList.append(newMspl)
        return newList
    
    @staticmethod
    def saveEnabledUserCapabilities(user_id, enabled_capabilities):
        user_capabilities = UserCapability.objects.filter(user_id=user_id)
        
        # Update checked app
        for capability in user_capabilities:
            if str(capability.id) in enabled_capabilities:
                capability.enabled = 1
            else:
                capability.enabled = 0
            capability.save()
    
    @staticmethod      
    def saveMSPL(user_id, mspl_id, mspl_title, mspl_xml):
        if mspl_id == 0:
            # New MSPL
	    utf8_parser = etree.XMLParser(encoding='utf-8')
	    root = etree.fromstring(mspl_xml.encode('utf-8'), parser=utf8_parser)
	    capability = root.find('{http://modeliosoft/xsddesigner/a22bd60b-ee3d-425c-8618-beb6a854051a/ITResource.xsd}configuration').find('{http://modeliosoft/xsddesigner/a22bd60b-ee3d-425c-8618-beb6a854051a/ITResource.xsd}capability').find('{http://modeliosoft/xsddesigner/a22bd60b-ee3d-425c-8618-beb6a854051a/ITResource.xsd}Name').text
	    r = myClient.create_mspl(user_id, user_id, capability, False, base64.b64encode(mspl_xml), internalID=mspl_title)
	    mspl = {}
            mspl['id'] = json.loads(r.text)['mspl_id']
            mspl['name'] = mspl_title
            mspl['capability'] = capability
            mspl['xml'] = mspl_xml
        else:
            # Update XML
	    myClient.delete_mspl(mspl_id)
	    utf8_parser = etree.XMLParser(encoding='utf-8')
	    root = etree.fromstring(mspl_xml.encode('utf-8'), parser=utf8_parser)
	    capability = root.find('{http://modeliosoft/xsddesigner/a22bd60b-ee3d-425c-8618-beb6a854051a/ITResource.xsd}configuration').find('{http://modeliosoft/xsddesigner/a22bd60b-ee3d-425c-8618-beb6a854051a/ITResource.xsd}capability').find('{http://modeliosoft/xsddesigner/a22bd60b-ee3d-425c-8618-beb6a854051a/ITResource.xsd}Name').text
	    r = myClient.create_mspl(user_id, user_id, capability, False, base64.b64encode(mspl_xml), internalID=mspl_title)
            mspl = {}
            mspl['id'] = json.loads(r.text)['mspl_id']
            mspl['name'] = mspl_title
            mspl['capability'] = capability
            mspl['xml'] = mspl_xml

        return mspl
        
    @staticmethod    
    def bindMSPLCapability(user_id, psa_id, mspl_id):
   	myClient.put_user_mspl_psa(user_id, psa_id, int(mspl_id))
 
    @staticmethod
    def getStoreApplications(user_id):
        r = myPSARClient.get_image_list()
	psaList = json.loads(r.text)
	applications = []
	for psa in psaList:
		app = {}
		app["id"] = psa['psa_id']
		app['name'] = psa['psa_name']
		app['description'] = psa['psa_description']
		app['is_capability'] = psa['is_generic']
		app['price'] = str(psa['cost'])
		capResp = myPSARClient.get_psa_capabilities(psa['psa_id'])
		app['capabilities'] = json.loads(capResp.text)['capabilities']
		applications.append(app)
	#all_user_apps_id = UserApplication.objects.filter(user_id=user_id).values_list('application')
        return applications
    
    @staticmethod
    def getAllCapabilities():
        r = myPSARClient.get_image_list(is_generic=True)
	capabilitiesList = json.loads(r.text)
	capabilities = []
	for capability in capabilitiesList:
		cap = {}
		cap["id"] = capability['psa_id']
		cap['name'] = capability['psa_name']
		capabilities.append(cap)
        return capabilities 
    
    @staticmethod
    def saveBoughtApps(user_id, store_apps, user_apps):
        # Load user
        #user = User.objects.get(pk=user_id)
        
        # Load user apps
        #db_user_apps = UserApplication.objects.filter(user_id=user_id)

	actual_app = API.getAllUserApplications(user_id)
       
	# Remove user apllications sold
	for app in actual_app:
	    if app["id"] not in user_apps:
		myClient.delete_user_psa(user_id, app["id"])		 
        
        for appId in store_apps:
		myClient.put_user_psa(user_id, psa_id=appId, active=False, running_order=0)
	return []	
        # Save new applications bought
        list_id = []
        for s_app_id in store_apps:
            s_app = Application.objects.get(pk=s_app_id)
            order = UserApplication.objects.filter(user_id=user_id).count() + 1
            u_app = UserApplication(user=user, application=s_app, enabled=0, order=order)
            u_app.save()
            list_id.append(u_app.id)
            for cap in s_app.capabilities.all():
                u_cap = UserCapability(user=user, capability=cap, enabled=0)
                u_cap.save()
                u_app.capabilities.add(u_cap)
            u_app.save()
            
        return list_id
    
    @staticmethod
    def getOptimizationLists():
        opt1 = Optimization.getOpt1List()
        opt2 = Optimization.getOpt2List()
        opt3 = Optimization.getOpt3List()
        
        return opt1, opt2, opt3
    
    @staticmethod
    def getUserOptimizations(user_id):
	r = myClient.get_user_opt_profile(user_id)
        #user_opt, created = Optimization.objects.get_or_create(user_id=user_id)
        return json.loads(r.text)['optimization_profile']
    
    @staticmethod
    def saveUserOptimizations(user_id, opt1):#, opt2, opt3):
        #user_opt = Optimization.objects.get(user_id=user_id)
        opt = Optimization.getOpt1List()
	myClient.update_user(user_id, optimization_profile=opt[int(opt1)]["constant"])
        #user_opt.opt1 = opt1
        #user_opt.opt2 = opt2
        #user_opt.opt3 = opt3
        #user_opt.save()
        
    @staticmethod
    def getCapabilityById(user_id, psa_id, cap_id):
	r = myClient.get_user_mspl_psa(user_id)
	msplList = json.loads(r.text)
	newList = sorted(msplList, key=itemgetter('timestamp'), reverse=True)
	for association in newList:
		if association['psa_id'] == psa_id:
			mspl = API.getMSPLById(user_id, association['mspl'])
			if mspl['capability'] == cap_id:
				return mspl
	return None
    
    @staticmethod
    def getMSPLById(user_id, mspl_id):
        msplList = API.getUserMSPL(user_id)
	for mspl in msplList:
		if mspl['id'] == int(mspl_id):
			return mspl
	return None
    
    @staticmethod
    def deleteMSPLById(mspl_id):
        myClient.delete_mspl(mspl_id)
 
    @staticmethod
    def getUserHSPL(user_id):
	r = myClient.get_hspl(editor=user_id)
	hsplList = json.loads(r.text)
	hspls = []
	for hspl in hsplList:
		newHSPL = HSPLClass(hspl)
		hspls.append(newHSPL)
        return hspls
    
    @staticmethod
    def saveHSPL(user_id, post_dict, logger, request):
        # HSPL id for this user in db + id for new HSPL
        hspl_list = API.getUserHSPL(user_id)
	if 'hspl' not in post_dict.keys():
	    return
	if len(post_dict['hspl']) is 0:
	    return
        for hspl in hspl_list:
	    hspl_id = hspl.id
            phrase = post_dict['hspl'][hspl_id]['subject'] + ";"
            target = post_dict['hspl'][hspl_id]['subject']
	    actionsList = HSPL.getActionList()
            for item in actionsList:
                if item['id'] == int(post_dict['hspl'][hspl_id]['action']):
                        phrase = phrase + item['value'] + ";"
                        break
            objectsList = HSPL.getObjectListStatic(post_dict['hspl'][hspl_id]['action'])
            for item in objectsList:
                if item['id'] == int(post_dict['hspl'][hspl_id]['object']):
                        phrase = phrase + item['value']
                        break
            conditionList = HSPL.getConditionListStatic(post_dict['hspl'][hspl_id]['object'])
            for conditionID in post_dict['hspl'][hspl_id]['condition'].keys():		
		if post_dict['hspl'][hspl_id]['condition'][conditionID] == "":
                        break
		for item in conditionList:
			if item['id'] == int(post_dict['hspl'][hspl_id]['condition'][conditionID]):
				if int(post_dict['hspl'][hspl_id]['condition'][conditionID]) == 1:
					phrase = phrase + ';('+item['value']+',' + str(post_dict['hspl'][hspl_id]['datetime1'][conditionID]) + "-" + str(post_dict['hspl'][hspl_id]['datetime2'][conditionID]) + ")"
					break
				elif int(post_dict['hspl'][hspl_id]['condition'][conditionID]) == 2:
					phrase = phrase + ";("+item['value']+"," + str(post_dict['hspl'][hspl_id]['text'][conditionID]) + ")"
					break
				elif int(post_dict['hspl'][hspl_id]['condition'][conditionID]) == 3:
	        	                phrase = phrase + ";("+item['value']+"," + str(post_dict['hspl'][hspl_id]['text'][conditionID]) + ")"
					break
				elif int(post_dict['hspl'][hspl_id]['condition'][conditionID]) == 4:
	        	                phrase = phrase + ";("+item['value']+"," + str(post_dict['hspl'][hspl_id]['text'][conditionID]) + ")"
					break
				elif int(post_dict['hspl'][hspl_id]['condition'][conditionID]) == 5:
		                        phrase = phrase + ";("+item['value']+"," + str(post_dict['hspl'][hspl_id]['text'][conditionID]) + ")"
					break
				elif int(post_dict['hspl'][hspl_id]['condition'][conditionID]) == 6:
	                	        phrase = phrase + ";("+item['value']+"," + str(post_dict['hspl'][hspl_id]['text'][conditionID]) + ")"
					break
				elif int(post_dict['hspl'][hspl_id]['condition'][conditionID]) == 7:
        	        	        phrase = phrase + ";("+item['value']+"," + str(post_dict['hspl'][hspl_id]['text'][conditionID]) + ")"
					break
				elif int(post_dict['hspl'][hspl_id]['condition'][conditionID]) == 8:
        	        	        phrase = phrase + ";("+item['value']+"," + str(post_dict['hspl'][hspl_id]['text'][conditionID]) + ")"
					break
				elif int(post_dict['hspl'][hspl_id]['condition'][conditionID]) == 9:
        	        	        phrase = phrase + ";("+item['value']+"," + str(post_dict['hspl'][hspl_id]['text'][conditionID]) + ")"
					break

	    if phrase != hspl.getString():
		myClient.delete_hspl(user_id, hspl_id)
		myClient.put_user_hspl(user_id, phrase, target)
            
	newHSPLnum = len(post_dict['hspl']) - len(hspl_list)
	index = 0
        index2 = -1
	while index < newHSPLnum:
	    hspl_id = index2
	    target = post_dict['hspl'][hspl_id]['subject']
	    phrase = post_dict['hspl'][hspl_id]['subject'] + ";"
            actionsList = HSPL.getActionList()
            for item in actionsList:
                if item['id'] == int(post_dict['hspl'][hspl_id]['action']):
                        phrase = phrase + item['value'] + ";"
                        break
            objectsList = HSPL.getObjectListStatic(post_dict['hspl'][hspl_id]['action'])
            for item in objectsList:
                if item['id'] == int(post_dict['hspl'][hspl_id]['object']):
                        phrase = phrase + item['value']
                        break

            conditionList = HSPL.getConditionListStatic(post_dict['hspl'][hspl_id]['object'])
            for conditionID in post_dict['hspl'][hspl_id]['condition'].keys():
                if post_dict['hspl'][hspl_id]['condition'][conditionID] == "":
                        break
                for item in conditionList:
                        if item['id'] == int(post_dict['hspl'][hspl_id]['condition'][conditionID]):
                                if int(post_dict['hspl'][hspl_id]['condition'][conditionID]) == 1:
                                        phrase = phrase + ';('+item['value']+',' + str(post_dict['hspl'][hspl_id]['datetime1'][conditionID]) + "-" + str(post_dict['hspl'][hspl_id]['datetime2'][conditionID]) + ")"
                                        break
                                elif int(post_dict['hspl'][hspl_id]['condition'][conditionID]) == 2:
                                        phrase = phrase + ";("+item['value']+"," + str(post_dict['hspl'][hspl_id]['text'][conditionID]) + ")"
                                        break
                                elif int(post_dict['hspl'][hspl_id]['condition'][conditionID]) == 3:
                                        phrase = phrase + ";("+item['value']+"," + str(post_dict['hspl'][hspl_id]['text'][conditionID]) + ")"
                                        break
                                elif int(post_dict['hspl'][hspl_id]['condition'][conditionID]) == 4:
                                        phrase = phrase + ";("+item['value']+"," + str(post_dict['hspl'][hspl_id]['text'][conditionID]) + ")"
                                        break
                                elif int(post_dict['hspl'][hspl_id]['condition'][conditionID]) == 5:
                                        phrase = phrase + ";("+item['value']+"," + str(post_dict['hspl'][hspl_id]['text'][conditionID]) + ")"
                                        break
                                elif int(post_dict['hspl'][hspl_id]['condition'][conditionID]) == 6:
                                        phrase = phrase + ";("+item['value']+"," + str(post_dict['hspl'][hspl_id]['text'][conditionID]) + ")"
                                        break
                                elif int(post_dict['hspl'][hspl_id]['condition'][conditionID]) == 7:
                                        phrase = phrase + ";("+item['value']+"," + str(post_dict['hspl'][hspl_id]['text'][conditionID]) + ")"
                                        break
				elif int(post_dict['hspl'][hspl_id]['condition'][conditionID]) == 8:
                                        phrase = phrase + ";("+item['value']+"," + str(post_dict['hspl'][hspl_id]['text'][conditionID]) + ")"
                                        break
				elif int(post_dict['hspl'][hspl_id]['condition'][conditionID]) == 9:
                                        phrase = phrase + ";("+item['value']+"," + str(post_dict['hspl'][hspl_id]['text'][conditionID]) + ")"
                                        break
                

            myClient.put_user_hspl(user_id, phrase, target)
	    index = index + 1
	    index2 = index2 - 1
           
                
    @staticmethod
    def deleteHSPLById(user_id, hspl_id):
        myClient.delete_hspl(user_id, hspl_id)
        
                
    @staticmethod
    def saveUsersAndGroups(request, user):
        addtype = request.GET['addtype']
        if addtype == 'user':
            username = request.POST['new_username']
            password = request.POST['new_password']
            if request.POST['new_usertype'] == '1':
	    	usertype = 'expert'
	    elif request.POST['new_usertype'] == '2':
		usertype = 'normal'
	    else:
		usertype = 'enthusiastic'
	    myClient.create_user(username, password, 1, usertype, True, False, False, creator=request.session['username'])
            #user = User(username=username, password=password, usertype=usertype)
            #user.save()
            request.session['message'] = {'type': 'messageSuccess', 'text': 'New user has been saved'}
        elif addtype == "group":
            name = request.POST['groupname']
	    myClient.create_group(name, "Description")
	    myClient.associate_user_group(name, user)
            request.session['message'] = {'type': 'messageSuccess', 'text': 'New group has been saved'}
	elif addtype == "delete":
	    username = request.POST['delete_username']
            myClient.delete_user(username)
            request.session['message'] = {'type': 'messageSuccess', 'text': 'User '+username+' has been deleted'}
	elif addtype == "association":
	    username = request.POST['associate_username']
	    groupname = request.POST['associate_group']
	    myClient.associate_user_group(groupname, username)
            request.session['message'] = {'type': 'messageSuccess', 'text': 'User '+username+' added to group '+groupname}

import json
import logging
import os
import workflow_manager
from workflow_manager_analysis import AnalysisWorkflowManager
from threading import Thread

from django import forms
from django.http import HttpResponse, QueryDict, JsonResponse
from django.views.decorators.http import require_http_methods, require_POST, require_GET
from django.shortcuts import render, redirect
from django.db import IntegrityError, transaction

from django.template.loader import render_to_string
from lxml import etree
import requests
from requests.exceptions import Timeout, ConnectionError
from models import UploadForm, HSPL, Condition, MSPL, Application, User, Group, UserApplication, UserCapability, Capability, Optimization, API
from constants import URL_IMAGE, PATH_JSON, TIMEOUT, MSPL_XML_SCHEMA, UPR_URL, SPM_URL, PSAR_URL
from modules.auth import keystone_auth, user_logout
from modules.exception import Unauthorized
from modules.service_graph import saveAndInstantiateServiceGraph
from modules.utils import handle_uploaded_file, get_filename, putNewAppToAPI
from modules.xml_validator import validate
from querystring_parser import parser
import sys

# Logger Instance
logger = logging.getLogger(__name__)

""" 
LOGIN
GET: login page
POST: login to keystone server
"""
@require_http_methods(["GET", "POST"])
def login(request):
	
	if request.method == 'GET':
		# Check auth
		if request.session.has_key('username'):
			return redirect("/app/")
		
		# Get login error message
		err_msg = ''
		if request.GET.has_key('err_message'):
			err_msg = request.GET['err_message']
		
		return render(request, 'login.html', {'title': 'Login', 'err_message': err_msg})
	
	elif request.method == 'POST':
		# Get data from form
		username = request.POST['username']
		password = request.POST['password']
		#usertype = int(request.POST['usertype'])
		token = 'admin'
		user_id = ''
		
		# Authentication
		try:
			user_id = API.authenticate(username=username, password=password)
		except requests.exceptions.Timeout:
			return redirect('/login/?err_message=Connection problem with UPR')
		if user_id == '':
			return redirect('/login/?err_message=Invalid Credentials')
		
		r = API.getUserInfo(username)
		userInfo = r.json()
		# Set session variables
		request.session['user_id']  = user_id
		request.session['username'] = username
		request.session['isAdmin'] = userInfo['is_admin']
		usertype = 0
		if userInfo['type'] == 'expert':
			request.session['usertype'] = 1
			usertype = 1
		elif userInfo['type'] == 'normal':
			request.session['usertype'] = 2
			usertype = 2
		else:
			request.session['usertype'] = 3
			usertype = 3
		
		# Session expires when Web browser is closed
		request.session.set_expiry(0)
		
		# LOG Info
		#logger.info('LOGIN - username: ' + username + ', usertype: ' + str(usertype))
		
		if usertype in [1,3]:
			return redirect('/app/')
		else:
			return redirect('/hspl/')


"""
LOGOUT
POST: logout user (clean user session)
"""
@require_http_methods(["GET", "POST"])
def logout(request):
	username = request.session['username']
	logger.info('LOGOUT - username: ' + username)
	callWfm = Thread(target=callWarkflowManager, kwargs={"username": username})
	callWfm.start()
	user_logout(request)
	return redirect('/login/')

def callWarkflowManager(username):
	token = ""
        upr_url = UPR_URL
        #upr_url = upr_url.replace("http://", '')
        #upr_url = upr_url.split(":")[0]
        wfm = workflow_manager.WorkflowManager(username, token, upr_url, SPM_URL, PSAR_URL)

"""
APPLICATIONS
GET: application list
POST: new capability, new application status
"""
@require_http_methods(["GET", "POST"])
def app(request):
	# Check authentication
	if not request.session.has_key('username') or not request.session.has_key('usertype'):
		return redirect("/login/")
	
	# Get username from session
	user_id  = request.session['user_id']
	username = request.session['username']
	usertype = request.session['usertype']
	
	# Check usertype
	if usertype not in [1,3]:
		user_logout(request)
		return redirect('/login/')
	
	if request.method == 'GET':
		# Response message from session
		response_message = ''
		if 'message' in request.session:
			response_message = request.session['message']
			del request.session['message']
		
		# Get all user applications
		applications = API.getAllUserApplications(user_id=user_id)
		#applications = []
		# Get all user capabilities
		capabilities = API.getAllCapabilities()
		#capabilities = []
		params = {'title': 'MyApps',
				  'usertype': usertype,
				  'response_message': response_message,
				  'apps': applications,
				  'caps': capabilities }
		
		return render(request, 'app.html', params)
	
	elif request.method == 'POST':
		# Load data from form and db
		ordered_apps = request.POST.getlist('app-order')
		enabled_apps = request.POST.getlist('app-actives')
		
		API.saveEnabledAndOrderedApplications(user_id=user_id, ordered_apps=ordered_apps, enabled_apps=enabled_apps)
		
		logger.info('APP - ' + username + ' saved apps')	
		request.session['message'] = {'type': 'messageSuccess', 'text': 'Customizations saved correctly'}
		
		return redirect('/app/')
	
	
"""
Capability view
"""
@require_http_methods(["GET", "POST"])
def capability(request):
	# Check auth
	if not request.session.has_key('username') or not request.session.has_key('usertype'):
		return redirect("/login/")
	
	# Get username from session
	user_id  = request.session['user_id']
	username = request.session['username']
	usertype = request.session['usertype']
	
	# Check usertype
	if usertype != 1:
		user_logout(request)
		return redirect('/login/')
	
	if request.method == 'GET':
		# Response message from session
		response_message = ''
		if 'message' in request.session:
			response_message = request.session['message']
			del request.session['message']
		
		# Load user enabled applications
		user_applications = API.getEnabledUserApplications(user_id=user_id)
		
		# Get all capabilities
		capabilities = API.getAllCapabilities()
		
		# Load all mspl (for dropdown menu)
		mspls = API.getUserMSPL(user_id=user_id)
		
		params = {'title': 'MyCapabilities',
				  'usertype': usertype,
				  'response_message': response_message,
				  'user_applications': user_applications,
				  'mspls': mspls,
				  'caps': capabilities}
		
		return render(request, 'capability.html', params)
	
	elif request.method == 'POST':
		# Load data from form and db
		#enabled_capabilities = request.POST.getlist('cap-active')
		#API.saveEnabledUserCapabilities(user_id=user_id, enabled_capabilities=enabled_capabilities)
		
		logger.info('APP - ' + username + ' saved capabilities')	
		request.session['message'] = {'type': 'messageSuccess', 'text': 'Customizations saved correctly'}
		
		return redirect('/capability/')


"""
MSPL view
"""
@require_http_methods(["GET", "POST"])
def mspl(request):
	# Check authentication
	if not request.session.has_key('username') or not request.session.has_key('usertype'):
		return redirect("/login/")
	
	# Get username from session
	user_id = request.session['user_id']
	username = request.session['username']
	usertype = request.session['usertype']
	
	# Check usertype
	if usertype != 1:
		user_logout(request)
		return redirect('/login/')
	
	if request.method == 'GET':
		# Response message from session
		message = ''
		if 'message' in request.session:
			message = request.session['message']
			del request.session['message']
			
		# All mspl filtered by username
		mspl_list = API.getUserMSPL(user_id=user_id)
		
		return render(request, 'MSPL.html', {'title': 'myMSPL', 'usertype': usertype, 'message': message, 'mspl_list': mspl_list })
			
		
	elif request.method == 'POST':
		# Get data from form
		mspl_id = int(request.POST['mspl_id'])
		mspl_title = request.POST['mspl_title'] 
		mspl_xml = request.POST['mspl_xml']
		
		# Validate XML before saving
		try:
			validate(mspl_xml, MSPL_XML_SCHEMA)
			mspl = API.saveMSPL(user_id=user_id, mspl_id=mspl_id, mspl_title=mspl_title, mspl_xml=mspl_xml)
			request.session['message'] = {'type': 'messageSuccess', 'text': 'MSPL has been saved'}
			# Bind mspl to capability
			if request.POST.has_key('cap_id'):
				if mspl['capability'] == request.POST['cap_id']:
					psa_id = request.POST['psa_id']
					API.bindMSPLCapability(user_id, psa_id, mspl['id'])
				else:
					request.session['message'] = {'type': 'messageError', 'text': 'MSPL has been saved but the capability is wrong'}	
			
		
		except etree.XMLSyntaxError as ex:
			logger.exception('MSPL')
			request.session['message'] = {'type': 'messageError', 'text': 'XML is invalid'}
		except:
			print "Unexpected error:", sys.exc_info()
			logger.exception('MSPL')
			request.session['message'] = {'type': 'messageError', 'text': 'XML is invalid'}
			
		return redirect(request.META['HTTP_REFERER'])
				
"""
IFA
"""
@require_http_methods(["GET"])
def ifa(request):
        token = ""
        set_debug = True
        username = request.session['username']
        wfm = AnalysisWorkflowManager(debug=set_debug)
	#Put here the code for IFA
#        try:
        r = wfm.ifa(username, token, UPR_URL, SPM_URL)
#        except Exception as ex:
#            error_type = type(ex).__name__
#            request.session['message'] = {'type': 'messageError', 'text': 'Error occured: ' + \
#                    str(wfm.DEBUG_MSG)}
	#Do not remove the redirect to MSPL
	return redirect("/mspl/")

"""
MIFA
"""
@require_http_methods(["GET"])
def mifa(request):
        token = ""
        set_debug = True
        username = request.session['username']
        print "Making sure all policy stack users have an AG..."
        callWarkflowManager(username)
        print "Beginning MIFA analysis"
        wfm = AnalysisWorkflowManager(debug=set_debug)
	#Put here the code for MIFA
        try:
            report = wfm.mifa(username, token, UPR_URL, SPM_URL)
            if report != None:
                return HttpResponse(str(report), status=200)

        except Exception as ex:
            error_type = type(ex).__name__
            request.session['message'] = {'type': 'messageError', 'text': 'Error occured: ' + \
                    str(wfm.DEBUG_MSG)}
	#Do not remove the redirect to MSPL
	return redirect("/mspl/")
				
"""
STORE
GET: get application store list
"""
@require_http_methods(["GET", "POST"])
def store(request):
	# Check authentication
	if not request.session.has_key('username') or not request.session.has_key('usertype'):
		return redirect("/login/")
	
	# Get username from session
	user_id = request.session['user_id']
	username = request.session['username']
	usertype = request.session['usertype']
	
	# Check usertype
	if usertype not in [1,3]:
		user_logout(request)
		return redirect('/login/')
	
	if request.method == 'GET':
		# Response message from session
		response_message = ''
		if request.session.has_key('message'):
			response_message = request.session['message']
			del request.session['message']

		# Applications
		
		store_apps = API.getStoreApplications(user_id=user_id)
		user_apps = API.getAllUserApplications(user_id=user_id, applications=store_apps)
		
		appsToBuy = []
		for app in store_apps:
			appsToBuy.append(app)
			for userApp in user_apps:
				if app["id"] == userApp["id"]:
					appsToBuy.pop()
					break	
		# Get all capabilities
		capabilities = API.getAllCapabilities()
		#capabilities = []

		# Parameters for response
		params = {'title': 'MyStore',
				  'usertype': usertype,
				  'response_message': response_message,
				  'store_apps': appsToBuy,
				  'user_apps': user_apps,
				  'caps': capabilities }	
				
		return render(request, 'store.html', params)
	
	elif request.method == 'POST':
		# Load currently bought app by user
		q_psa = QueryDict(request.POST['psa_ser'])
		store_apps = q_psa.getlist('store[]')
		user_apps  = q_psa.getlist('user[]')
		
		# Save
		list_id = API.saveBoughtApps(user_id=user_id, store_apps=store_apps, user_apps=user_apps)

		return JsonResponse({"type": 'success', "list": list_id }, status=200)


"""
STORE
GET: get application store list
"""
@require_http_methods(["GET", "POST"])
def optimization(request):
	# Check authentication
	if not request.session.has_key('username') or not request.session.has_key('usertype'):
		return redirect("/login/")
	
	# Get username from session
	user_id = request.session['user_id']
	username = request.session['username']
	usertype = request.session['usertype']
	
	# Check usertype
	if usertype != 1:
		user_logout(request)
		return redirect('/login/')
	
	if request.method == 'GET':
		# Response message from session
		response_message = ''
		if request.session.has_key('message'):
			response_message = request.session['message']
			del request.session['message']
		
		# Load all possible optimizations
		opt1, opt2, opt3 = API.getOptimizationLists()
		
		# Load user optimizations
		user_opt =API.getUserOptimizations(user_id=user_id)
		
		# Parameters for response
		params = {'title': 'MyOptimizations',
				  'usertype': usertype,
				  'response_message': response_message,
				  'opt1': opt1,
				  #'opt2': opt2,
				  #'opt3': opt3,
				  'user_opt': user_opt}
		
		return render(request, 'optimization.html', params)
	
	if request.method == 'POST':
		opt1 = request.POST['opt-1']
		#opt2 = request.POST['opt-2']
		#opt3 = request.POST['opt-3']
		
		# Load user optimizations
		API.saveUserOptimizations(user_id=user_id, opt1=opt1)#, opt2=opt2, opt3=opt3)
		
		request.session['message'] = {'type': 'messageSuccess', 'text': 'Optimizations saved correctly'}
		
		return redirect("/optimization/")

"""
HSPL view

"""
@require_http_methods(["GET", "POST"])
def hspl(request):
	# Check auth
	if not request.session.has_key('username') or not request.session.has_key('usertype'):
		return redirect("/login/")
	
	# Get username from session
	user_id = request.session['user_id']
	username = request.session['username']
	usertype = request.session['usertype']
	
	# Check usertype
	if usertype not in [2,3]:
		user_logout(request)
		return redirect('/login/')
	
	if request.method == 'GET':
		# Response message from session
		response_message = ''
		if 'message' in request.session:
			response_message = request.session['message']
			del request.session['message']
		
		# Get created user
		createdUserList = API.getCreatedUsers(user_id=user_id)

		# Get data
		hspls = API.getUserHSPL(user_id=user_id)
		actions = HSPL.getActionList()

		return render(request, 'HSPL.html', {'title': 'HSPL', 'username' : username, 'is_admin' : request.session['isAdmin'], 'usertype': usertype, 'createdUser': createdUserList, 'response_message': response_message, 'hspls': hspls, 'actions': actions})
	
	elif request.method == 'POST':
		# Parsing POST
		post_dict = parser.parse(request.POST.urlencode())
		
		API.saveHSPL(user_id=user_id, post_dict=post_dict, logger=logger, request=request)
			
		if not request.session.has_key('message'):
			request.session['message'] = {'type': 'messageSuccess', 'text': 'HSPL saved'}
                                              
				
		return redirect('/hspl/')


"""
USERS
GET: validate single MSPL xml
POST: add new user
"""
def users(request):
	# Check auth
	if not request.session.has_key('username') or not request.session.has_key('usertype'):
		return redirect("/login/")
	
	# Response message from session
	response_message = ''
	if request.session.has_key('message'):
		response_message = request.session['message']
		del request.session['message']
	
	# Get username from session
	username = request.session['username']
	usertype = request.session['usertype']
	
	if request.method == 'GET':
        	createdUserList = API.getCreatedUsers(user_id=username)
		createdGroupList = API.getAssociatedGroups(user_id=username)
		return render(request, 'users.html', {'createdGroup': createdGroupList, 'username': username, 'createdUser': createdUserList,'title': 'Users', 'usertype': usertype, 'message':response_message})	
	elif request.method == 'POST':
		API.saveUsersAndGroups(request, username)
		return redirect('/users/')



"""
USER IMAGE UPLOAD
GET: get upload application form
POST: post new app to server
"""
@require_http_methods(["GET", "POST"])
def user_image_upload(request):
	# Check authentication
	if "username" not in request.session:
		return redirect("/login/")
	
	if request.method == 'GET':
		form = UploadForm()
		return render(request, 'upload.html', { 'title': 'Upload', 'form': form })
	
	elif request.method == 'POST':
		form = UploadForm(request.POST, request.FILES)

		if not form.is_valid():
			return render(request, 'upload.html', { 'title': 'Upload', 'form': form, 'response_message': 'fail' })
		
		# Handle file
		fpath = handle_uploaded_file(request.FILES['file_image'])
		fname = get_filename(request.FILES['file_image'].name)
		
		# Send file to API
		params = {
				"id": fname,
				"name": form.cleaned_data['appname'],
				"status": form.cleaned_data['status'],
				"manifest_id": form.cleaned_data['manifest_id'],
				"storage_id": form.cleaned_data['storage_id'],
				"plugin_id": form.cleaned_data['plugin_id'],
				"disk_format": form.cleaned_data['disk_format'],
				"container_format": form.cleaned_data['container_format'],
				}
		files = {"image": open(fpath, 'rb')}
		
		try:
			putNewAppToAPI(fname, files, params)
			request.session['upload_status'] = 'success'
		except requests.exceptions.HTTPError:
			return render(request, 'upload.html', { 'title': 'Upload', 'form': form, 'response_message': 'fail' })
			
		# Delete file
		os.remove(fpath)
		
		return redirect('/store/')
	
	
	

"""  UTILITY FUNCTIONS """


"""
APP MSPL (AJAX method)
GET (param app_id): mspl associate to application
"""
@require_GET
def app_mspl(request):
	# Check authentication
	if not request.session.has_key('username'):
		return HttpResponse('Unauthorized', status=401)
	
	if not request.is_ajax():
		return HttpResponse('Bad Request', status=400)
	
	# Get mspl associated with capability
	cap_id = request.GET['cap_id']
	psa_id = request.GET['psa_id']
	mspl = API.getCapabilityById(request.session['username'], psa_id, cap_id)
	if mspl == None:
		return JsonResponse({"id": 0, "title": "", "xml": ""})
	else:
		return JsonResponse({"id": mspl['id'], "title": mspl['name'], "xml": mspl['xml']})
	

"""
MSPL ID (AJAX method)
GET: retrive single mspl by mspl id
"""
@require_GET
def mspl_id(request):
	if "username" not in request.session:
                return redirect("/login/")
	# Check auth
	if not request.is_ajax():
		return HttpResponse('Bad Request', status=400)
	
	mspl_id = int(request.GET['mspl_id'])
	if mspl_id == 0:
		return JsonResponse({"id": "", "title": "", "xml": ""})
	else:
		mspl = API.getMSPLById(user_id = request.session['username'], mspl_id=mspl_id)
		return JsonResponse({"id": mspl_id, "title": mspl['name'], "xml": mspl['xml']})
	

"""
MSPL DELETE
POST: delete single MSPL by passing mspl_id
"""
@require_POST
def mspl_delete(request):
	# Get MSPL instance
	mspl_id = int(request.POST['mspl_id'])
	
	# Delete MSPL
	API.deleteMSPLById(mspl_id=mspl_id)
	
	return redirect('/mspl/')


"""
MSPL VALIDATE (AJAX method)
GET: validate single MSPL xml
"""
@require_POST
def mspl_validate(request):
	# Check auth
	if not request.is_ajax():
		return HttpResponse('Bad Request', status=400)

	mspl_xml = request.POST['mspl_xml']
	try:
		validate(mspl_xml, MSPL_XML_SCHEMA)
	except etree.XMLSyntaxError as ex:
		return JsonResponse({"type":"error", "message": ex.message}, status=200)
	except:
		return JsonResponse({"type":"error", "message": "General error"}, status=200)
	
	return JsonResponse({"type":"valid", "message": "XML is correct"}, status=200)

"""
SFA VALIDATE (AJAX method)
GET: validate single MSPL xml
"""
@require_POST
def sfa_validate(request):
	# Check auth
	if not request.is_ajax():
		return HttpResponse('Bad Request', status=400)

	mspl_xml = request.POST['mspl_xml']
        print "MSPL XML is " + str(mspl_xml)

        set_debug = True
        username = request.session['username']
        wfm = AnalysisWorkflowManager(debug=set_debug)
        print "Running SFA"
        try:
            print "ok"
            validate(mspl_xml, MSPL_XML_SCHEMA)
            print "validated"
            report = wfm.sfa(username, "password", mspl_xml, UPR_URL, SPM_URL)
            print "done"
            print str(report)
            return HttpResponse(str(report), status=200)

        except etree.XMLSyntaxError as ex:
            print "Bad"
            return JsonResponse({"type":"error", "message": "Bad XML format"}, status=200)
 
#        except Exception as ex:
#            error_type = type(ex).__name__
#            return JsonResponse({'type': 'error', 'message': 'Error occured: ' + str(error_type) + " " +  str(wfm.DEBUG_MSG) + "'"}, status=200)

        print "Executing something elsed"
	return JsonResponse({"type":"valid", "message": "Configuration is correct"}, status=200)

"""
HSPL NEW (AJAX method)
GET: get new hspl box
"""
@require_GET
def hspl_new(request):
	
	if not request.is_ajax():
		return HttpResponse('Bad Request', status=400)
	
	username = request.session['username']
	createdUserList = API.getCreatedUsers(user_id=username)
	hspl_id = request.GET['hspl_id']
	actions = HSPL.getActionList()
	html = render_to_string('newHSPL.html', {'hspl_id': hspl_id, 'actions': actions, 'createdUsers': createdUserList, 'username': username})
	
	return HttpResponse(html)


"""
HSPL DELETE (AJAX method)
POST: delete HSPL
"""
@require_POST
def hspl_delete(request):
	
	if not request.is_ajax():
		return HttpResponse('Bad Request', status=400)
	
	hspl_id = request.POST['hspl_id']
	API.deleteHSPLById(request.session['username'], hspl_id=hspl_id)
	
	return HttpResponse('success')

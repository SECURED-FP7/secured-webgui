import json
import requests

from webContent.constants import URL_AUTH_V2, TIMEOUT
from exception import Unauthorized


def keystone_auth(username, password, tenant='admin'):
	# Authentication json
	tenant = username
	datajs = {"auth": {"tenantName": tenant, "passwordCredentials": {"username": username, "password": password}}}
	headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
	
	# Authentication request
	resp = requests.post(URL_AUTH_V2, data=json.dumps(datajs), headers=headers, timeout=TIMEOUT)
	if resp.status_code == 401:
		raise Unauthorized('Keystone returns 401 Unauthorized')
	
	resp.raise_for_status()
	js_response = json.loads(resp.text)
	
	return js_response["access"]["token"]["id"], js_response["access"]["user"]["id"]

def user_logout(request):
	request.session.flush()

from requests import get, put, post, delete
import json
class UPRClient:
	def __init__(self,base_URL):
		self.base_URL=base_URL+'/v1/upr/'
		self.headers={"Accept":'application/json','Content-type':'application/json'}		

	def create_user(self, user_id, password, integrityLevel, type, 
			is_cooperative, is_infrastructure, is_admin,token=None, creator=None,
			optimization_profile=None):
		url=self.base_URL+'users/'
		data={}
                if token is not None:
                       data['token']=token
		data['user_id']=user_id
		data['password']=password
		data['integrityLevel']=integrityLevel
		data['is_cooperative']=is_cooperative
		data['is_infrastructure']=is_infrastructure
		data['is_admin']=is_admin
		if creator:
			data['creator']=creator
		data['type']=type
		if optimization_profile:
			data['optimization_profile']=optimization_profile
		r=post(url,data=json.dumps(data),headers=self.headers)
		return r

	def get_user_list(self,user_id=None, token=None):
		url=self.base_URL+'users/'
		params={}
                if token is not None:
                        params['token']=token

		if user_id is not None:
			params['user_id']=user_id

		r=get(url, params=params)
		return r

	def get_user_type(self, user_id, token=None):
		url=self.base_URL+'users/'+user_id+'/UserType/'
                params={}
                if token is not None:
                        params['token']=token

		r=get(url, params=params)
		return r	
	def get_user_creator(self, user_id, token=None):
		url=self.base_URL+'users/'+user_id+'/Creator/'
                params={}
                if token is not None:
                        params['token']=token

		r=get(url, params=params)
		return r	
	def get_user_opt_profile(self, user_id,token=None):
		url=self.base_URL+'users/'+user_id+'/OptProfile/'
                params={}
                if token is not None:
                        params['token']=token

		r=get(url, params=params)
		return r	
	def get_user_groups(self, user_id, token=None):
		url=self.base_URL+'users/'+user_id+'/Groups/'
                params={}
                if token is not None:
                        params['token']=token

		return get(url,params=params)
	def get_created_users(self,user_id, token=None):		
		url=self.base_URL+'users/'+user_id+'/CreatedUsers/'
                params={}
                if token is not None:
                        params['token']=token

		return get(url, params=params)
	
	def auth_user(self, user , password, token=None):
		url=self.base_URL+'users/auth/'
		data={}
                if token is not None:
                        params['token']=token
		data['username']=user
		data['password']=password

		r=post(url,data=json.dumps(data),headers=self.headers)
		return r
	def update_user(self, user_id,  name=None, password=None, integrityLevel=None, type=None, 
                        is_cooperative=None, is_infrastructure=None, is_admin=None, creator=None, token=None):
		url=self.base_URL+'users/'+str(user_id)+'/'
		
		data={}
                if token is not None:
                        params['token']=token

		if name is not None:
			data['name']=name
		if password is not None:
			data['password']=password
		if integrityLevel is not None:
			data['integrityLevel']=integrityLevel
		if is_cooperative is not None:
			data['is_cooperative']=is_cooperative
		if is_infrastructure is not None:
			data['is_infrastructure']=is_infrastructure
		if is_admin is not None:
			data['is_admin']=is_admin
		if creator is not None:
			data['creator']=creator
		
		r=put(url, data=json.dumps(data),headers=self.headers)
		return r

	def delete_user(self,user_id, token=None):
		url=self.base_URL+'users/'+str(user_id)+'/'
                params={}
                if token is not None:
                        params['token']=token

		r=delete(url, params=params)
		return r

	def get_user_psa(self,user_id,is_active=None, token=None):
		url=self.base_URL+'users/'+str(user_id)+'/PSA/'
		params={}
                if token is not None:
                        params['token']=token

		if is_active is not None:
			params['is_active']=is_active
		return get(url,params=params)
	def put_user_psa(self,user_id,data=None,psa_id=None,active=None,running_order=None, token=None):
		"""
		Data must be in the form accepted by the UPR
		{'PSAList':[
                                {
                                        'psa_id':'12345',
                                        'active':true,
                                        'running_order':2
                                },
                                {
                                        'psa_id':'54321',
                                        'active':false,
                                        'running_order':1
                                }
                           ]
                        }
		"""
		url=self.base_URL+'users/'+str(user_id)+'/PSA/'
		if data:
			return put(url,data=data,headers=self.headers)
		else:
			psa_list={}
	                if token is not None:
        	               psa_list['token']=token
				
			psas=[]
			psa={}
			psa['psa_id']=psa_id
			psa['active']=active
			psa['running_order']=running_order
			psas=psas+[psa]
			psa_list['PSAList']=json.dumps(psas)
			return put(url,data=json.dumps(psa_list),headers=self.headers)
		
	def delete_user_psa(self,user_id,psa_id, token=None):
		url=self.base_URL+'users/'+str(user_id)+'/PSA/'
		params={}
                if token is not None:
                       params['token']=token
		params['psa_id']=str(psa_id)
		return delete(url,params=params)
	
	def get_hspl(self,target=None,editor=None, token=None):
		url=self.base_URL+'HSPL/'
		params={}
                if token is not None:
                       params['token']=token

		if target is not None:
			params['target']=target
		if editor is not None:
			params['editor']=editor

		return get(url,params=params)
	def delete_hspl(self,user_id,hspl_id, token=None):
		url=self.base_URL+'HSPL/'
		params={}
                if token is not None:
                       params['token']=token

		params['hspl_id']=hspl_id
		return delete(url,params=params)		

	def put_user_hspl(self, user_id, hspl, target, token=None):
		url=self.base_URL+'users/'+user_id+'/HSPL/'		
		data={}
                if token is not None:
                       data['token']=token

		data['hspl']=hspl
		data['target']=target
		return put(url,data=json.dumps(data),headers=self.headers)

	def create_group(self, name, description, token=None):
		url=self.base_URL+'groups/'
		data={}
                if token is not None:
                       data['token']=token
		data['name']=name
		data['description']=description
		return post(url,data=json.dumps(data),headers=self.headers)
	
	def list_group(self,token=None):
		url=self.base_URL+'groups/'
                params={}
                if token is not None:
                       params['token']=token

		return get(url, params=params)
		
	def delete_group(self, group_id,token=None):
		url=self.base_URL+'groups/'+group_id+'/'
		params={}
                if token is not None:
                       params['token']=token

		return delete(url, params=params)

	def update_group(self, group, description=None,token=None):
		url=self.base_URL+'groups/'+group+'/'
		data={}
                if token is not None:
                       params['token']=token

		if description:
			data['description']=description
		return put(url,data=json.dumps(data),headers=self.headers)

	def list_user_group(self,group,token=None):
		url=self.base_URL+'groups/'+group+'/users/'
                params={}
                if token is not None:
                       params['token']=token

                return get(url, params=params)

	def associate_user_group(self, group, user_id,token=None):
		url=self.base_URL+'groups/'+group+'/users/'
		data={}
                if token is not None:
                       data['token']=token

		data['user_id']=user_id
		return put(url,data=json.dumps(data),headers=self.headers)

	def delete_user_group(self, user, group,token=None):
		url=self.base_URL+'groups/'+group+'/users/'
		params={}
                if token is not None:
                       params['token']=token

		params['user_id']=user
		return delete(url,params=params)
	
	def get_group_psa(self, group,token=None):
		url=self.base_URL+'groups/'+group+'/PSA/'
                params={}
                if token is not None:
                       params['token']=token

		return get(url, params=params)

	def put_group_psa(self, group, psa_id,token=None):
		url=self.base_URL+'groups/'+group+'/PSA/'
		data={}
                if token is not None:
                       data['token']=token

		data['psa_id']=psa_id
		return put(url,data=json.dumps(data),headers=self.headers)

	def delete_group_psa(self,group,psa_id,token=None):		
		url=self.base_URL+'groups/'+group+'/PSA/'
		params={}
                if token is not None:
                       params['token']=token
		params['psa_id']=psa_id
		return delete(url,params=params)

	#MSPL

	def get_mspl(self,internalID=None,target=None,editor=None,is_reconciled=False,token=None):
		url=self.base_URL+'MSPL/'
		params={}
                if token is not None:
                       params['token']=token

		if internalID:
			params['internalID']=internalID
		if target:
			params['target']=target
		if editor:
			params['editor']=editor
		if is_reconciled:
			params['is_reconciled']=is_reconciled
		return get(url,params=params)
	
	def create_mspl(self,target,editor,capability,is_reconciled,mspl,internalID=None,token=None):
		url=self.base_URL+'MSPL/'
		data={}
                if token is not None:
                       data['token']=token
		data['target']=target
		data['editor']=editor
		data['capability']=capability
		data['is_reconciled']=is_reconciled
		data['mspl']=mspl
		if internalID:
			data['internalID']=internalID
		return post(url,data=json.dumps(data),headers=self.headers)

	def delete_mspl(self,mspl_id=None,target=None,editor=None,capability=None,is_reconciled=None,token=None):
		url=self.base_URL+'MSPL/'
		params={}
                if token is not None:
                       params['token']=token

		if mspl_id:
			params['mspl_id']=mspl_id
			return delete(url,params=params)
		if target:
			params['target']=target
		if editor:
			params['editor']=editor
		if capability:
			params['capability']=capability
		if is_reconciled is not None:
			params['is_reconciled']=is_reconciled
		return delete(url,params=params)

	def put_user_mspl_psa(self,user_id,psa_id,mspl_id,token=None):
		url=self.base_URL+'users/'+user_id+'/MSPL/'
		
		#json_data=json.loads('{"MSPL":[{"psa_id":'+str(psa_id)+',"mspl_id":'+str(mspl_id)+'}]}')
		
		data={}
                if token is not None:
                       data['token']=token

		mspls=[]
		mspl={}
		mspl["psa_id"]=str(psa_id)
		mspl["mspl_id"]=mspl_id
		mspls=mspls+[mspl]
		data["MSPL"]=json.dumps(mspls)
		print data
		#headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
		return put(url,data=json.dumps(data),headers=self.headers)


	def get_user_mspl_psa(self,user_id ,token=None):
		url=self.base_URL+'users/'+user_id+'/MSPL/'
                params={}
                if token is not None:
                       params['token']=token

		return get(url, params=params)

	#AG
	def get_user_ag(self,target,editor=None,token=None):
		url=self.base_URL+'users/'+target+'/AG'
		params={}
                if token is not None:
                       params['token']=token

		if editor:
			params['editor']=editor
		return get(url,params=params)
	def delete_user_ag(self,target,editor,token=None):
		url=self.base_URL+'users/'+target+'/AG'
		params={}
                if token is not None:
                       params['token']=token

		params['editor']=editor
		return delete(url,params=params)
	def post_ag(self,target_id,editor_id,ag,token=None):
		url=self.base_URL+'users/AG/'
		data={}
                if token is not None:
                       data['token']=token

		data['target_id']=target_id
		if editor_id is not None:
	                data['editor_id']=editor_id
		else:
			data['editor_id']=target_id
		data['application_graph']=ag
		return post(url,data=json.dumps(data),headers=self.headers)
	#RAG
	def get_user_rag(self,user_id,token=None):
		url=self.base_URL+'users/'+user_id+'/RAG'
                params={}
                if token is not None:
                       params['token']=token

		return get(url, params=params)
	def delete_user_rag(self,user_id,token=None):
		url=self.base_URL+'users/'+user_id+'/RAG'
                params={}
                if token is not None:
                       params['token']=token

		return delete(url, params=params)
	def post_rag(self,target_id,ned_info,rag,token=None):
		url=self.base_URL+'users/RAG/'
		data={}
                if token is not None:
                       data['token']=token

		data['target_id']=target_id
		data['ned_info']=ned_info
		data['reconcile_application_graph']=rag
		return post(url,data=json.dumps(data),headers=self.headers)

	#Low Level
	def get_user_psaconf(self,user_id,psa_id=None,token=None):
		url=self.base_URL+'users/'+user_id+'/PSAConf/'
		params={}
                if token is not None:
                       params['token']=token

		if psa_id:
			params['psa_id']=psa_id
		return get(url,params=params)
	def post_psaconf(self,user_id,psa_id,configuration,token=None):
		url=self.base_URL+'users/'+user_id+'/PSAConf/'
		data={}
                if token is not None:
                       data['token']=token

		data['psa_id']=psa_id
		data['configuration']=configuration
		return post(url,data=json.dumps(data),headers=self.headers)
	def delete_user_psaconf(self,user_id,psa_id,token=None):
		url=self.base_URL+'users/'+user_id+'/PSAConf/'
		params={}
                if token is not None:
                       params['token']=token
		params['psa_id']=psa_id
		return delete(url,params=params)		
	#Executed PSA
	def delete_executed_psa(self,user_id,psa_id,token=None):
		url=self.base_URL+'users/'+user_id+'/ExecutePSA/'
		params={}
                if token is not None:
                       params['token']=token
		params['psa_id']=psa_id
		return delete(url,params=params)
		
	def get_executed_psa(self,user_id,token=None):
		url=self.base_URL+'users/'+user_id+'/ExecutePSA/'
                params={}
                if token is not None:
                       params['token']=token
		return get(url, params=params)
	def put_executed_psa(self,user_id,psa_id,token=None):
		url=self.base_URL+'users/'+user_id+'/ExecutePSA/'
		data={}
                if token is not None:
                       data['token']=token
		data['psa_id']=psa_id
		print data
		return put(url,data=json.dumps(data),headers=self.headers)


	#Reconciliation Report

	def get_reconciliation_report(self,user_id,ned_info=None,token=None):
		url=self.base_URL+'users/'+user_id+'/reconciliation_report/'
		params={}
                if token is not None:
                       params['token']=token
		if ned_info:
			params['ned_info']=ned_info
		return get(url,params=params)

	def post_reconciliation_report(self,user_id,ned_info,reconciliation_report,token=None):
		url=self.base_URL+'users/'+user_id+'/reconciliation_report/'
		data={}
                if token is not None:
                       data['token']=token
		data['ned_info']=ned_info
		data['reconciliation_report']=reconciliation_report
		return post(url,data=data)
	
	def delete_reconciliation_report(self,user_id,ned_info=None,token=None):
		url=self.base_URL+'users/'+user_id+'/reconciliation_report/'
		params={}
                if token is not None:
                       params['token']=token

		if ned_info:
			params['ned_info']=ned_info

		return delete(url,params=params)		

       #SFA report

        def get_sfa(self,user_id,mspl_id,token=None):
                url=self.base_URL+'users/'+user_id+'/sfa_report/'
                params={}
                if token is not None:
                       params['token']=token
		params['mspl_id']=mspl_id
                return get(url,params=params)

        def post_sfa(self,user_id,mspl_id,sfa_report,token=None):
                url=self.base_URL+'users/'+user_id+'/sfa_report/'
                data={}
                if token is not None:
                       data['token']=token
                data['mspl_id']=mspl_id
                data['sfa_report']=sfa_report
                return post(url,data=data)

        def delete_sfa(self,user_id,mspl_id,token=None):
                url=self.base_URL+'users/'+user_id+'/sfa_report/'
                params={}
                if token is not None:
                       params['token']=token
		params['mspl_id']=mspl_id
                return delete(url,params=params)


        #IFA report

        def get_ifa(self,user_id,token=None):
                url=self.base_URL+'users/'+user_id+'/ifa_report/'
                params={}
                if token is not None:
                       params['token']=token
                return get(url,params=params)

        def post_ifa(self,user_id,ifa_report,token=None):
                url=self.base_URL+'users/'+user_id+'/ifa_report/'
                data={}
                if token is not None:
                       data['token']=token
                data['ifa_report']=ifa_report
                return post(url,data=data)

        def delete_ifa(self,user_id,token=None):
                url=self.base_URL+'users/'+user_id+'/ifa_report/'
                params={}
                if token is not None:
                       params['token']=token
                return delete(url,params=params)

        #MIFA report

        def get_mifa(self,user_id,token=None):
                url=self.base_URL+'users/'+user_id+'/mifa_report/'
                params={}
                if token is not None:
                       params['token']=token
                return get(url,params=params)

        def post_mifa(self,user_id,mifa_report,token=None):
                url=self.base_URL+'users/'+user_id+'/mifa_report/'
                data={}
                if token is not None:
                       data['token']=token
                data['mifa_report']=mifa_report
                return post(url,data=data)

        def delete_mifa(self,user_id,token=None):
                url=self.base_URL+'users/'+user_id+'/mifa_report/'
                params={}
                if token is not None:
                       params['token']=token
                return delete(url,params=params)



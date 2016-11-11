from django import forms
from django.db import models

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction


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
    
    
class Optimization(models.Model):
    
    OPT1_CHOICES = (
        (0, 'None'),
        (1, 'Optimize for speed'),
        (2, 'Optimize for latency'),
        (3, 'Minimize network bandwith consumption')
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
            list.append({'id': opt[0], 'value': opt[1]})
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
class Condition(models.Model):
    
    CONDITION_CHOICES = (
        (1, 'time period'),
        (2, 'traffic target'),
        (3, 'specific URL'),
        (4, 'type of content'),
        (5, 'purpose'),
        (6, 'bandwidth value'),
        (7, 'resource value'),
    )
    
    condition = models.IntegerField(choices=CONDITION_CHOICES)
    text = models.CharField(max_length=255, null=True)
    number = models.FloatField(null=True)
    datetime1 = models.TimeField(null=True)
    datetime2 = models.TimeField(null=True)


class HSPL(models.Model):
    
    ACTION_CHOICES = (
        (1, 'is/are not authorized to access'),
        (2, 'is/are authorized to access'),
        (3, 'enable(s)'),
        (4, 'remove(s)'),
        (5, 'reduce(s)'),
        (6, 'check(s) over'),
        (7, 'count(s)'),
        (8, 'protect(s) confidentiality'),
        (9, 'protect(s) integrity'),
        (10, 'protect(s) confidentiality integrity')
    )
    
    OBJECT_CHOICES = (
        (1, 'VOIP traffic'),
        (2, 'P2P traffic'),
        (3, '3G/4G traffic'),
        (4, 'Internet traffic'),
        (5, 'intranet traffic'),
        (6, 'DNS traffic'),
        (7, 'all traffic'),
        (8, 'public identity'),
        (9, 'Resource x'),
        (10, 'file scanning'),
        (11, 'email scanning'),
        (12, 'antivirus'),
        (13, 'basic parental control'),
        (14, 'advanced parental control'),
        (15, 'IDS/IPS'),
        (16, 'DDos attack protection'),
        (17, 'tracking techniques'),
        (18, 'advertisement'),
        (19, 'bandwidth'),
        (20, 'security status'),
        (21, 'connection'),
        (22, 'logging'),
    )
    
    ENABLE_OBJECT = {1: [1,2,3,4,5,6,7,9], 
                     2: [1,2,3,4,5,6,7,9],
                     3: [10,11,12,13,14,15,16,22],
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
                    13: None,
                    14: [1,4],
                    15: [2],
                    16: [2],
                    17: [3],
                    18: [3],
                    19: [1,3,6],
                    20: None,
                    21: [1,3],
                    22: [1,2,3,4]}
    
    user      = models.ForeignKey(User, on_delete=models.CASCADE, default=0)
    subject   = models.CharField(max_length=100)
    action    = models.IntegerField(choices=ACTION_CHOICES)
    object    = models.IntegerField(choices=OBJECT_CHOICES)
    condition = models.ManyToManyField(Condition)
    
    @staticmethod
    def getActionList():
        list = []
        for hspl in HSPL.ACTION_CHOICES:
            list.append({'id': hspl[0], 'value': hspl[1]})
        return list
    
    def getObjectList(self):
        list = []
        list_objects_id = self.ENABLE_OBJECT[self.action]
        for hspl in HSPL.OBJECT_CHOICES:
            if hspl[0] in list_objects_id:
                list.append({'id': hspl[0], 'value': hspl[1]})
        return list
    
    def getConditionList(self):
        list = []
        list_conditions_id = self.ENABLE_CONDITION[self.object]
        for cond in Condition.CONDITION_CHOICES:
            if cond[0] in list_conditions_id:
                list.append({'id': cond[0], 'value': cond[1]})
        return list
    

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
class API():
    
    @staticmethod
    def authenticate(username, password):
        try:
            user = User.objects.get(username=username, password=password)
        except User.DoesNotExist:
            raise Unauthorized('401 Unauthorized')
        
        return user.id
    
    @staticmethod
    def getAllUserApplications(user_id):
        return UserApplication.objects.filter(user_id=user_id).order_by("order")
    
    @staticmethod
    def getCapabilities(user_id):
        capabilities_id = UserCapability.objects.filter(user_id=user_id).values_list('capability', flat=True).distinct()
        return Capability.objects.filter(id__in=capabilities_id)
    
    @staticmethod
    def saveEnabledAndOrderedApplications(user_id, ordered_apps, enabled_apps):
        user_apps = UserApplication.objects.filter(user_id=user_id)
        
        # Update checked app
        for app in user_apps:
            if str(app.id) in enabled_apps:
                app.enabled = 1
            else:
                app.enabled = 0
            app.save()
        
        # Update ordered app
        for app in user_apps:
            i = 0
            for id_oapp in ordered_apps:
                i += 1
                if int(app.id) == int(id_oapp):
                    app.order = i
                    app.save()
                    break
                
    @staticmethod
    def getEnabledUserApplications(user_id):
        return UserApplication.objects.filter(user_id=user_id, enabled=True).order_by("order")
    
    @staticmethod
    def getUserMSPL(user_id):
        return MSPL.objects.filter(user_id=user_id)
    
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
            mspl = MSPL(user_id=user_id, title=mspl_title, xml=mspl_xml)
        else:
            # Update XML
            mspl = MSPL.objects.get(pk=mspl_id)
            mspl.title = mspl_title
            mspl.xml = mspl_xml
            
        mspl.save()
        
        return mspl
        
    @staticmethod    
    def bindMSPLCapability(cap_id, mspl):
        capability = UserCapability.objects.get(pk=cap_id)
        capability.mspl = mspl
        capability.save()
    
    @staticmethod
    def getStoreApplications(user_id):
        all_user_apps_id = UserApplication.objects.filter(user_id=user_id).values_list('application')
        return Application.objects.exclude(id__in=all_user_apps_id)
    
    @staticmethod
    def getAllCapabilities():
        capabilities_id = UserCapability.objects.all().values_list('capability', flat=True).distinct()
        return Capability.objects.filter(id__in=capabilities_id)
    
    @staticmethod
    def saveBoughtApps(user_id, store_apps, user_apps):
        # Load user
        user = User.objects.get(pk=user_id)
        
        # Load user apps
        db_user_apps = UserApplication.objects.filter(user_id=user_id)
        
        # Remove user apllications sold
        for u_app in db_user_apps:
            if str(u_app.id) not in user_apps:
                u_app.capabilities.all().delete()
                u_app.delete()
        
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
        user_opt, created = Optimization.objects.get_or_create(user_id=user_id)
        return user_opt
    
    @staticmethod
    def saveUserOptimizations(user_id, opt1, opt2, opt3):
        user_opt = Optimization.objects.get(user_id=user_id)
        
        user_opt.opt1 = opt1
        user_opt.opt2 = opt2
        user_opt.opt3 = opt3
        user_opt.save()
        
    @staticmethod
    def getCapabilityById(cap_id):
        return UserCapability.objects.get(pk=cap_id)
    
    @staticmethod
    def getMSPLById(mspl_id):
        return MSPL.objects.get(pk=mspl_id)
    
    @staticmethod
    def deleteMSPLById(mspl_id):
        mspl = MSPL.objects.get(pk=mspl_id)
        mspl.delete()
        
    @staticmethod
    def getUserHSPL(user_id):
        return HSPL.objects.filter(user_id=user_id)
    
    @staticmethod
    def saveHSPL(user_id, post_dict, logger, request):
        # HSPL id for this user in db + id for new HSPL
        hspl_id_list = list(HSPL.objects.filter(user_id=user_id).values_list('id', flat=True)) + list(range(-1, -10, -1))
        
        for hspl_id in hspl_id_list:
            try:
                subject = post_dict['hspl'][hspl_id]['subject'] if post_dict['hspl'][hspl_id]['subject'] != '' else ''
                action = int(post_dict['hspl'][hspl_id]['action']) if post_dict['hspl'][hspl_id]['action'] != '' else 0
                object = int(post_dict['hspl'][hspl_id]['object']) if post_dict['hspl'][hspl_id]['object'] != '' else 0
            except KeyError as ex:
                break
            
            if subject == '' or action == 0 or object == 0:
                if action != 0 or object != 0:
                    request.session['message'] = {'type': 'messageError', 'text': 'Missing some mandatory conditions'}
                continue
            
            try:
                with transaction.atomic():
                    if hspl_id < 0:
                        hspl = HSPL(user_id=user_id, subject=subject, action=action, object=object)
                    else:
                        hspl = HSPL(id=hspl_id, user_id=user_id, subject=subject, action=action, object=object)
                    hspl.save()
                    
                    if object in [13,20]:
                        continue;
                    
                    # HSPL condition id in db for this user
                    condition_id_list = list(hspl.condition.values_list('id', flat=True)) + list(range(-1, -10, -1))
                    
                    # Saving every condition
                    for cond_id in condition_id_list:
                        try:
                            condition_id = int(post_dict['hspl'][hspl_id]['condition'][cond_id])
                        except KeyError as ex:
                            break
                        # Date time condition
                        if condition_id == 1:
                            datetime1 = post_dict['hspl'][hspl_id]['datetime1'][cond_id]
                            datetime2 = post_dict['hspl'][hspl_id]['datetime2'][cond_id]
                            if cond_id < 0:
                                condition = Condition(condition=condition_id, datetime1=datetime1, datetime2=datetime2)
                            else:
                                condition = Condition(id=cond_id, condition=condition_id, datetime1=datetime1, datetime2=datetime2)
                            condition.save()
                        # Text condition
                        elif condition_id in [2, 3, 4, 5]:
                            text = post_dict['hspl'][hspl_id]['text'][cond_id]
                            if cond_id < 0:
                                condition = Condition(condition=condition_id, text=text)
                            else:
                                condition = Condition(id=cond_id, condition=condition_id, text=text)
                            condition.save()
                        # Number condition
                        elif condition_id in [6, 7]:
                            number = post_dict['hspl'][hspl_id]['number'][cond_id]
                            if cond_id < 0:
                                condition = Condition(condition=condition_id, number=number)
                            else:
                                condition = Condition(id=cond_id, condition=condition_id, number=number)
                            condition.save()
                    
                        if cond_id < 0:
                            hspl.condition.add(condition)
                            hspl.save()

            except ValueError as ex:
                logger.exception('HSPL')
            except ValidationError as ex:
                logger.exception('HSPL validation')
                request.session['message'] = {'type': 'messageError', 'text': 'Invalid time period condition: must be hh:mm'}
            except:
                logger.exception('HSPL')
                request.session['message'] = {'type': 'messageError', 'text': 'General error'}
                
    @staticmethod
    def deleteHSPLById(hspl_id):
        hspl = HSPL.objects.get(pk=hspl_id)
        hspl.condition.all().delete()
        hspl.save()
        hspl.delete()
                
    @staticmethod
    def saveUsersAndGroups(request):
        addtype = request.GET['addtype']
        if addtype == 'user':
            username = request.POST['new_username']
            password = request.POST['new_password']
            usertype = request.POST['new_usertype']
            user = User(username=username, password=password, usertype=usertype)
            user.save()
            request.session['message'] = {'type': 'messageSuccess', 'text': 'New user has been saved'}
        else:
            name = request.POST['groupname']
            group = Group(name=name)
            group.save()
            request.session['message'] = {'type': 'messageSuccess', 'text': 'New group has been saved'}
        
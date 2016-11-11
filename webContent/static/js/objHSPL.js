/*
 * HSPL Object
 */
HSPL = function() {
	
	/* Action */
	this.actions = {
		1:'is/are not authorized to access',
		2:'is/are authorized to access',
		3:'enable(s)',
		4:'remove(s)',
		5:'reduce(s)',
		6:'check(s) over',
		7:'count(s)',
		8:'protect(s) confidentiality',
		9:'protect(s) integrity',
		10:'protect(s) confidentiality integrity'
	};
		
	/* Objects */
	this.objects = {
		1:'VOIP traffic',
		2:'P2P traffic',
		3:'3G/4G traffic',
		4:'Internet traffic',
		5:'intranet traffic',
		6:'DNS traffic',
		7:'all traffic',
		8:'public identity',
		9:'Resource “x”',
		10:'file scanning',
		11:'email scanning',
		12:'antivirus',
		13:'basic parental control',
		14:'advanced parental control',
		15:'IDS/IPS',
		16:'DDos attack protection',
		17:'tracking techniques',
		18:'advertisement',
		19:'bandwidth',
		20:'security status',
		21:'connection',
		22:'logging',
		23:'malware detection',
		24:'anti-phishing',
		25:'anonimity'
	};
	
	/* Conditions */
	this.conditions = {
		1:'time period',
		2:'traffic target',
		3:'specific URL',
		4:'type of content',
		5:'purpose',
		6:'uplink bandwidth value',
		7:'resource value',
		8:'downlink bandwidth value',
		9:'country'
	};
	
	this.enableObj = new Map();
	this.enableObj.set(1, [1,2,3,4,5,6,7,9]);
	this.enableObj.set(2, [1,2,3,4,5,6,7,9]);
	this.enableObj.set(3, [10,11,12,13,14,15,16,22,23,24,25]);
	this.enableObj.set(4, [8,17,18]);
	this.enableObj.set(5, [19]);
	this.enableObj.set(6, [20]);
	this.enableObj.set(7, [6,21]);
	this.enableObj.set(8, [1,2,3,4,5,6,7]);
	this.enableObj.set(9, [1,2,3,4,5,6,7]);
	this.enableObj.set(10, [1,2,3,4,5,6,7]);
	
	this.enableCond = new Map();
	this.enableCond.set(1, [1,2]);
	this.enableCond.set(2, [1,2]);
	this.enableCond.set(3, [1,2]);
	this.enableCond.set(4, [1,2,3,4]);
	this.enableCond.set(5, [1,2,3,4]);
	this.enableCond.set(6, [1,2,3,4]);
	this.enableCond.set(7, [1,2,3,4]);
	this.enableCond.set(8, [1,2,3]);
	this.enableCond.set(9, [7]);
	this.enableCond.set(10, [5]);
	this.enableCond.set(11, [5]);
	this.enableCond.set(12, [2]);
	this.enableCond.set(13, null);
	this.enableCond.set(14, [1,4]);
	this.enableCond.set(15, [2]);
	this.enableCond.set(16, [2]);
	this.enableCond.set(17, [3]);
	this.enableCond.set(18, [3]);
	this.enableCond.set(19, [1,3,6,8]);
	this.enableCond.set(20, null);
	this.enableCond.set(21, [1,3]);
	this.enableCond.set(22, [1,2,3,4,5]);
	this.enableCond.set(23, [4,5]);
	this.enableCond.set(24, null);
	this.enableCond.set(25, [9]);
	
	this.getActionList = function() {
		return this.actions;
	};
	
	this.getObjectEnabledBy = function(action) {
		var a_object = this.enableObj.get(parseInt(action));
		var list_obj = new Array();

		for(var i=0; i < a_object.length; i++) {
			var index = a_object[i];
			if(index == undefined) continue;
			list_obj[index] = this.objects[index];
		}
		
		return list_obj;
	};
	
	this.getConditionEnabledBy = function(object) {
		var a_condition = this.enableCond.get(parseInt(object));
		var list_cond = new Array();
		
		if(a_condition == null) {
			return null;
		}
		
		for(var i=0; i < a_condition.length; i++) {
			var index = a_condition[i];
			if(index == undefined) continue;
			list_cond[index] = this.conditions[index];
		}
		
		return list_cond;
	};
				
	this.getAction = function(index) {
		return this.actions[index];
	};
	
	this.getObject = function(index) {
		return this.objects[index];
	};
	
	this.condition = function(index) {
		return this.conditions[index];
	};
};

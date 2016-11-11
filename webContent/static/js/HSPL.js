var hspl = new HSPL();
var lastHsplId = -1;

$(function() {
	$(".action").bind('change', newObject);
	$(".object").bind('change', newCondition);
	$(".condition").bind('change', newConditionField);
	$(".btn-addc").bind('click', addCondition);
	$(".btn-remc").bind('click', removeCondition);
	$(".btn-clear").bind('click', clearAll);
	$(".btn-addrule").bind('click', newHSPL);
	$(".btn-rem").bind("click", removeHSPL);

	/* HIDE RESPONSE MESSAGE */
	setTimeout(function() {
		$('#response_message').hide(800);
	}, 5000);

	/* SUBMIT disabled fields */
	$("#form-hspl").on('submit', function() {
		$('input, select').attr('disabled', false);
	});

	/* ADD DateTimePicker */
	$(".datetimepicker").datetimepicker({
		pickDate : false,
		pickSeconds: false,
	});
});

function newHSPL() {
	document.getElementById('empty_text').style.visibility = "hidden";
	$.ajax({
		type : "GET",
		url : "/hspl/new/",
		data : {
			hspl_id : lastHsplId
		},
		success : function(data) {
			$(".hspl-list").append(data);
			$("li#" + lastHsplId).delegate(".action", 'change', newObject);
			$("li#" + lastHsplId).delegate(".object", 'change', newCondition);
			$("li#" + lastHsplId).delegate(".condition", 'change', newConditionField);
			$("li#" + lastHsplId).delegate(".btn-addc", 'click', addCondition);
			$("li#" + lastHsplId).delegate(".btn-remc", 'click', removeCondition);
			$("li#" + lastHsplId).delegate(".btn-clear", 'click', clearAll);
			$("li#" + lastHsplId).delegate(".btn-rem", 'click', removeHSPL);
			lastHsplId--;
		},
		error : function(data) {
			console.log(data);
		},
	});
}

function removeHSPL() {
	var hspl_id = $(this).attr("id");
	var csrftoken = $.cookie("csrftoken");
	var hspl_li = $(this).parent().parent();
	
	if(hspl_id < 0) {
		hspl_li.remove();
		lastHsplId++;
	} else {
		$.ajax({
			type : "POST",
			url : "/hspl/delete/",
			data : {
				hspl_id : hspl_id,
				csrfmiddlewaretoken : csrftoken
			},
			success : function(data) {
				hspl_li.remove();
			},
			error : function(data) {
				console.log(data);
			}
		});
	}
	if($('#hspl_list li').length == 0)
	{
		document.getElementById('empty_text').style.visibility = "visible";
	}
}

function newObject() {
	var options = '<option value="">Select</option>';
	var objects = hspl.getObjectEnabledBy(this.value);

	for (var index in objects) {
		options += '<option value="' + index + '">' + objects[index] + '</option>';
	}

	$(this).next().html(options);
}

function newCondition() {
	var options = '<option value="">Select</option>';
	var conditions = hspl.getConditionEnabledBy(this.value);

	for (var index in conditions) {
		options += '<option value="' + index + '">' + conditions[index] + '</option>';
	}

	/* Hide follower field if there aren't options for this */
	if (this.value == 13 || this.value == 20) {
		$(this).next().hide();
	} else {
		$(this).next().show();
		$(this).next().html(options);
	}

	/* Disable previous field */
	if (this.value == 0 && !$(this).prev().is(".condition")) {
		$(this).prev().attr('disabled', false);
	} else {
		$(this).prev().attr('disabled', true);
	}
}

function newConditionField() {

	/* Remove previous value field */
	$(this).next("input, .input-append").remove();
	$(this).next("input, .input-append").remove();

	/* Get hspl and condition ID */
	var hspl_id = $(this).parent().attr('id');
	var cond_id = $(this).attr('id');

	/* Prepare fields */
	switch(parseInt(this.value)) {
	case 1:
		$('<div class="datetimepicker condition input-append"><input type="text" data-format="hh:mm" class="condition hspl-input datetime" name="hspl[' + hspl_id + '][datetime2][' + cond_id + ']" disabled="disabled"><span class="add-on"><i data-time-icon="icon-time" data-date-icon="icon-calendar"></i></span></div>').insertAfter($(this));
		$('<div class="datetimepicker condition input-append"><input type="text" data-format="hh:mm" class="condition hspl-input datetime" name="hspl[' + hspl_id + '][datetime1][' + cond_id + ']" disabled="disabled"><span class="add-on"><i data-time-icon="icon-time" data-date-icon="icon-calendar"></i></span></div>').insertAfter($(this));
		break;

	case 2:
	case 3:
	case 4:
	case 5:
	case 6:
	case 7:
	case 8:
	case 9:	
		$('<input type="text" class="condition hspl-input" name="hspl[' + hspl_id + '][text][' + cond_id + ']">').insertAfter($(this));	
		break;
	}

	/* Add timepicker to time field */
	$(".datetimepicker").datetimepicker({
		pickDate : false,
		pickSeconds: false,
	});

	/* Disable previous field */
	if (this.value == 0) {
		$(this).prev().attr('disabled', false);
	} else {
		$(this).prev().attr('disabled', true);
	}
}

function addCondition() {
	var obj_sel = $(this).parent().parent().find(".object").val();
	var last_cond = $(this).parent().parent().find(".condition").val();
	var matches = $(this).parent().parent().find("select.condition:last").attr("id").match(/(\d+)cond(\d+)/);
	var last_cond_id = Number(matches[2]);

	if (obj_sel == 13 || obj_sel == 20) {
		return false;
	}

	if (last_cond == undefined || last_cond == '') {
		return false;
	}

	var hspl_id = $(this).parent().parent().attr('id');
	var cond_id = last_cond_id + 1;

	var options = '<option value="">Select</option>';
	var conditions = hspl.getConditionEnabledBy(obj_sel);

	for (var index in conditions) {
		options += '<option value="' + index + '">' + conditions[index] + '</option>';
	}

	var select = '<select id="' + hspl_id + 'cond' +cond_id + '" class="condition" name="hspl[' + hspl_id + '][condition][' + hspl_id + 'cond' +cond_id + ']">' + options + '</select>';

	$(select).insertBefore($(this).parent());

	$("#" + hspl_id + 'cond' +cond_id ).bind('change', newConditionField);
}

function removeCondition() {
	
	if ($(this).parent().prev().is(".hspl-input, .datetimepicker")) {
		$(this).parent().prev().remove();

		if ($(this).parent().prev().hasClass("datetimepicker")) {
			$(this).parent().prev().remove();
		}

		if (!$(this).parent().prev().prev().is(".object")) {
			$(this).parent().prev().remove();
		} else {
			$(this).parent().prev().find("option").each(function() {
				if ($(this).val() == '')
					$(this).attr("selected", "selected");
			});
		}

		return true;
	}
	
	if ($(this).parent().prev().is(".condition")) {
		if (!$(this).parent().prev().prev().is(".object")) {
			$(this).parent().prev().remove();
		} else {
			$(this).parent().prev().find("option").each(function() {
				if ($(this).val() == '')
					$(this).attr("selected", "selected");
			});
		}

		return true;
	}

	return false;
}

function clearAll() {

	while ($(this).parent().prev().is(".condition") && !$(this).parent().prev().prev().is(".object") && !$(this).parent().prev().prev().prev().is(".action")) {
		$(this).parent().prev().remove();
	}

	$(this).parent().prev().find("option").each(function() {
		if ($(this).val() == '')
			$(this).attr("selected", "selected");
	});
	$(this).parent().prev().attr('disabled', false);

	$(this).parent().prev().prev().find("option").each(function() {
		if ($(this).val() == '')
			$(this).attr("selected", "selected");
	});
	$(this).parent().prev().prev().attr('disabled', false);

	$(this).parent().prev().prev().prev().find("option").each(function() {
		if ($(this).val() == '')
			$(this).attr("selected", "selected");
	});
	$(this).parent().prev().prev().prev().attr('disabled', false);

}

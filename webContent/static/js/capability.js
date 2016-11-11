$(function() {
	
	/* SUBMIT CAPABILITY FORM */
	$(".save-btn").bind("click", function(event) {
		$("#form-app").submit();
	});
	
	/* CAPABILITY FILTER */
	$("select.filter.cap").bind("change", function(event) {
		var filter_name = $(".filter.filter-name").val();
		$("li.apps").each(function(index) {
			var found = false;
			$(this).find(".cap-name").each(function(index) {
				var label_name = $(this).html();
				if(label_name.toLowerCase().indexOf(filter_name.toLowerCase()) >= 0 ) found = true;
			});
			
			if (found) {
				$(this).removeClass('nodisplay');
			} else {
				$(this).addClass('nodisplay');
			}
		});
	});
	
	/* HIDE MSPL FEEDBACK BOX */
	$(".mspl-valid-box").bind("click", function(event) {
		$(this).hide();
	});
	
	/* MSPL CHECK REQUIRED FIELDS */
	$("#mspl-form").bind("submit", function(event) {
		var title = $("[name='mspl_title']").val();
		var xml = $("[name='mspl_xml']").val();
		if(title == '' || xml == '') {
			$(".mspl-valid-box").removeClass("messageSuccess messageError");
			$(".mspl-valid-box").addClass("messageError");
			$(".mspl-valid-box").html("Insert title and xml before submit");
			$(".mspl-valid-box").show();
			return false;
		}
		
		return true;
	});

	/* MSPL MODAL WINDOW */
	$(".o-modal").bind("click", function(event) {
		var cap_id = $(this).find(".btn").attr("id");
		var psa_id = $(this).find(".btn").attr("psa_id");
		$.ajax({
			type : "GET",
			url : "/app/mspl/",
			data : {
				cap_id : cap_id,
				psa_id : psa_id
			},
			async : true,
			success : function(mspl) {
				$("[name='cap_id']").val(cap_id);
				$("[name='psa_id']").val(psa_id);
				$("[name='mspl_id']").val(mspl.id);
				$("[name='mspl_title']").val(mspl.title);
				$("[name='mspl_xml']").val(mspl.xml);
				document.getElementById('mspl-list').value=mspl.id;
				var x = document.getElementById("mspl-list").options;
				var len = x.length;
				for(i = 1; i < len; i++)
				{
					if(x[i].getAttribute('capability_id') != cap_id)
					{
						x[i].disabled = true;
					}
					else
					{
						x[i].disabled = false;
					}
				}
			},
			error : function(data, status) {
				return false;
			}
		});
	});

	/* MSPL MODAL WINDOW LIST */
	$("#mspl-list").bind("change", function(event) {
		var mspl_id = this.value;

		if (mspl_id == 0) {
			$("[name='mspl_id']").val(0);
			$("[name='mspl_title']").val('');
			$("[name='mspl_xml']").val('');
			return true;
		}

		$.ajax({
			type : "GET",
			url : "/mspl/id/",
			data : {
				mspl_id : mspl_id
			},
			async : true,
			success : function(mspl) {
				$("[name='mspl_id']").val(mspl.id);
				$("[name='mspl_title']").val(mspl.title);
				$("[name='mspl_xml']").val(mspl.xml);
				$(".mspl-valid-box").html("").hide();
			},
			error : function(data, status) {
				return false;
			}
		});
	});

	/* Validate XML */
	$(".btn-val").bind("click", function(event) {
		var mspl_xml = $("[name='mspl_xml']").val();
		var csrftoken = $.cookie("csrftoken");

		$.ajax({
			type : "POST",
			url : "/mspl/validate/",
			data : {
				mspl_xml : mspl_xml,
				csrfmiddlewaretoken : csrftoken
			},
			async : true,
			success : function(data) {
				$(".mspl-valid-box").removeClass("messageSuccess messageError");
				if (data.type == "error") {
					$(".mspl-valid-box").addClass("messageError");
				} else {
					$(".mspl-valid-box").addClass("messageSuccess");
				}
				$(".mspl-valid-box").html(data.message);
				$(".mspl-valid-box").show();
				return true;
			},
			error : function(data, status) {
				return false;
			}
		});
	});
	
	/* VALIDATE CONFIG */
	$(".btn-vconf").bind("click", function(event) {
		alert("Not yet implemented");
		/* See previous function for the implementation */
		var mspl_xml = $("[name='mspl_xml']").val();
		var csrftoken = $.cookie("csrftoken");

		$.ajax({
			type : "POST",
			url : "/mspl/sfa/",
			data : {
				mspl_xml : mspl_xml,
				csrfmiddlewaretoken : csrftoken
			},
			async : true,
			success : function(data) {
				$(".mspl-valid-box").removeClass("messageSuccess messageError");
				if (data.type == "error") {
					$(".mspl-valid-box").addClass("messageError");
				} else {
					$(".mspl-valid-box").addClass("messageSuccess");
				}
				$(".mspl-valid-box").html(data.message);
				$(".mspl-valid-box").show();
				return true;
			},
			error : function(data, status) {
				return false;
			}
		});

	});

});

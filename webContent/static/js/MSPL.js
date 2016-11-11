$(function() {
	var timeout = null;
	var submitFilterInterval = null;
	
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

	/* MSPL FILTER */
	$("input.filter").bind("keyup", function(event) {
		window.clearInterval(submitFilterInterval);
		submitFilterInterval = window.setTimeout(function() {
			var filter = $("input.filter").val();
			$("li.mspl").each(function(index) {
				var label = $(this).find(".app-name").html();
				if (label.toLowerCase().indexOf(filter.toLowerCase()) >= 0) {
					$(this).removeClass('nodisplay');
				} else {
					$(this).addClass('nodisplay');
				}
			});
		}, 750);
	});

	/* MSPL DELETE CONFIRMATION */
	$(".mspl-delete").bind("submit", function(event) {
		return confirm("Are you sure?");
	});
	
	/* HIDE MSPL FEEDBACK BOX */
	$(".mspl-valid-box").bind("click", function(event) {
		$(this).hide();
	});

	/* MSPL MODAL WINDOW */
	$(".o-modal").bind("click", function(event) {
		var id = $(this).find(".btn").attr("id");

		$.ajax({
			type : "GET",
			url : "/mspl/id/",
			data : {
				mspl_id : id
			},
			async : true,
			success : function(mspl) {
				$("[name='mspl_title']").val(mspl.title);
				$("[name='mspl_xml']").val(mspl.xml);
			},
			error : function(data, status) {
				return false;
			}
		});

		$("[name='mspl_id']").val(id);
		$(".mspl-valid-box").removeClass("messageSuccess messageError");
		$(".mspl-valid-box").html("");
	});

	/* Validate XML */
	$(".btn-val").bind("click", function(event) {
		var csrftoken = $.cookie("csrftoken");

		$.ajax({
			type : "POST",
			url : "/mspl/validate/",
			data : {
				mspl_xml : $("[name='mspl_xml']").val(),
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
		var csrftoken = $.cookie("csrftoken");

		$.ajax({
			type : "POST",
			url : "/mspl/sfa/",
			data : {
				mspl_xml : $("[name='mspl_xml']").val(),
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
				var w = window.open();
  				var html = data;

				$(w.document.body).html(html);
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

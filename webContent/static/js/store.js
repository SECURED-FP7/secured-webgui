$(function() {
	var saved = true;
	var total = 0;
	var submitFilterInterval = null;

	/* DRAG & DROP APPLICATIONS */
	$("ul#sourceList").sortable({
		connectWith : "ul",
		receive : function(event, ui) {
			$(this).find(".app-price").show();
		}
	});

	$("ul#targetList").sortable({
		connectWith : "ul",
		cancel : ".empty-placeholder",
		receive : function(event, ui) {
			/* Empty placeholder */
			numItems = $("#targetList").find('li').length;
			if (numItems == 2) {
				$("#targetList").find('li.empty-placeholder').hide();
			}
			saved = false;

			/* Total cost */
			var app_cost = parseFloat($(this).find(".app-price > .price").html());
			total += app_cost;
			$("#total-cost").html(total.toFixed(2));
		},
		remove : function(event, ui) {
			/* Empty placeholder */
			numItems = $("#targetList").find('li').length;
			if (numItems == 1) {
				$("#targetList").find('li.empty-placeholder').show();
			}
			saved = false;

			/* Total cost */
			var app_cost = parseFloat($(this).find(".app-price > .price").html());
			total -= app_cost;
			total = total < 0 ? 0 : total;
			$("#total-cost").html(total.toFixed(2));
		}
	});

	$("#sourceList, #targetList").disableSelection();

	/* CHECK SAVED CHANGES */
	$("a").bind("click", function(event) {

		if ($("#targetList").find('li').length > 1 && saved == false) {
			$('#startLoader').hide();
			var response = confirm("All changes will be lost, do you want to proceed anyway?");
			if (response == false) {
				return false;
			}
		}

		return true;
	});

	/* STORE FILTER */
	$(".filter.store").bind("keyup change", function(event) {
		window.clearInterval(submitFilterInterval);
		submitFilterInterval = window.setTimeout(function() {
			var filter_name = $(".filter-name.store").val();
			var filter_capability = $(".filter-capability.store").val();
			var filter_price = parseFloat($(".filter-price.store").val());

			
			$("li.store").each(function(index) {
				var name = $(this).find(".app-name").html();
				var price = parseFloat($(this).find(".price").html());
				
				var match_name = name.toLowerCase().indexOf(filter_name.toLowerCase()) >= 0;
				var match_capability = false;
				$(this).find(".app-capability").each(function(index) {
					var label_name = $(this).val();
					if(label_name.toLowerCase().indexOf(filter_capability.toLowerCase()) >= 0 ) match_capability = true;
				});
				var match_price = true;
				if(!isNaN(filter_price)) {
					match_price = filter_price == price;
				}
				
				if(match_name && match_capability && match_price) {
					$(this).removeClass('nodisplay');
				} else {
					$(this).addClass('nodisplay');
				}
			});
		}, 750);
	});

	/* APPLICATION FILTER */	
	$(".filter.app").bind("keyup change", function(event) {
		window.clearInterval(submitFilterInterval);
		submitFilterInterval = window.setTimeout(function() {
			var filter_name = $(".filter-name.app").val();
			var filter_capability = $(".filter-capability.app").val();
			var filter_price = parseFloat($(".filter-price.app").val());

			
			$("li.apps").each(function(index) {
				var name = $(this).find(".app-name").html();
				var price = parseFloat($(this).find(".price").html());
				
				var match_name = name.toLowerCase().indexOf(filter_name.toLowerCase()) >= 0;
				var match_capability = false;
				$(this).find(".app-capability").each(function(index) {
					var label_name = $(this).val();
					if(label_name.toLowerCase().indexOf(filter_capability.toLowerCase()) >= 0 ) match_capability = true;
				});
				var match_price = true;
				if(!isNaN(filter_price)) {
					match_price = filter_price == price;
				}
				
				if(match_name && match_capability && match_price) {
					$(this).removeClass('nodisplay');
				} else {
					$(this).addClass('nodisplay');
				}
			});
		}, 750);
	});

	/* SAVE BOUGHT APPLICATIONS */
	$(".btn-submit").bind("click", function(event) {
		var ser = $("#targetList").sortable("serialize", {
			expression : /(.+?)_(.+)/
		});
		var csrftoken = $.cookie("csrftoken");

		console.log(ser);

		$('#startLoader').show();

		$.ajax({
			type : "POST",
			url : "/store/",
			data : {
				psa_ser : ser,
				csrfmiddlewaretoken : csrftoken
			},
			success : function(data) {
				console.log(data);
				var array_id = data.list.reverse();
				console.log(array_id);
				
				$('#startLoader').hide();
				$("#response_message").removeClass("messageSuccess messageError");
				$('#response_message').show();
				$("#response_message").html("Customization saved");
				$("#response_message").addClass("messageSuccess");
				$("#targetList > li > .app-price").hide();
				$("ul#targetList li").each(function() {
					if ($(this).attr("id") != undefined){
						console.log($(this).attr("id").match(/store_(.*)/));
					}
					if ($(this).attr("id") != undefined && $(this).attr("id").match(/store_(.*)/) != null) {
						$(this).attr("id", "user_" + array_id.pop());
					}
				});
				saved = true;
				total = 0;
				setTimeout(function() {
					$('#response_message').hide(800);
				}, 5000);
			},
			error : function(data) {
				$('#startLoader').hide();
				$("#response_message").removeClass("messageSuccess messageError");
				$('#response_message').show();
				$("#response_message").html("Error saving customizations");
				$("#response_message").addClass("messageError");
				setTimeout(function() {
					$('#response_message').hide(800);
				}, 5000);
			},
		});
	});

});

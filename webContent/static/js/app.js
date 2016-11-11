$(function() {
	var saved = true;
	var timeout = null;
	var submitFilterInterval;
	
	/* APPLICATION SORTABLE LIST */
	$(".applist").sortable({
		axis : "y",
		delay : 900
	});

	$(".draggable").mousedown(function() {
		var obj = $(this);
		if ($(window).width() > 910) {
			timeout = setTimeout(function() {
				obj.animate({
					backgroundColor : "#9D9D9D"
				}, 300);
			}, 0);
		} else {
			timeout = setTimeout(function() {
				obj.animate({
					backgroundColor : "#9D9D9D"
				}, 300);
			}, 300);
		}
	});

	$(".draggable").mouseup(function() {
		clearTimeout(timeout);
		$(this).animate({
			backgroundColor : "#C4C3C3"
		}, 500);
	});
	
	/* SUBMIT APPLICATION FORM */
	$(".save-btn").bind("click", function(event) {
		$("#form-app").submit();
	});

	/* APP FILTER */
	$(".filter.app").bind("keyup change", function(event) {
		window.clearInterval(submitFilterInterval);
		submitFilterInterval = window.setTimeout(function() {
			var filter_name = $("input.filter.filter-name").val();
			var filter_capability = $(".filter.filter-capability").val();
			var filter_price = parseFloat($("input.filter.filter-price").val());
			
			$("li.apps").each(function(index) {
				var name = $(this).find(".app-name").html();
				var price = parseFloat($(this).find(".app-price").val());
				
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

});
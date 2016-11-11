$(window).load(function() {
	$('#startLoader').hide();
	calculateHeight();
});

$(function() {
	setTimeout(function() {
		$('#response_message').hide(800);
	}, 5000);

	$(".navbar-btn").bind("click", function(event) {
		$('#startLoader').show();
	});
	
	/*
	$("a:not(.o-modal, .close)").bind("click", function(event) {
		if (saved == false) {
			$('#startLoader').hide();
			return confirm("All changes will be lost, do you want to proceed anyway?");
		}
	});
	*/
});

$(window).resize(calculateHeight);

function calculateHeight() {
	var height = $(window).height() - $(".header-fixed").outerHeight() - $(".footer").outerHeight() - 150;

	if ($(window).width() > 910) {
		$(".sortable").height(height);
		$(".section").height(height + 150);
		$(".applist").sortable("option", "delay", false);
	} else {
		$(".sortable").height('auto');
		$(".section").height('auto');
		$(".applist").sortable("option", "delay", 900);
	}
}
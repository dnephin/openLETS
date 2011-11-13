
/*
 * Set 'active' class on the active nav item.
 */
set_active_tab = function() {
	var path = document.location.pathname;
	var nav_link = $('.nav > li > a[href="'+path+'"]');
	if (nav_link) {
		nav_link.parent().addClass('active');
	}
}

/*
 * Create sliders with jquery ui.
 */
setup_sliders = function() {
	$('.slider').each(function(i, ele) {
		var input = $(ele).siblings('input.slider-input');
		$(ele).slider({
			range: "min",
			value: input.val(),
			min: parseInt(input.attr('data-min')),
			max: parseInt(input.attr('data-max')),
			slide: function(event, ui) {
				input.val(ui.value);
			}
		})
	})
}

$(document).ready(function () {
	set_active_tab();
	$('[rel="popover"]').popover();
	setup_sliders();
})

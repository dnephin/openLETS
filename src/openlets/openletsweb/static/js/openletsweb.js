
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

/*
 * Setup click events for toggles.
 */
setup_toggles = function() {
	$('.show-hide-toggle').each(function(i, ele) {
		var ele = $(ele);
		var target = $(ele.attr('data-target'));
		ele.click(function(event) {
			event.preventDefault();
			// toggle text
			old_text = ele.html();
			ele.html(ele.attr('data-toggle-text'));
			ele.attr('data-toggle-text', old_text);

			// toggle css
			remove_class = ele.attr('data-remove-class');
			add_class = ele.attr('data-add-class');
			target.removeClass(remove_class);
			target.addClass(add_class);
			ele.attr('data-remove-class', add_class);
			ele.attr('data-add-class', remove_class);
		})
	})
}

$(document).ready(function () {
	set_active_tab();
	$('[rel="popover"]').popover();
	setup_sliders();
	setup_toggles();
})

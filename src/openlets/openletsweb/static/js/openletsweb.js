
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


$(document).ready(function () {
	set_active_tab()	
})

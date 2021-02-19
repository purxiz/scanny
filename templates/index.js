$(document).ready(function() {
	$('#search').keyup(function() {
		let term = $('#search').val();
		if(term.length < 3) {
			$('#left').children().show();
			return;
		}
		let items = $('#left').children().hide().each(function() {
			if($(this).text().toLowerCase().indexOf(term) > -1) $(this).show();
		});
	});
	$('#search').focus();
	$('#search').blur(function() {
		setTimeout(function() {
			$('#search').focus();
		}, 20);
	});
	$('.item').item_clickable();
});

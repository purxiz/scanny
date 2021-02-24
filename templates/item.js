$(document).ready(function() {

	$('#add').click(function() {
		$.ajax({
			url: '/add_by_id',
			data: {
				id: '{{ item }}'
			}
		}).then(function(response) {
			add_visual_item(response);
			inc_or_dec(1);
		});
	});
	$('#remove').click(function() {
		$.ajax({
			url: '/remove_by_id',
			data: {
				id: '{{ item }}'
			}
		}).then(function(response) {
			if(response.err && response.err === 'none_exists') {
				return;
			}
			remove_visual_item(response);
			inc_or_dec(-1);
		});
	});

	function inc_or_dec(val) {
		let amount = parseInt($('#count').html()) + val;
		if (amount < 0) return;
		$('#count').html(amount);
	}

	function add_visual_item(item) {
		$('#left').prepend(
			$('<div>').addClass('item').html(item.name + ' - ' + item.purchase_date)
		);
		return 0;
	}

	function remove_visual_item(item) {
		$('#left').children().last().remove();
	}
});

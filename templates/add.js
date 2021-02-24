$(document).ready(function() {

	focus_code_input();

	$('.item').item_clickable();

	function add_new_item(name, code) {
		$('#name').off('');
		$('#submit').off('');
		$.ajax({
			url: '/add_barcode_and_item',
			data: {
				name: name,
				code: code,
			}
		}).then(function(response) {
			if(response.err && response.err === 'unique_violation') {
				$('#name').val('');
				listen_for_name_input('#unique_violation');
				return;
			}
			$.add_visual_item(response);
			$('#code_input').val('');
			$('#name').val('');
			focus_code_input();
		});
	}

	function listen_for_name_input(warning) {
		$('#name').blur();
		$('#code_input').blur();
		$.warn(warning,
		function() {
			$('#name').keyup(function(e) {
				if(e.key === '{{ config.confirm_key }}') {
					add_new_item($('#name').val(), $('#code_input').val());
				}
			});
			$('#name').inline_complete();
			$('#name').focus();
			$('#submit').click(function(e) {
				add_new_item($('#name').val(), $('#code_input').val());
			});
		});
	}

	function focus_code_input() {
		$('#code_input').focus();
		$('#code_input').blur(function() {
			setTimeout(function() {
				$('#code_input').focus();
			}, 20);
		});
		$('#code_input').keyup(function(e) {
			if(e.key === '{{ config.confirm_key }}') {
				$.ajax({
					url: '/add_by_barcode',
					data: {
						code: $('#code_input').val()
					},
				}).then(function(response) {
					if(response.err && response.err === 'not_found') {
						$('#code_input').off();
						listen_for_name_input('#not_found');
					} else {
						$('#code_input').val('');
						$.add_visual_item(response);
					}
				});
			}
		});
	}
});

$(document).ready(function() {

	focus_code_input();

	$('.item').item_clickable();
	console.log('hi');

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
				$('#unique_violation').show();
				$('#name').val('');
				listen_for_name_input();
				return;
			}
			$.add_visual_item(response);
			$('#code_input').val('');
			$('#name').val('');
			focus_code_input();
		});
	}

	function listen_for_name_input() {
		$('#name').blur();
		$('#code_input').blur();
		let complete_string = '';
		$(document).keydown(function(e) {
			console.log(e.key);
			if(e.key === 'Escape') {
				$(document).off();
				$('.warn').hide();
				$('#name').keyup(function(e) {
					if(e.key === 'Enter') {
						add_new_item($('#name').val(), $('#code_input').val());
					}
				});
				$('#name').inline_complete();
				$('#name').focus();
				$('#submit').click(function(e) {
					add_new_item($('#name').val(), $('#code_input').val());
				});
			}
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
			if(e.key === 'Enter') {
				$.ajax({
					url: '/add_by_barcode',
					data: {
						code: $('#code_input').val()
					},
				}).then(function(response) {
					if(response.err && response.err === 'not_found') {
						$('#code_input').off();
						$('#not_found').show();
						listen_for_name_input();
					} else {
						$('#code_input').val('');
						$.add_visual_item(response);
					}
				});
			}
		});
	}
});

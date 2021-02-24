$(document).ready(function() {
	let last_item = null;
	$('#last_item').click(function() {
		if(!last_item) return;
		document.location = '/item?id=' + last_item;
	});

	focus_code_input();

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
					url: '/remove_by_barcode',
					data: {
						code: $('#code_input').val()
					},
				}).then(function(response) {
					if(response.err && response.err === 'none_exists') {
						$('#code_input').off();
						$('#code_input').blur();
						$.warn('#not_found', function() {
							$('#code_input').val('');
							focus_code_input();
						});
					} else {
						last_item = response.id;
						$('#code_input').val('');
						$.add_visual_item(response);
					}
				});
			}
		});
	}


});

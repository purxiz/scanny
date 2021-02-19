$(document).ready(function() {
	let last_item = null;
	$('#last_item').click(function() {
		if(!last_item) return;
		document.location = '/item?id=' + last_item;
	});

	focus_code_input();

	function add_visual_item(item) {
		console.log(item);
		$('#left').prepend(
			$('<div>').addClass('item').html(item.name + ' - ' + item.purchase_date)
		);
		return 0;
	}

	function listen_for_continue_input() {
		$('#code_input').blur();
		$(document).keydown(function(e) {
			if(e.key === 'Escape') {
				$(document).off();
				$('.warn').hide();
				focus_code_input();
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
					url: '/remove_by_barcode',
					data: {
						code: $('#code_input').val()
					},
				}).then(function(response) {
					if(response.err && response.err === 'none_exists') {
						$('#code_input').off();
						$('#not_found').show();
						listen_for_continue_input();
					} else {
						last_item = response.id;
						$('#code_input').val('');
						add_visual_item(response);
					}
				});
			}
		});
	}


});

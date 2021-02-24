$(document).ready(function() {
	focus_name_and_listen();
	$('#submit').click(function() {
		rename_item();
	});

	function rename_item_and_rebase() {
		rename_item('/rename_by_name');
	}

	function rename_item(url = null) {
		if($('#name').val().replace('\n', '').length < 1) {
			$.warn('#blank',
			function() {
				focus_name_and_listen();
			}, function() {
				rename_item_and_rebase();
			});
			return;
		}
		$.ajax({
			url: url || '/rename_by_id',
			data: {
				id: {{ id }},
				name: $('#name').val()
			}
		}).then(function(response) {
			if(response.redirect) {
				window.location.href = response.redirect;
			}
			if(response.err && response.err === 'unique_violation') {
				$('#name').off();
				$('#name').blur();
				$.warn('#unique_violation',
				function() {
					focus_name_and_listen();
				}, function() {
					rename_item_and_rebase();
				});
				return;
			}
			$.add_visual_item({
				name: 'Renamed ' + $('#title_name').html() + ' to ' + response.name,
				purchase_date: 'success',
				id: ''
			});
			$('#title_name').html(response.name);
			$('#name').val('');
		});
	}

	function focus_name_and_listen() {
		$('#name').focus();
		$('#name').blur(function() {
			setTimeout(function() {
				$('#name').focus();
			}, 20);
		});

		$('#name').inline_complete();

		$('#name').keyup(function(e) {
			if(e.key === '{{ config.confirm_key }}') {
				rename_item();
			}
		});
	}
	
});

$(document).ready(function() {
	focus_name_and_listen();
	$('#submit').click(function() {
		rename_item();
	});

	function warn(warning) {
		$(warning).show();
		$('#name').off();
		$('#name').blur();
		$(document).keydown(function(e) {
			if (e.key === 'Escape') {
				$(warning).hide();
				$(document).off('keydown');
				focus_name_and_listen();
			}
			else if (e.key === 'Enter') {
				$(warning).hide();
				$(document).off('keydown');
				rename_item_and_rebase();
			}
		})
	}

	function rename_item_and_rebase() {
		rename_item('/rename_by_name');
	}

	function rename_item(url = null) {
		console.log('renaming ' + $('#name').val());
		if($('#name').val().replace('\n', '').length < 1) {
			warn('#blank');
			return;
		}
		$.ajax({
			url: url || '/rename_by_id',
			data: {
				id: {{ id }},
				name: $('#name').val()
			}
		}).then(function(response) {
			console.log(response);
			if(response.redirect) {
				window.location.href = response.redirect;
			}
			if(response.err && response.err === 'unique_violation') {
				warn('#unique_violation');
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
			if(e.key === 'Enter') {
				rename_item();
			}
		});
	}
	
});

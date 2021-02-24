jQuery.fn.extend({
	item_clickable: function() {
		return this.each(function(){
			$(this).addClass('item-clickable');
			$(this).click(function() {
				document.location = '/item?id=' + $(this).attr('item_id');
			});
		});
	},
	inline_complete: function() {
		let complete_string = '';
		$(this).keyup(function(e) {
			if(e.key ===  '{{ config.continue_key }}') {
				$(this).val(complete_string);
				$('#name_complete').val('');
			}
			else if($(this).val().length > 2) {
				$.ajax({
					url: '/item_most_likely',
					data: {
							name: $('#name').val(),
							offset: 0,
					},
				}).then(function(response) {
					complete_string = response.name;
					$('#name_complete').val(complete_string);
				});
			} else {
				$('#name_complete').val('');
				complete_string = '';
			}
		});
	},
});

$.add_visual_item = function(item) {
	$('#left').prepend(
		$('<div>').addClass('item').html(item.name + ' - ' + item.purchase_date).attr('item_id', item.id).item_clickable()
	);
};

$.warn = function(warning, continue_callback = null, confirm_callback=null) {
	$(warning).show();
	$('input').blur();
	$(document).keydown(function(e) {
		if (e.key === '{{ config.continue_key }}') {
			$(warning).hide();
			$(document).off('keydown');
			if (continue_callback) continue_callback();
		}
		else if (e.key === '{{ config.confirm_key }}') {
			$(warning).hide();
			$(document).off('keydown');
			if (confirm_callback) confirm_callback();
		}
	});
}

{% if config.left_pane_scroll %}
$(document).ready(function() {
	let offset = 0;
	let prev_offset = 0;
	$(document).keyup(function(e) {
		prev_offset = offset;
		if(e.key === '{{ config.page_up_key }}') {
			offset = offset - $('#left').height() - 25;
		}
		if(e.key === '{{ config.page_dn_key }}') {
			offset = offset + $('#left').height() - 25;
		}
		if(offset < 0) offset = 0;
		else if(offset > $('#left')[0].scrollHeight - $('#left').height()) offset = $('#left')[0].scrollHeight - $('#left').height();
		if(offset !== prev_offset) {
			$('#left').animate({
				scrollTop: offset
			});
		}
	});
	$('#left').scroll(function() {
		offset = $('#left').scrollTop();
	});
});
{% endif %}

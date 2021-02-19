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
			if(e.key ===  'Escape') {
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

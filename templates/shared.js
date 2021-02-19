jQuery.fn.extend({
	item_clickable: function() {
		return this.each(function(){
			$(this).addClass('item-clickable');
			$(this).click(function() {
				document.location = '/item?id=' + $(this).attr('item_id');
			});
		});
	},
});
$.add_visual_item = function(item) {
	$('#left').prepend(
		$('<div>').addClass('item').html(item.name + ' - ' + item.purchase_date).attr('item_id', item.id).item_clickable()
	);
};

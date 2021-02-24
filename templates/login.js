$(document).ready(function() {
	$('#username').focus();

	$('#username').keyup(function(e) {
		if(e.key === 'Enter') {
			$('#password').focus();
		}
	});

	$('#password').keyup(function(e) {
		if(e.key === 'Enter') {
			attempt_login();
		}
	});

	$('#login').click(function() {
		attempt_login();
	});

	function attempt_login() {
		let user = $('#username').val();
		let pass = $('#password').val();
		$.ajax({
			url: '/login_or_register',
			data: {
				username: user,
				password: pass
			}
		}).then(function(response) {
			if(response.redirect) {
				window.location.href = response.redirect;
			}
			else if (response.err && response.err === 'username') {
				$.warn('#warn_user')
			}
			else if (response.err && response.err === 'password') {
				$.warn('#warn_pass')
			}
		});
	}
});

#########################
#	App Configuration	#
#########################

# require_login
# If true, the app will require login before viewing the grocery list
require_login = True

# If true, the app will allow users to register using the login fields, if false, users can only login.
# The intended usage is to enable registration when you want to add a new user, then disable it afterwards.
# Otherwise, anyone can access your grocery list simply by creating a new user.
allow_registration = True

# Whether or not to enable scrolling using the configured keys, please use javascript key names
# Disabling scrolling will save performance on lower powered devices.
left_pane_scroll = True
page_up_key = 'PageUp'
page_dn_key = 'PageDown'

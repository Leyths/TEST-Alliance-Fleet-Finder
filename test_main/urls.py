from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'test_main.views.home', name='home'),
	url(r'^update_status.html', 'test_main.views.update_status', name='update_status'),
	url(r'^login.html', 'test_main.views.login', name='login'),
	url(r'^update.html', 'test_main.views.check_in', name='check_in'),
	url(r'^looking_for_fleet.html', 'test_main.views.lff', name='looking_for_fleet'),
    url(r'^cancel_lff.html', 'test_main.views.cancel_looking_for_fleet', name='cancel_looking_for_fleet'),
    url(r'^create_fleet_temp.html', 'test_main.views.create_fleet_template', name='create_fleet_template'),
    url(r'^update_fleet_temp.html', 'test_main.views.update_fleet_temp', name='update_fleet_template'),
    url(r'^create_fleet.html', 'test_main.views.create_fleet', name='create_fleet'),
    url(r'^update_fleet.html', 'test_main.views.update_fleet', name='update_fleet'),
    url(r'^join_fleet.html', 'test_main.views.join_fleet', name='join_fleet'),
    url(r'^system_search.html', 'test_main.views.search_for_system', name='search_for_system'),
    url(r'^leave_fleet.html', 'test_main.views.leave_fleet', name='Leave_fleet'),
    url(r'^disband_fleet.html', 'test_main.views.disband_fleet', name='disband_fleet'),

    #url(r'^dummy.html', 'test_main.views.insert_dummy_data', name='dummy_data'),
    #url(r'^random_u.html', 'test_main.views.create_random_user', name='random_user'),
    url(r'^random_f.html', 'test_main.views.create_random_fleet', name='random_fleet'),
    # url(r'^testproject/', include('testproject.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

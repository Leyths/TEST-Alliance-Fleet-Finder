from django.http import HttpResponse
from django.template import RequestContext, loader
from test_main.models import Pilot, FleetType, Fleet, System, Region, FleetMembership
from httplib import HTTPSConnection
from django.utils import timezone, dateparse
from django.shortcuts import redirect
from django.contrib import messages
import pytz
import hashlib
import json
import datetime
import random
import io

counter = [datetime.datetime.now()]
currentUsersOnlineRenderedTemplate = [None, None]

def home(request, message=""):
	if(is_signed_in(request)):
		t = loader.get_template('test_main/index.html')
		pilot_list = Pilot.objects.all().filter(looking_for_fleet=True)
		user_pilot = Pilot.objects.get(name=request.session['username'])

		if(currentUsersOnlineRenderedTemplate[0] == None):
			render_current_users_template(request)
		else:
			update_template_if_delta(request)

		c = RequestContext(request, {
			'u':user_pilot,
			'template':currentUsersOnlineRenderedTemplate[0],
			'info':currentUsersOnlineRenderedTemplate[1]
		})
		return HttpResponse(t.render(c))
	else:
		t = loader.get_template('test_main/login.html')
		c = RequestContext(request, {
			"message":message
		})
		return HttpResponse(t.render(c))

def update_template_if_delta(request):
	delta = datetime.datetime.now()-counter[0]

	if(delta.seconds>30 or currentUsersOnlineRenderedTemplate[0] == None):
		render_current_users_template(request);
		
def check_in(request):
	timezone.activate(pytz.timezone("Iceland"))
	user = Pilot.objects.get(name=request.session['username'])
	user.last_checkin = timezone.now()
	user.save()
	
	update_template_if_delta(request)
	
	user_pilot = Pilot.objects.get(name=request.session['username'])

	t = loader.get_template("test_main/pilot_header.html")
	c = RequestContext(request, {
			'u':user_pilot
		})
	pilot_header = t.render(c)

	json_result = json.dumps({"pilot_info":pilot_header, "body":currentUsersOnlineRenderedTemplate[0], "info":currentUsersOnlineRenderedTemplate[1]})

	return HttpResponse(json_result)
	
def render_current_users_template(request):
	timezone.activate(pytz.timezone("Iceland"))
	#do work
	counter[0] = datetime.datetime.now()
	idle_and_expired = Pilot.objects.all().filter(looking_for_fleet = True).exclude(last_checkin__gte = timezone.now()-datetime.timedelta(minutes = 2))
	
	
	idle_and_expired.update(looking_for_fleet=False)
	update_fleet_list()


	fleets = sorted(list(Fleet.objects.all().filter(active = True)), key=lambda n: (n.date_primary(n)), reverse=False)


	for i in range(len(fleets)):
		fleet_m = FleetMembership.objects.all().filter(fleet = fleets[i])
		fleets.insert(i, [fleets[i], Pilot.objects.all().filter(current_fleet__in = fleet_m)])
		fleets.pop(i+1)

	t = loader.get_template('test_main/update.html')
	c = RequestContext(request, {
		'lf_fleet':Pilot.objects.all().filter(looking_for_fleet = True),
		'fleets':fleets,
	})
	
	currentUsersOnlineRenderedTemplate[0] = t.render(c)

	t = loader.get_template('test_main/info.html')
	c = RequestContext(request, {
		'number_online':Pilot.objects.all().filter(last_checkin__gte = timezone.now()-datetime.timedelta(minutes = 2)).count(),
		'last_rendered':timezone.now(),
	})
	
	currentUsersOnlineRenderedTemplate[1] = t.render(c)

def update_status(request):
	t = loader.get_template('test_main/update_status.html')
	c = RequestContext(request, {
		"fleet_types" : FleetType.objects.all(),
		"u":Pilot.objects.get(name=request.session['username'])
	})
	return HttpResponse(t.render(c))

def create_fleet_template(request):
	t = loader.get_template('test_main/create_fleet.html')
	c = RequestContext(request, {
		"fleet_types" : FleetType.objects.all(),
		"update" : False,
	})
	return HttpResponse(t.render(c))
	
def login(request):
	username = request.POST["user"]
	password = request.POST["pass"]
	
	hashp = hashlib.sha1()
	hashp.update(password)

	connection = HTTPSConnection("auth.pleaseignore.com:443")
	connection.request("GET", "/api/1.0/login/?user="+username+"&pass="+hashp.hexdigest())
	login_result = connection.getresponse().read()
	
	#Parse JSON result for auth status
	result = json.loads(login_result)
	if(result["auth"] == "ok"):
		success = True
	else:
		success = False
	if(not success):
		messages.add_message(request, messages.INFO, 'Incorrect Username/Password')
		return redirect("home")
	else:
		auth_username = result["primarycharacter"]["name"]
		request.session['username'] = auth_username
		
		handle_first_logon(request)
		
		return redirect("home")

def lff(request):
	timezone.activate(pytz.timezone("Iceland"))
	user = Pilot.objects.get(name=request.session['username'])
	user.last_checkin = timezone.now()
	
	if(user.current_fleet != None):
		leave_fleet(request)

	it = request.GET.getlist("fleetType", "")
	fleets = FleetType.objects.all()
	

	fleets=fleets.filter(name__in=it)
	
	user.looking_for_fleet = True;
	user.alert = request.GET.get("alert", False)
	user.fleet_types.clear()

	for f in fleets:
		user.fleet_types.add(f)

	user.save()

	render_current_users_template(request)

	return HttpResponse("{\"success\":true}")

def cancel_looking_for_fleet(request):
	timezone.activate(pytz.timezone("Iceland"))
	user = Pilot.objects.get(name=request.session['username'])
	user.last_checkin = timezone.now()

	user.looking_for_fleet = False
	user.save()

	render_current_users_template(request)

	return HttpResponse("{\"success\":true}")
		
def is_signed_in(request):
	if(not request.session.get('username', "") == ""):
		return True
	else:
		return False

def handle_first_logon(request):
	try:
		user_pilot = Pilot.objects.get(name=request.session['username'])
	except Pilot.DoesNotExist:
		user_pilot = Pilot(name=request.session['username'], 
			last_checkin = timezone.now(),
			looking_for_fleet = False,
			alert = False)
		user_pilot.save();

def search_for_user(request):
	try:
		user_pilot = Pilot.objects.get(name=request.GET.get("user", ""))
		return HttpResponse("{\"success\":true}")
	except Pilot.DoesNotExist:
		return HttpResponse("{\"success\":false}")

def search_for_system(request):
	term = request.GET.get("term", "")
	system = list(System.objects.all().filter(name__istartswith = term).values("name"))
	return HttpResponse(json.dumps(system))

def update_fleet(request):
	timezone.activate(pytz.timezone("Iceland"))

	name = request.GET.get("name", "")
	description = request.GET.get("desc", "")
	fleet_types = request.GET.getlist("fleetType", "")
	#fc = Pilot.objects.get(name = request.GET.get("fc", ""))
	formup_loc = System.objects.get(name=request.GET.get("loc", ""))
	creator = Pilot.objects.get(name=request.session['username'])

	if(request.GET.get("now", "") == "true"):
		leaving = timezone.now()
	else:
		leaving = dateparse.parse_datetime(request.GET.get("leaving", ""))
		if(leaving!=None):
			leaving = pytz.timezone("Iceland").localize(leaving)
		else:
			leaving = timezone.now()

	if(	creator.current_fleet.fleet.fleet_commander == creator ):
		fleet = creator.current_fleet.fleet
		fleet.name = name;
		fleet.description = description

		fleets = FleetType.objects.all()
		fleets=fleets.filter(name__in=fleet_types)

		fleet.fleet_type.clear()
		for f in fleets:
			fleet.fleet_type.add(f)

		fleet.location = formup_loc
		fleet.leaving = leaving
		fleet.save()

		render_current_users_template(request)

		return HttpResponse("{\"success\":true}")

	return HttpResponse("{\"success\":false}")

def update_fleet_temp(request):
	t = loader.get_template('test_main/create_fleet.html')
	c = RequestContext(request, {
		"fleet_types" : FleetType.objects.all(),
		"update" : True,
		"u": Pilot.objects.get(name=request.session['username'])
	})
	return HttpResponse(t.render(c))

def create_fleet(request):
	timezone.activate(pytz.timezone("Iceland"))

	name = request.GET.get("name", "")
	description = request.GET.get("desc", "")
	fleet_types = FleetType.objects.all().filter(name__in=request.GET.getlist("fleetType", ""))
	#fc = Pilot.objects.get(name = request.GET.get("fc", ""))
	formup_loc = System.objects.get(name=request.GET.get("loc", ""))
	creator = Pilot.objects.get(name=request.session['username'])

	if(request.GET.get("now", "") == "true"):
		leaving = timezone.now()
	else:
		leaving = dateparse.parse_datetime(request.GET.get("leaving", ""))
		if(leaving!=None):
			leaving = pytz.timezone("Iceland").localize(leaving)
		else:
			leaving = timezone.now()

	old_fleets = Fleet.objects.all().filter(active=True, creator = creator) #| Fleet.objects.all().filter(active=True, fleet_commander = creator)  |Fleet.objects.all().filter(active=True, creator = fc) | Fleet.objects.all().filter(active=True, fleet_commander = fc) 
	#old_fleets = old_fleets.distinct()
	close_fleet_queryset(old_fleets)

	fleet = Fleet(name = name,
	description = description,
	fleet_commander = creator,#fc, 
	location = formup_loc, 
	created = timezone.now(), 
	active = True,
	leaving = leaving,
	creator = creator)
	fleet.save()	

	for tp in fleet_types:
		fleet.fleet_type.add(tp)

	join_fleet_nr(creator, fleet)
	#if(creator != fc):
	#	join_fleet(fc, fleet)

	fleet.save()

	render_current_users_template(request)

	return HttpResponse("{\"success\":true}")

def join_fleet_nr(pilot, fleet):
	timezone.activate(pytz.timezone("Iceland"))
	c_fleet = FleetMembership(pilot = pilot, fleet = fleet, join_date = timezone.now())
	c_fleet.save()
	if(pilot.current_fleet != None):
		pilot.current_fleet.leave_date=timezone.now()
		pilot.current_fleet.save()

	pilot.current_fleet = c_fleet
	pilot.looking_for_fleet = False
	pilot.save()

def leave_current_fleet(pilot):
	timezone.activate(pytz.timezone("Iceland"))
	if(pilot.current_fleet != None):
		pilot.current_fleet.leave_date = timezone.now()
		pilot.current_fleet.save()
		pilot.current_fleet = None
		pilot.save()

def update_fleet_list():
	timezone.activate(pytz.timezone("Iceland"))
	old_time = timezone.now()-datetime.timedelta(hours=4)

	older = Fleet.objects.all().filter(active = True, leaving__lt=old_time)

	close_fleet_queryset(older)

def join_fleet(request):
	if(is_signed_in(request)):
		user = Pilot.objects.get(name=request.session['username'])
		fleet = Fleet.objects.get(id = request.GET.get("id", ""))

		if(user.current_fleet != None):
			if(user.current_fleet.fleet.fleet_commander != user):
				leave_current_fleet(user)
			elif(user.current_fleet.fleet != fleet):
				disband_fleet(request)
			else:
				return HttpResponse(json.dumps({"success":False}))

		join_fleet_nr(user, fleet)
		render_current_users_template(request)
		return HttpResponse(json.dumps({"success":True}))
	return HttpResponse(json.dumps({"success":False}))

def leave_fleet(request):
	if(is_signed_in(request)):
		user = Pilot.objects.get(name=request.session['username'])

		if(user.current_fleet != None):
			if(user.current_fleet.fleet.fleet_commander != user):
				leave_current_fleet(user)
			else:
				disband_fleet(request)
		render_current_users_template(request)		
		return HttpResponse(json.dumps({"success":True}))
	return HttpResponse(json.dumps({"success":False}))

def disband_fleet(request):
	if(is_signed_in(request)):
		user = Pilot.objects.get(name=request.session['username'])

		if(user.current_fleet != None):
			fleets = Fleet.objects.all().filter(creator = user, id = user.current_fleet.fleet.id, active = True)
			close_fleet_queryset(fleets)
			render_current_users_template(request)
			return HttpResponse(json.dumps({"success":True}))

	return HttpResponse(json.dumps({"success":False}))

def close_fleet_queryset(fleet):
	timezone.activate(pytz.timezone("Iceland"))
	fleet_update = FleetMembership.objects.all().filter(fleet__in = fleet, leave_date = None)
	Pilot.objects.all().filter(current_fleet__in = fleet_update).update(current_fleet = None)
	fleet_update.all().update(leave_date = timezone.now())
	fleet.all().update(active=False)

def import_systems():
	systems = open('D:/Website Stuff/TEST/testproject/test_main/EVE_Systems.txt', "r")
	line = systems.readline()
	while(line != ""):
		val = line.split("\t")
		val[1] = val[1].strip("\n")
		print(val)

		try:
			region = Region.objects.get(name=val[1])
		except:
			region = Region(name=val[1])
			region.save()
		sys = System(name = val[0], region = region)
		sys.save()

		line = systems.readline()

def insert_dummy_data(request):
	import_systems()
	try:
		FleetType.objects.get(name="AHAC")
	except:
		FleetType(name="AHAC").save()
		FleetType(name="DrakeFleet").save()
		FleetType(name="Any").save()
		FleetType(name="Frigates").save()
		FleetType(name="Assault Frigates").save()
		FleetType(name="Rohktrine").save()

		return HttpResponse("{\"success\":true}")

def create_random_user(request):
	timezone.activate(pytz.timezone("Iceland"))
	p = Pilot(name="Random Man"+str(random.random()), 
			last_checkin = timezone.now(),
			looking_for_fleet = True,
			alert = False)
	p.save()

	num = random.randrange(0, FleetType.objects.all().count())
	f = FleetType.objects.all()

	for i in range(num):
		p.fleet_types.add(f[i])

	p.save()
	render_current_users_template(request)
	return HttpResponse("{\"success\":true}")

def create_random_fleet(request):
	timezone.activate(pytz.timezone("Iceland"))
	p = Pilot(name="Random Commander"+str(random.random()), 
			last_checkin = timezone.now(),
			looking_for_fleet = True,
			alert = False)
	p.save()
	r = random.random()
	f = ""

	ra = random.random()
	if(ra<0.25):
		time = timezone.now()
	elif(ra < 0.5):
		time = timezone.now()+datetime.timedelta(minutes = 30)
	elif(ra < 0.75):
		time = timezone.now()-datetime.timedelta(minutes = 40)
	elif(ra <=1 ): 
		time = timezone.now()+datetime.timedelta(minutes = 14)

	if(r>0.5):
		f=Fleet(name="A randomly generated fleet", 
			description="A randomly generated description of this made up fleet",
			fleet_commander = p,
			location = System.objects.all()[0],
			active=True,
			created = timezone.now(),
			leaving = time,
			creator = p )
	else:
		f=Fleet(name="A randomly generated fleet", 
			fleet_commander = p,
			location = System.objects.all()[0],
			active=True,
			created = timezone.now(),
			leaving = time,
			creator = p )

	f.save()
	num = random.randrange(0, FleetType.objects.all().count())
	fl = FleetType.objects.all()

	for i in range(num):
		f.fleet_type.add(fl[i])

	join_fleet_nr(p, f)

	num_people = random.randrange(0, 50)
	for i in range(num_people):
		p = Pilot(name="Random Man"+str(random.random()), 
			last_checkin = timezone.now(),
			looking_for_fleet = True,
			alert = False)
		p.save()
		num = random.randrange(0, FleetType.objects.all().count())

		for i in range(num):
			p.fleet_types.add(fl[i])
		p.save()
		join_fleet_nr(p, f)

	render_current_users_template(request)
	return HttpResponse("{\"success\":true}")


from django.db import models
from django.utils import timezone
import pytz
import datetime

class FleetType(models.Model):
	name = models.CharField(max_length=200, primary_key=True)

class Fleet(models.Model):
	name = models.CharField(max_length=260)
	description = models.CharField(max_length=500)
	id = models.AutoField(primary_key=True)
	fleet_commander = models.ForeignKey("Pilot", related_name='fleet_fleet_commander')
	location = models.ForeignKey("System")
	active = models.BooleanField()
	fleet_type = models.ManyToManyField(FleetType, related_name='fleet_fleet_type', null=True)
	created = models.DateTimeField()
	leaving = models.DateTimeField()
	creator = models.ForeignKey("Pilot", related_name='fleet_fleet_creator')

	def date_primary(fleet, fleet1):
		timezone.activate(pytz.timezone("Iceland"))
		delta = timezone.now()-fleet.leaving 
		if(delta.days == 0):
			if(delta.seconds <= 15*60):
				return delta.seconds
			else:
				return delta.seconds+15*60
		else:
			return (fleet.leaving - timezone.now()).seconds

		return 0


		

class FleetMembership(models.Model):
	pilot = models.ForeignKey("Pilot")
	fleet = models.ForeignKey("Fleet")
	join_date = models.DateTimeField()
	leave_date = models.DateTimeField(null=True, blank=True)

class Pilot(models.Model):
	name = models.CharField(max_length=200, primary_key=True)
	last_checkin = models.DateTimeField()
	looking_for_fleet = models.BooleanField()
	fleet_types = models.ManyToManyField(FleetType, related_name='pilot_fleet_type', null=True)
	current_fleet = models.ForeignKey("FleetMembership", null=True,blank=True, related_name="pilot_current_fleet")
	alert = models.BooleanField()

class Region(models.Model):
	name = models.CharField(max_length=200)

class System(models.Model):
	name = models.CharField(max_length=200)
	region = models.ForeignKey(Region)

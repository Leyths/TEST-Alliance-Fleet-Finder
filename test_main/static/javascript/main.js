
$(document).ready(function() {
	startPolling();
	$.timeago.settings.allowFuture = true;
	$("abbr.timeago").timeago();
});

$(document).ready(function() {
	setUpHandlers()
	updateFleetButton()
 });

function setUpHandlers()
{
	$("#update").off("click").click(function(){
		if($("#fleet_status_dropdown").html()=="")
		{
			working(true)
			$.ajax({url:"update_status.html", success:function(data) {
				working(false)
				$("#fleet_status_dropdown").html(data);
				$("#fleet_status_dropdown").show("blind");

				$("#cancel_btn").click(function(){
					$("#fleet_status_dropdown").hide("blind");
				});

				setUpChosen("#fleet_type")

				$("#submit_btn").click(function() {
					var multSelect = $("#fleet_type")[0];
					var total = 0;
					var queryString = "";
					for(var i=0; i< multSelect.length; i++)
						if(multSelect[i].selected)
						{
							total++;
							if(queryString == "")
								queryString+= "fleetType="+multSelect[i].value;
							else 
								queryString+= "&fleetType="+multSelect[i].value;
							g_alert_types.push(multSelect[i].value)
						}
					if(total>0)
					{
						g_alert = $("#alert").is(':checked');
						disableStatus(true)
						working(true)
						$.ajax({url:"./looking_for_fleet.html?"+queryString+"&alert="+g_alert, success:function(data) {
							$("#fleet_status_dropdown").hide("blind");
							console.log(data);
							disableStatus(false)
							working(false)
							$(".connection_status_text").html("Current Status: Looking for fleet");
							refreshContent();
							$("#cancel_lff").show();
						}, error:function(){
							error(true)
						}})
					}
					else
						$("#fleet_tp").css({"color":"red"});
				});
			}, error:function(){error(true)}}) 
		} else
		{
			$("#fleet_status_dropdown").stop().toggle("blind");
		}
		
	});

	setUpFleetEvents();
    
    $("#cancel_lff").click(function() {
    	working(true)
    	$.ajax({url:"./cancel_lff.html", success:function(data) {
					refreshContent();
					console.log(data)
					working(false)
			}, error:function(){error(true)}})
    });

    $("#leave_fleet").click(function(){
    	working(true)
    	$.ajax({url:"./leave_fleet.html", success:function(data) {
					refreshContent();
					console.log(data)
					working(false)
			}, error:function(){error(true)}})
    });

    $("#disband_fleet").click(function(){
    	working(true)
    	$.ajax({url:"./disband_fleet.html", success:function(data) {
					refreshContent();
					console.log(data)
					working(false)
			}, error:function(){error(true)}})
    });

}

function toggle(elem)
{
	if(elem.is(":visible"))
		elem.hide("blind")
	else
		elem.show("blind")
}
  
function setUpChosen(id)
{
	$(id).chosen(); 
	if(id == "#fleet_type")
		var op = "#fleet_tp";
	else if(id == "#fleet_fleet_type")
		var op = "#fleet_fleet_tp"
	$(id).chosen().change(function(){
		var multSelect = $(id)[0];
		$(op).css({"color":"black"});
		for(var i=0; i< multSelect.length; i++)
		{
			if(multSelect[i].selected && multSelect[i].value == "Any")
			{
				for(var j=0; j< multSelect.length; j++)
				{
					if(j!=i)
						multSelect[j].selected = false;
				}
				$(id).trigger("liszt:updated");
				break;
			}
		}
	}); 
}

function setupFleetWindow(updateCreate)
{
	var URL = "";
	var URL1 = "";
	var ttext = "";
	var stext = "";
	if(updateCreate == "create")
	{
		URL = "create_fleet.html";
		URL1 = "create_fleet_temp.html";
		ttext = "Create new fleet";
		stext = "Create fleet"
	} else
	{
		URL = "update_fleet.html";
		URL1 = "update_fleet_temp.html";
		ttext = "Update fleet"
		stext = "Update fleet"
	}
	if($("#fleet_creation").html() == "")
	{
		working(true)
		$.ajax({url:URL1, success:function(data) {
			working(false)
			$("#fleet_creation").html(data);
			setUpChosen("#fleet_fleet_type");
			
			$("#fleet_loc").ajaxChosen({
			    method: 'GET',
			    minTermLength:1,
			    url: './system_search.html',
			    dataType: 'json'
			}, function (data) {
			    var terms = {};
			    $.each(data, function (i, val) {
			        terms[val.name] = val.name;
			    });

			    return terms;
			});

			fleetWindow("show");

			$("#fleet_leaving").datetimepicker({currentText: '', dateFormat:"yy-mm-dd", timeFormat:"hh:mm:ss"});
			$("#leaving_now").click(function(){
				$("#fleet_leaving").toggle();
			});

			$("#submit_fleet_btn").click(function(){
				validateNewFleet(true, URL);
			});

			$("#cancel_fleet_btn").click(function(){
				fleetWindow("hide")
			});

			blurCSSReset("#fleet_name");
			blurCSSReset("#fleet_loc");
			blurCSSReset("#fleet_leaving");
			$("#leaving_now").click(function(){$("#fleet_leaving_text").css({"color":"black"})})
		}, error:function(){error(true)}})
	} else
	{
		$("#fleet_c_title_text").html(ttext)
		$("#submit_fleet_btn").html(stext)
		fleetWindow("show");
	}
}

function setUpFleetEvents()
{
	var fc_verified = true;//false;
	$(".create_fleet").off("click").click(function(){

		setupFleetWindow("create")

		/*$("#fleet_commander").blur(function(){
			var pilot_name = $("#fleet_commander").val();
			$.ajax({url:"./search_for_user.html?user="+pilot_name, success:function(data) {
				var d = JSON.parse(data)
				fc_verified = d.success;

				if(!fc_verified)
					$("#fc_tooltip").html("No user exists with this name").css({"color":"red"});
				else
					$("#fc_tooltip").html("");
			}, error:function(){ 
				
			}});
		});*/
	});

	$("#update_fleet").off("click").click(function(){
		setupFleetWindow("update")
	})

	$(".fleet .btn").off("click").click(function(){
		var classes= $(this).attr("class").split(/\s+/);
		var dropdown = false;
		var fleet_num = "";
		$.each( classes, function(index, item){
    		if (item.substr(0, 6) == "fleet_") {
    			fleet_num = item.substr(6, item.length);
   			 }
   			if(item == "dropdown-toggle")
   				dropdown = true;
		});
		if(!dropdown)
			$(".fleet_members.fleet_"+fleet_num).stop().toggle("blind");
	});

	$("#join_fleet").off("click").click(function(){
		var id="";
		var tclass = $(this).attr("class");

		id=tclass.substr(6, tclass.length);

		$.ajax({url:"./join_fleet.html?id="+id, success:function(data) {
			refreshContent();
		}, error:function(){error(true)}})
	});
} 

function fleetWindow(showHide)
{
	if(showHide == "show")
	{
		$("#body").hide("blind", function(){	
			$("#fleet_creation").show("blind");
		});
	} else
	{
		$("#fleet_creation").hide("blind", function(){	
			$("#body").show("blind");
		});
	}
}

function blurCSSReset(id)
{
	$(id).blur(function(){
			if($(id).val()!="")
				$(id+"_text").css({"color":"black"});
		});
}

function validateNewFleet(fc_verified, URL)
{
	var cont = true;
	var queryString = "";

	if($("#fleet_name").val()=="")
	{
		$("#fleet_name_text").css({"color":"red"});
		cont = false;
	} else
	{
		queryString+="name="+$("#fleet_name").val()+"&";
	}

	var multSelect = $("#fleet_fleet_type")[0];
	var total = 0;
	for(var i=0; i< multSelect.length; i++)
		if(multSelect[i].selected)
		{
			total++;
			queryString+= "fleetType="+multSelect[i].value+"&";
		}
	if(total>0)
	{
		$("#fleet_fleet_tp").css({"color":"black"})
	}
	else
	{
		$("#fleet_fleet_tp").css({"color":"red"});
		cont = false;
	}


	if($('#fleet_loc option:selected').val()=="" || $('#fleet_loc option:selected').val()==undefined)
	{
		$("#fleet_loc_text").css({"color":"red"});
		cont = false;
	} else
	{
		queryString+="loc="+$('#fleet_loc option:selected').val()+"&";
	}

	queryString+="desc="+$("#fleet_description").val()+"&"

	if($("#fleet_leaving").val()=="" && (!$("#leaving_now").is(':checked')))
	{
		$("#fleet_leaving_text").css({"color":"red"});
		cont = false;
	} else
	{
		queryString+="now="+$("#leaving_now").is(':checked')+"&";
		//if(leaving )
		queryString+="leaving="+$("#fleet_leaving").val();
	}
	if(cont)
	{
		disableFleet(true)
		working(true)
		$.ajax({url:URL+"?"+queryString, success:function(data) {
			console.log(data);
			fleetWindow("hide")
			disableFleet(false)
			working(false)
			$(".connection_status_text").html("Current Status: In a fleet");
			refreshContent();
		}, error:function(){ console.log("Failed to update"); error(true)}});
	}
}

function working(working)
{
	hide = false;
	if(working)
	{
		hide = false;
		var id = setInterval(function(){
			if(!hide)
				$("#alert_message_working").fadeIn();
			clearInterval(id)
		}, 1000)
	} else
	{
		hide = true;
		$("#alert_message_working").hide()
		error(false)
	}
}

function error(error)
{
	console.log("error")
	hide = false;
	if(error)
	{
		hide = false;
		var id = setInterval(function(){
			if(!hide)
				$("#alert_message_error").fadeIn();
				clearInterval(id)
		}, 100)
	} else
	{
		hide = true;
		$("#alert_message_error").hide()
	}
}

function disableFleet(disable)
{
	if(disable)
	{
		$("#fleet_name").attr("disabled", "disabled");
		$("#fleet_description").attr("disabled", "disabled");
		$("#fleet_fleet_type").attr("disabled", "disabled");
		$("#fleet_fleet_type").trigger("liszt:updated");
		$("#fleet_loc").attr("disabled", "disabled");
		$("#fleet_loc").trigger("liszt:updated");
		$("#fleet_leaving").attr("disabled", "disabled");
		$("#submit_fleet_btn").attr("disabled", "disabled");
		$("#cancel_fleet_btn").attr("disabled", "disabled");
		$("#leaving_now").attr("disabled", "disabled");
	} else
	{
		$("#fleet_name").removeAttr("disabled");
		$("#fleet_description").removeAttr("disabled");
		$("#fleet_fleet_type").removeAttr("disabled");
		$("#fleet_fleet_type").trigger("liszt:updated");
		$("#fleet_loc").removeAttr("disabled");
		$("#fleet_loc").trigger("liszt:updated");
		$("#fleet_leaving").removeAttr("disabled");
		$("#submit_fleet_btn").removeAttr("disabled");
		$("#cancel_fleet_btn").removeAttr("disabled");
		$("#leaving_now").removeAttr("disabled");
	}
}

function disableStatus(disable)
{
	if(disable)
	{
		$("#fleet_type").attr("disabled", "disabled");
		$("#fleet_type").trigger("liszt:updated");
		$("input#alert").attr("disabled", "disabled");
		$("#submit_btn").attr("disabled", "disabled");
		$("#cancel_btn").attr("disabled", "disabled");
	} else
	{
		$("#fleet_type").removeAttr("disabled");
		$("#fleet_type").trigger("liszt:updated");
		$("input#alert").removeAttr("disabled");
		$("#submit_btn").removeAttr("disabled");
		$("#cancel_btn").removeAttr("disabled");
	}
}

function refreshContent()
{
	$.ajax({url:"./update.html", success:function(data) {

		var result = JSON.parse(data);

		var elem = $(result.body)
		updateFleetList(elem)
		updatePilotList(elem)
		updateInfo(result.info)

		$("#pilot_info").html(result.pilot_info)
		setUpFleetEvents();
		setUpHandlers();
		jQuery("abbr.timeago").timeago();

		updateFleetButton();

	}, error:function(){ console.log("Failed to update"); error(true)}});
}

function updateFleetButton()
{
	if($("#disband_fleet").css("display") != "none")
		$("#create_fleet").hide()
	else
		$("#create_fleet").show()
}

function updateFleetList(body)
{
	var fleet = $("#fleets");

	var fleets = fleet.find(".fleet_cont");

	var fl_array = [];

	fleets.each(function(i, val){
		var id = $(val).attr("id");
		if(id!=undefined)
		{
			if(id.substr(0, 6) == "fleet_")
			id = id.substr(6, id.length)
			if(id!="")
				fl_array.push([id, "", false])
		}
	});

	body.find("#fleets").find(".fleet_cont").each(function(i, val){
		var id = $(val).attr("id");
		if(id!=undefined)
		{
			if(id.substr(0, 6) == "fleet_")
				id = id.substr(6, id.length)
			if(id!="")
			{
				var inserted = false;
				for(var it = 0; it<fl_array.length; it++)
				{
					if(fl_array[it][0] == id)
					{
						inserted = true;
						fl_array[it][1] = $(val);
						fl_array[it][2] = false;
						break;
					}
				}
				if(!inserted)
					fl_array.push([id, $(val), true])
			}
		}
	});

	for(var it = 0; it<fl_array.length; it++)
	{
		var id = fl_array[it][0];
		var content = fl_array[it][1];
		var newElem = fl_array[it][2]
		if(!newElem)
		{
			var dom_elem = $(fleet.find("#fleet_"+id));
			if(content!="")
			{
				//console.log("Updating existing fleet content id="+id)
				$(dom_elem.find(".fleet")).html($(content.find(".fleet")).html())
				$(dom_elem.find(".fleet_members")).html($(content.find(".fleet_members")).html())
			} else
			{
				//console.log("Removing disbanded fleet id="+id)
				var removeE = dom_elem
				dom_elem.fadeOut(300, function(){removeE.remove();})
			}
		} else
		{
			//console.log("Adding new fleet id="+id)
			fleet.prepend(content);

			if(true)//g_alert)
			{
				var label = content.find(".labels .label")
				outer:
				for(var i=0; i<label.length; i++)
				{
					for(var j=0; j<g_alert_types.length; j++)
					{
						if($(label[i]).html() == g_alert_types[j] || g_alert_types[j] == "Any")
						{
							playAlert();
							break outer;
						}
					}
				}
			}
		}


	}
}

function playAlert()
{
	console.log("Alert")
	document.getElementById("alert").play()
}

function updatePilotList(body)
{
	$("#pilots").html(body.find("#pilots").html());
}

function updateInfo(body)
{
	$("#info_cont").html(body)
}
  
 function startPolling() {
	var intId= setInterval(function() {
		refreshContent();
		console.log("Updating");
	}, 20000);
}
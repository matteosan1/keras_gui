$(document).ready(function() {

    $(".btn").click(function(event) {
	$(this).blur();
    });

    $(".selectpicker").click(function(event) {
	$(this).blur();
    });

    $('.dropdown').each(function (key, dropdown) {
        var $dropdown = $(dropdown);
        $dropdown.find('.dropdown-menu a').on('click', function () {
	    $dropdown.find('button').text($(this).text()).append(' <span class="caret"></span>');
        });
    });

    var counter=0;
    $("#add_row").click(function(){
	$('#addr'+counter).html("<td><select class='form-control bldg-menu selectpicker' id=type"+counter+"' name='type' data-live-search='true' required><option disabled='' selected='' value=''>Select...</option><option value='Linear'>Linear</option><option value='Convolution'>Convolution</option><option value='Flatten'>Flatten</option><option value='MaxPool'>MaxPool</option></select></td><td><input class='form-control' type='number' id='neurons"+counter+"' name='neurons' min='1' max='100' step='1' value='1'></td><td><select class='form-control bldg-menu selectpicker' id='activation"+counter+"' name='activation' data-live-search='true' required><option disabled='' selected='' value=''>Select...</option><option value='sigmoid'>Sigmoid</option><option value='relu'>ReLU</option><option value='tanh'>Tanh</option><option value='softmax'>Softmax</option></select></td>");
	$('#tab_logic').append('<tr id="addr'+(counter+1)+'"></tr>');
	counter++;
    });
    $("#delete_row").click(function(){
    	if(counter>1){
	    $("#addr"+(counter-1)).html('');
	    counter--;
	}
    });

    function addLayer() {
	var table = document.getElementById('layers');
	var rowCount = table.rows.length;
	var cellCount = table.rows[0].cells.length; 
	var row = table.insertRow(rowCount);
	for(var i=0; i < cellCount; i++) {
	    var cell = 'cell'+i;
	    cell = row.insertCell(i);
	    var copycel = document.getElementById('col'+i).innerHTML;
	    cell.innerHTML=copycel;
	}
    }
    
    $('#addLayer').on('click', function(event) {
	event.preventDefault();
	addLayer();
    });

    $('#deleteLayer').on('click', function(event) {
	event.preventDefault();
	var table = document.getElementById('layers');
	var rowCount = table.rows.length;
	if(rowCount > '2'){
	    var row = table.deleteRow(rowCount-1);
	    rowCount--;
	}
    });

    $('#load_template').on('click', async function(event) {
	event.preventDefault();
	var nnname = document.getElementById("nnname").value;
	const url = ('/look_for_template?' +
		     new URLSearchParams({nnname: nnname}).toString()
		    );
	await fetch(url)
	    .then(response => response.json())
	    .then(function(data) {
		if (!$.isEmptyObject(data)) {
		    document.getElementById("datafile").disabled = true;
		    document.getElementById("loaded_file").innerHTML = "Sample loaded from " + data['filename'];
		    populate(data['cols'], "xparams", "yparams");
		    for (i=0; i<data['neurons'].length; i++) {
			document.getElementById("add_row").click();
		    	parent = document.getElementById("addr"+i);
		    	children = parent.querySelectorAll('.form-control');
			children[0].value = data['type'][i];
		    	children[1].value = data['neurons'][i];
		    	children[2].value = data['activation'][i];
		    }
		    
		    for (var key in data){
			var ele = document.getElementById(key);
			if (ele === null) {
			    continue;
			}			
			if (key == "nnname") {
			    continue;
			} else if (key == "scaling") {
			    ele.checked = true;
			} else if (key.endsWith("_x") || key.endsWith("_y"))  {
			    ele.checked = true;
			} else if (key == "filename") {
			    continue;
			} else {
			    ele.value = data[key];
			}
		    }		  
		} else {
		    document.getElementById("load_template").disabled = true;
		}
	    });
    });
    
    $('#createModel').on('click', async function(event) {
	event.preventDefault();
	var myform = document.getElementById("trainingForm");
	var formData = new FormData(myform);
	var label = document.getElementById('loaded_file').innerText
	if (label != "") {
	    label = label.split("from ")[1];
	    formData.append('loaded_file', label)
	}
	await fetch("/create_model", {
	    method: "POST",
	    body: formData,
	})
	    .then(response => response.json())
	    .then(function(response) {
		if (response['msg'] != "OK") {
		    $("#"+response['type']).text(response['msg'])
		    $("#"+response['type']).fadeTo(2000, 500).slideUp(500, function() {
			$("#"+response['type']).slideUp(500);
		    });
		} else {
		    location.assign("/train_model");
		}
	    });
    });
    
    $("#datafile").change(async function() {
	let formData = new FormData();
	formData.append("file", datafile.files[0]);
	const response = await fetch('/loaddata', {
	    method: "POST",
	    body: formData,
	});
	const json = await response.json();
	populate(json, 'xparams', 'yparams');
    });
});

function enable_button() {
    if(document.getElementById("nnname").value==="") { 
        document.getElementById('load_template').disabled = true; 
    } else { 
        document.getElementById('load_template').disabled = false;
    }
}

function createCheckBox(parent, text) {
    var label = document.createElement('label')	
    var checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    if (parent.id == "xparams") {
	checkbox.name = text + "_x";
	checkbox.id = text + "_x";
    } else {
	checkbox.id = text + "_y";
	checkbox.name = text + "_y";
    }
    checkbox.value = text;
    label.appendChild(checkbox)
    label.appendChild(document.createTextNode(text));
    parent.appendChild(label);
    parent.appendChild(document.createElement("br"));
}

function populate(optionArray, xparams, yparams) {
    var xp = document.getElementById(xparams);
    var yp = document.getElementById(yparams);
    xp.replaceChildren();
    yp.replaceChildren();
    
    for (i = 0; i < optionArray.length; ++i) {
	var pair = optionArray[i];
	createCheckBox(xp, pair);
	createCheckBox(yp, pair);
    }
}

    

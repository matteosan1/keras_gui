$( document ).ready(function() {
    const config = {
        type: 'line',
        data: {
            labels: [],
            datasets: [
		{
                    label: "Training loss",
                    backgroundColor: 'rgb(255, 99, 132)',
                    borderColor: 'rgb(255, 99, 132)',
                    data: [],
                    fill: false
		},
		{
		    label: "Test loss",
                    backgroundColor: 'rgb(13, 117, 248)',
                    borderColor: 'rgb(13, 117, 248)',
                    data: [],
                    fill: false
		}],
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: 'Model Loss'
            },
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Epochs'
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Loss'
                    }
                }]
            }
        }
    };

    const context = document.getElementById('canvas').getContext('2d');
    const lineChart = new Chart(context, config);

    var source = new EventSource("/listen");
    
    $(".btn").click(function(event) {
	$(this).blur();
    });

    $('#save').on('click', async function(event) {
	event.preventDefault();
	await fetch("/save_model")
	    .then(response => response.json())
	    .then(function(data) {
		if (data.status == "OK") {
		    $("#model_saved").text(data.msg);
		    $("#model_saved").fadeTo(2000, 500).slideUp(500, function() {
			$("#model_saved").slideUp(500); });
		} else {
		    $("#model_not_saved").text(data.msg);
		    $("#model_not_saved").fadeTo(2000, 500).slideUp(500, function() {
			$("#model_not_saved").slideUp(500); });
		}
	    });	
    });
    
    $('#train').on('click', function(event) {
	event.preventDefault();
	document.getElementById("save").disabled = true;
	document.getElementById("epochs").innerText = "";
	document.getElementById("loss_train").innerText = "";
	document.getElementById("loss_test").innerText = "";
	config.data.datasets[0].data.length = 0;
	config.data.datasets[1].data.length = 0;
	config.data.labels.length = 0;
	lineChart.update();
	fetch("/start_training", {
	    method: "GET",
	});
    });

    source.onerror = function(event) {
	// FIXME throw an error
    	source.close();
    }

    source.addEventListener("end", (e) => {
	const data = JSON.parse(e.data);
	document.getElementById("epochs").innerText = "Epochs: " + data.epochs;
	document.getElementById("loss_train").innerText = "Final Model Loss (Train): " + data.loss;
	document.getElementById("loss_test").innerText = "Final Model Loss (Test): " + data.val_loss;
	document.getElementById("save").disabled = false;
	// eventualmente si puo` chiudere la connessione
    });
    
    source.addEventListener("loss", (e) => {
	const data = JSON.parse(e.data);
        if (config.data.labels.length === 20) {
            config.data.labels.shift();
            config.data.datasets[0].data.shift();
	    config.data.datasets[1].data.shift();
        }
        config.data.labels.push(data.epoch);
        config.data.datasets[0].data.push(data.loss);
	config.data.datasets[1].data.push(data.val_loss);
        lineChart.update();
	//document.getElementById('loss').innerHTML = "Epoch: " + data.epoch + " loss: " + data.loss;
    });
});
    

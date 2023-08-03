$( document ).ready(function() {
    const config = {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: "Training loss",
                backgroundColor: 'rgb(255, 99, 132)',
                borderColor: 'rgb(255, 99, 132)',
                data: [],
                fill: false,
            }],
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: 'Creating Real-Time Charts with Flask'
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

    $('#train').on('click', function(event) {
	event.preventDefault();
	fetch("/start_training", {
	    method: "GET",
	});
    });

    source.onerror = function(event) {
    	console.error("PUPPA");
    	source.close();
    }

    source.addEventListener("end", (e) => {
	console.log("FINE TRAINING");
	// eventualmente si puo` chiudere la connessione
    });
    
    source.addEventListener("loss", (e) => {
	const data = JSON.parse(e.data);
        //if (config.data.labels.length === 20) {
        //    config.data.labels.shift();
        //    config.data.datasets[0].data.shift();
        //}
        config.data.labels.push(data.epoch);
        config.data.datasets[0].data.push(data.loss);
        lineChart.update();
	document.getElementById('loss').innerHTML = "Epoch: " + data.epoch + " loss: " + data.loss;
    });
});
    


var chartCanvas = document.getElementById("chart");
var summaryChart = new Chart(chartCanvas, {
    type: 'line',
    data: {
        datasets: [
            {
                data: {{ added_data|safe }},
                label: 'New requests',
                fill: 'origin',
                backgroundColor: 'rgba(255, 0, 0, 0.4)',
                borderColor: 'rgba(255, 0, 0, 1)',
                lineTension: 0
            }
        ]
    },
    options: {
        tooltips: {
            mode: 'x'
        },
        legend: {
            position: 'bottom'
        },
        hover: {
            animationDuration: 0
        },
        scales: {
            yAxes: [{
                stacked: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Number of requests'
                }
            }],
            xAxes: [{
                type: 'time',
                distribution: 'linear'
            }]
        },
        scaleBeginAtZero: true,
        maintainAspectRatio: false,
        responsive: true
    }
});
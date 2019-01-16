
var chartCanvas = document.getElementById("chart");
var summaryChart = new Chart(chartCanvas, {
    type: 'line',
    data: {
        datasets: [
            {
                data: {{ activity|safe }},
                label: 'Activity',
                borderColor: 'rgba(0, 128, 0, 1)',
                backgroundColor: 'rgba(255, 255, 255, 0)',
                pointRadius: 4,
                pointBorderWidth: 2,
                pointBackgroundColor: 'rgba(255, 255, 255, 1)',
                pointHoverBackgroundColor: 'rgba(255, 255, 255, 1)',
                pointHoverRadius: 5,
                lineTension: 0
            }
        ]
    },
    options: {
        tooltips: {
            mode: 'x'
        },
        legend: {
            display: false,
            position: 'bottom'
        },
        hover: {
            animationDuration: 0
        },
        scales: {
            yAxes: [{
                scaleLabel: {
                    display: true,
                    labelString: 'Activity'
                },
                ticks: {
                    beginAtZero: true,
                    callback: function(value) {if (Number.isInteger(value)) {return value;}}
                }
            }],
            xAxes: [{
                stacked: true,
                type: 'time',
                distribution: 'linear',
            }]
        },
        scaleBeginAtZero: true,
        maintainAspectRatio: false,
        responsive: true
    }
});
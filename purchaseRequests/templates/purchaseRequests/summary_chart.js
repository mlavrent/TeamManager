
var chartCanvas = document.getElementById("chart");
var summaryChart = new Chart(chartCanvas, {
    type: 'line',
    data: {
        datasets: [
            {
                data: {{ added_data|safe }},
                label: 'New requests',
                backgroundColor: 'rgba(255, 128, 0, 0.4)',
                borderColor: 'rgba(255, 128, 0, 1)',
                fill: 'origin',
                lineTension: 0
            },
            {
                data: {{ approved_data|safe }},
                label: 'Approvals',
                backgroundColor: 'rgba(0, 128, 0, 0.4)',
                borderColor: 'rgba(0, 128, 0, 1)',
                fill: '-1',
                lineTension: 0
            },
            {
                data: {{ order_data|safe }},
                label: 'Purchases',
                backgroundColor: 'rgba(255, 128, 128, 0.4)',
                borderColor: 'rgba(255, 128, 128, 1)',
                fill: '-1',
                lineTension: 0
            },
            {
                data: {{ delivery_data|safe }},
                label: 'Deliveries',
                backgroundColor: 'rgba(162, 59, 114, 0.4)',
                borderColor: 'rgba(162, 59, 114, 1)',
                fill: '-1',
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
                },
                ticks: {
                    beginAtZero: true
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
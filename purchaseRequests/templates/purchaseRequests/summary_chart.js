
Chart.defaults.global.defaultFontColor = 'black';
Chart.defaults.global.defaultFontFamily = '"Trebuchet MS", Roboto, Helvetica, sans-serif';
Chart.defaults.global.elements.line.borderWidth = 2.5;
Chart.defaults.global.elements.line.borderJoinStyle = 'bevel';
Chart.defaults.global.elements.line.fill = false;
Chart.defaults.global.elements.line.tension = 0;

Chart.defaults.global.elements.point.radius = 4;
Chart.defaults.global.elements.point.borderWidth = 2;
Chart.defaults.global.elements.point.borderColor = 'rgba(255, 255, 255, 1)';
Chart.defaults.global.elements.point.hoverRadius = 5;
Chart.defaults.global.elements.point.hitRadius = 10;

var chartCanvas = document.getElementById("chart");
var summaryChart = new Chart(chartCanvas, {
    type: 'line',
    data: {
        datasets: [
            {
                data: {{ activity|safe }},
                label: 'Activity',
                borderColor: '#28a745',
                pointBorderColor: '#fff',
                pointHoverBorderColor: '#fff',
                pointBackgroundColor: '#28a745',
                yAxisID: 'A'
            },
            {
                data: {{ spending|safe }},
                label: 'Money spent',
                borderColor: '#005cc5',
                pointBorderColor: '#fff',
                pointHoverBorderColor: '#fff',
                pointBackgroundColor: '#005cc5',
                yAxisID: 'B'
            }
        ]
    },
    options: {
        tooltips: {
            mode: 'x',
            callbacks: {
                label: function(tooltipItem, chart) {
                    if(tooltipItem.datasetIndex === 1) {return "Spending: $ " + tooltipItem.yLabel.toFixed(2);}
                    else {return "Activity: " + tooltipItem.yLabel.toFixed(0);}
                }
            }
        },
        legend: {
            display: false,
            position: 'bottom'
        },
        hover: {
            animationDuration: 0
        },
        scales: {
            yAxes: [
                {
                    id: 'A',
                    gridLines: {zeroLineColor: 'rgba(0, 0, 0, 0)'},
                    ticks: {
                        beginAtZero: true,
                        suggestedMax: 4,
                        callback: function(value) {if (Number.isInteger(value)) {return value;}}
                    }
                },
                {
                    id: 'B',
                    position: 'right',
                    gridLines: {zeroLineColor: 'rgba(0, 0, 0, 0)'},
                    ticks: {
                        beginAtZero: true,
                        suggestedMax: 100,
                        callback: function(value) {if (value % 10 === 0) {return '$' + value;}}
                    },
                    gridLines: {
                        color: 'rgba(0, 0, 0, 0)',
                    }
                }
            ],
            xAxes: [{
                type: 'time',
                distribution: 'linear',
                time: {
                    unit: "{{ interval }}",
                    tooltipFormat: "{{ tt_format }}"
                }
            }]
        },
        scaleBeginAtZero: true,
        maintainAspectRatio: false,
        responsive: true
    }
});
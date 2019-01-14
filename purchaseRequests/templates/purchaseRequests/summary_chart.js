
var chartCanvas = document.getElementById("chart");
var summaryChart = new Chart(chartCanvas, {
    type: 'line',
    data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Aug'],
        datasets: [
            {
                data: [1, 2, 3, 2, 0, 1],
                label: 'New requests',
                fill: 'origin',
                backgroundColor: 'rgba(255, 187, 0, 0.4)',
                borderColor: 'rgba(255, 187, 0, 1)',
                lineTension: 0
            },
            {
                data: [2, 0, 4, 1, 3, 2],
                label: 'Approvals',
                fill: '-1',
                backgroundColor: 'rgba(0, 128, 0, 0.4)',
                borderColor: 'rgba(0, 128, 0, 1)',
                lineTension: 0
            },
            {
                data: [2, 4, 3, 1, 1, 0],
                label: 'Purchases',
                fill: '-1',
                backgroundColor: 'rgba(249, 219, 189, 0.6)',
                borderColor: 'rgba(249, 219, 189, 1)',
                lineTension: 0
            },
            {
                data: [1, 2, 1, 0, 1, 3],
                label: 'Deliveries',
                fill: '-1',
                backgroundColor: 'rgba(162, 59, 114, 0.4)',
                borderColor: 'rgba(162, 59, 114, 1)',
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
                stacked: true
            }]
        },
        scaleBeginAtZero: true,
        maintainAspectRatio: false,
        responsive: true
    }
});
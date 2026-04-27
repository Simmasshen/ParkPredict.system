let peakChart = null;
let zoneChart = null;

function renderPeakChart(data){
    const ctx = document.getElementById("peakChart");

    const labels = Object.keys(data);
    const values = Object.values(data);

    if(peakChart){
        peakChart.destroy();
    }

    peakChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Parking Usage by Hour',
                data: values
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function renderZoneChart(data){
    const ctx = document.getElementById("zoneChart");

    if(zoneChart){
        zoneChart.destroy();
    }

    zoneChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data)
            }]
        },
        options: {
            responsive: true
        }
    });
}
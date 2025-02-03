document.addEventListener('DOMContentLoaded', function() {
    // Initialize score progress chart
    const scoreCtx = document.getElementById('scoreProgressChart').getContext('2d');
    new Chart(scoreCtx, {
        type: 'line',
        data: {
            labels: gameDates,
            datasets: [{
                label: 'Score Progress',
                data: gameScores,
                borderColor: '#009fdc',
                backgroundColor: 'rgba(0, 159, 220, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: 'rgba(255, 255, 255, 0.7)' }
                },
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: 'rgba(255, 255, 255, 0.7)' }
                }
            }
        }
    });

    // Initialize skills radar chart
    const skillsCtx = document.getElementById('skillsRadarChart').getContext('2d');
    new Chart(skillsCtx, {
        type: 'radar',
        data: {
            labels: categories,
            datasets: [{
                label: 'Skills',
                data: skillScores,
                backgroundColor: 'rgba(0, 159, 220, 0.2)',
                borderColor: '#009fdc',
                pointBackgroundColor: '#009fdc'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    pointLabels: { color: 'rgba(255, 255, 255, 0.7)' },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)',
                        backdropColor: 'transparent'
                    }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
});
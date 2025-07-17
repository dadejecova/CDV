 // Parse JSON data
        const barLabels = JSON.parse(document.getElementById('bar-labels').textContent);
        const barPrices = JSON.parse(document.getElementById('bar-prices').textContent);
        const historicalData = JSON.parse(document.getElementById('historical-data').textContent);
        const coinColors = JSON.parse(document.getElementById('coin-colors').textContent);
        const topCoins = JSON.parse(document.getElementById('top-coins').textContent);

        // Function to get color by coin ID (fallback to random)
        function getColor(coinId) {
            return coinColors[coinId] || '#' + Math.floor(Math.random()*16777215).toString(16);
        }

        // Bar Chart
        new Chart(document.getElementById('barChart'), {
            type: 'bar',
            data: {
                labels: barLabels,
                datasets: [{
                    label: 'Current Price (USD)',
                    data: barPrices,
                    backgroundColor: barLabels.map(label => getColor(topCoins.find(c => c.name === label).id)),
                }]
            },
            options: {
                scales: {
                    y: { type: 'logarithmic', beginAtZero: false }
                },
                plugins: { legend: { display: true } },
                responsive: true,
            }
        });

        // Line Chart
        const dates = historicalData.dates || [];
        new Chart(document.getElementById('lineChart'), {
            type: 'line',
            data: {
                labels: dates,
                datasets: Object.keys(historicalData).filter(k => k !== 'dates').map(coinId => ({
                    label: topCoins.find(c => c.id === coinId).name,
                    data: historicalData[coinId],
                    borderColor: getColor(coinId),
                    fill: false,
                }))
            },
            options: {
                scales: {
                    y: { title: { display: true, text: 'Indexed Price (%)' } }
                },
                plugins: { legend: { display: true } },
                responsive: true,
            }
        });
export function createPieChart(id, xlabels, ydata, title) {
    const barColors = [
        "red",
        "orange",
        "yellow",
        "green",
        "blue",
        "purple",
        "pink"
    ];

    const chart = new Chart(id, {
        type: "pie",
        data: {
            labels: xlabels,
            datasets: [{
                backgroundColor: barColors,
                data: ydata,
                borderWidth: 1,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: title,
                    font: {
                        size: 16,
                    }
                },
                legend: {
                    position: 'bottom'
                }
            }
        }
    });

    return chart;
}

export function createPurchasePieChart(id) {
    eel.get_transaction_percentages()(function(data) {
        const xlabels = data.map(item => item[0] || 'Uncategorized');
        const ydata = data.map(item => item[2]);
        const title = "Types of Purchases"
        const chart = createPieChart(id, xlabels, ydata, title);
    });
}
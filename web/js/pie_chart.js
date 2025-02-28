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
    const xlabels = ['Housing & Utilities', 'Food', 'Transportation', 'Health', 'Finance','Entertainment','Other']
    const ydata = [40, 15, 0, 10, 20, 5, 10]
    const title = "Types of Purchases"
    const chart = createPieChart(id, xlabels, ydata, title);
}
export function createPieChart(id, xlabels, ydata, title, onClick) {
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
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            return `${label}: ${value}%`;
                        }
                    }
                },
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
            },
            onClick: (event, elements) => {
                if (elements.length > 0) {
                    const index = elements[0].index;
                    if (onClick && typeof onClick === 'function') {
                        onClick(xlabels[index], ydata[index]);
                    }
                }
            },
            onHover: (event, elements) => {
                const canvas = event.native.target;
                canvas.style.cursor = elements.length ? 'pointer' : 'default';
            },
        }
    });

    return chart;
}

export function createPurchasePieChart(id) {
    eel.get_category_values()(function(data) {
        const xlabels = data.map(item => item[0] || 'Uncategorized');
        const ydata = data.map(item => item[2]);
        const title = "Types of Purchases"

        const handleClick = (label, value) => {
            console.log(`Clicked on category ${label}`);
            budgetingTransactionsTable(label);

            const tableContainer = document.getElementById('table-container');
            tableContainer.innerHTML = '';

            const table = window.budgetingTransactionsTable(label);
            tableContainer.appendChild(table);
            
        };


        const chart = createPieChart(id, xlabels, ydata, title, handleClick);
    });
}
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

export function createPurchasePieChartByPercent(id, mode) {
    eel.get_category_percentages(mode)(function(data) {
        const xlabels = data.map(item => item[0] || 'Uncategorized');
        const ydata = data.map(item => item[2]);
        var title;
        if (mode == 1){
            title = "Purchase Categories by Percentage";
        }
        else if (mode == 2){
            title = "Deposit Categories by Percentage";
        }
        const handleClick = (label, value) => {
            console.log(`Clicked on category ${label} with value ${value}`);
            var tableContainer;
            if (mode == 1){
                tableContainer = document.getElementById('table-container-1');
            }
            else if (mode == 2){
                tableContainer = document.getElementById('table-container-2');
            }
            if (!tableContainer) {
                console.error("Could not find element");
                return;
            }
            
            tableContainer.innerHTML = '';
            const loadingMessage = document.createElement('div');
            loadingMessage.textContent = `Loading transactions for ${label}...`;
            tableContainer.appendChild(loadingMessage);
            
            // Create the table
            const table = budgetingTransactionsTable(label, mode);
        };

        const chart = createPieChart(id, xlabels, ydata, title, handleClick);
    });
}


export function createPurchasePieChartByAmount(id) {
    eel.get_category_percentages()(function(data) {
        const xlabels = data.map(item => item[0] || 'Uncategorized');
        const ydata = data.map(item => item[2]);
        const title = "Purchase Categories by Amount"

        const handleClick = (label, value) => {
            console.log(`Clicked on category ${label} with value ${value}`);
            const tableContainer = document.getElementById('table-container');
            if (!tableContainer) {
                console.error("Could not find table-container element");
                return;
            }
            
            tableContainer.innerHTML = '';
            const loadingMessage = document.createElement('div');
            loadingMessage.textContent = `Loading transactions for ${label}...`;
            tableContainer.appendChild(loadingMessage);
            
            // Create the table
            const table = budgetingTransactionsTable(label);
        };

        const chart = createPieChart(id, xlabels, ydata, title, handleClick);
    });
}
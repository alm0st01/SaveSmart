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

export function createLineChart(id, xData, yData, title) {
    const chart = new Chart(id, {
        type: 'line',
        data: {
            labels: xData,
            datasets: [{
                label: 'Balance',
                data: yData,
                borderColor: '#97CADB',
                backgroundColor: 'rgba(151, 202, 219, 0.2)',
                borderWidth: 2,
                fill: true,
                tension: 0.1,
                spanGaps: true,
                segment: {
                    borderColor: ctx => '#97CADB'
                },
                pointStyle: 'circle',
                pointRadius: 3,
                pointHoverRadius: 6,
                pointBackgroundColor: '#97CADB',
                pointBorderColor: '#fff',
                pointBorderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Balance: $${context.parsed.y.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toFixed(2);
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            elements: {
                line: {
                    tension: 0.1,
                    borderJoinStyle: 'round',
                    borderCapStyle: 'round'
                }
            }
        }
    });

    return chart;
}

export function createBalanceLineChart(id) {
    eel.get_account_transactions(100, 0)(function(transactions) {
        if (!transactions || transactions.length === 0) {
            // Handle empty data case
            const canvas = document.getElementById(id);
            if (canvas) {
                const ctx = canvas.getContext('2d');
                ctx.font = '14px Arial';
                ctx.fillStyle = '#666';
                ctx.textAlign = 'center';
                ctx.fillText('No transaction data available', canvas.width / 2, canvas.height / 2);
            }
            return;
        }

        try {
            // Ensure all dates are valid and sort transactions
            transactions = transactions
                .filter(transaction => {
                    try {
                        const date = new Date(transaction[3]);
                        return !isNaN(date.getTime());
                    } catch (e) {
                        console.error('Invalid date:', transaction[3]);
                        return false;
                    }
                })
                .sort((a, b) => new Date(a[3]) - new Date(b[3]));
            
            // Group transactions by date and calculate final balance for each day
            const dailyBalances = new Map();
            let runningBalance = 0;
            
            transactions.forEach(transaction => {
                try {
                    const amount = parseFloat(transaction[2]) || 0;
                    const date = new Date(transaction[3]);
                    const type = transaction[1];
                    
                    // Apply transaction
                    if (type === 'Deposit') {
                        runningBalance += amount;
                    } else {
                        runningBalance -= amount;
                    }
                    
                    // Format date without time component
                    const formattedDate = date.toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric'
                    });
                    
                    // Store the latest balance for this date
                    dailyBalances.set(formattedDate, runningBalance);
                } catch (e) {
                    console.error('Error processing transaction:', e);
                }
            });
            
            // Convert map to arrays for Chart.js
            const dates = [...dailyBalances.keys()];
            const balances = [...dailyBalances.values()];
            
            if (dates.length === 0 || balances.length === 0) {
                throw new Error('No valid data points after processing');
            }

            createLineChart(id, dates, balances);
        } catch (e) {
            console.error('Error creating balance line chart:', e);
            // Handle error case
            const canvas = document.getElementById(id);
            if (canvas) {
                const ctx = canvas.getContext('2d');
                ctx.font = '14px Arial';
                ctx.fillStyle = '#666';
                ctx.textAlign = 'center';
                ctx.fillText('Error loading balance history', canvas.width / 2, canvas.height / 2);
            }
        }
    });
}
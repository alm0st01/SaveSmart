export function budgetingTransactionsTable(category) {
    const wrapper = document.createElement('div');
    wrapper.classList.add('table-responsive');
    wrapper.style.cssText = `
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        overflow-x: hidden;
    `;

    const table = document.createElement('table');
    table.classList.add('table', 'table-striped', 'table-bordered', 'table-hover');
    table.style.cssText = `
        width: 100%;
        table-layout: fixed;
    `;

    const thead = document.createElement('thead');
    thead.classList.add('thead-dark', 'sticky-top');
    const headerRow = document.createElement('tr');
    const headers = ['ID', 'Type', 'Amount', 'Date', 'Description'];
    const columnWidths = ['17.5%', '17.5%', '17.5%', '17.5%', '30%'];
    
    headers.forEach((headerText, index) => {
        const th = document.createElement('th');
        th.textContent = headerText;
        th.scope = 'col';
        th.style.cssText = `
            width: ${columnWidths[index]};
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        `;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement('tbody');
    
    eel.get_account_transactions_by_category(category)(function(transactions) {
        console.log("Received transactions for category:", category, transactions);
        
        if (!transactions || transactions.length === 0) {
            const row = document.createElement('tr');
            const td = document.createElement('td');
            td.colSpan = 5; // Updated to match new column count
            td.textContent = 'No transactions found for this category';
            td.style.textAlign = 'center';
            row.appendChild(td);
            tbody.appendChild(row);
        } else {
            transactions.forEach((transaction, i) => {
                const row = document.createElement('tr');
                transaction.forEach((value, j) => {
                    const td = document.createElement('td');
                    td.style.cssText = `
                        white-space: nowrap;
                        overflow: hidden;
                        text-overflow: ellipsis;
                    `;
                    // Format based on column
                    switch(j) {
                        case 2: // Amount
                            td.textContent = value ? `$${parseFloat(value).toFixed(2)}` : '$0.00';
                            td.title = value ? `$${parseFloat(value).toFixed(2)}` : '$0.00';
                            break;
                        case 3: // Date
                            const date = new Date(value);
                            date.setMinutes(date.getMinutes() + date.getTimezoneOffset());
                            td.textContent = value ? date.toLocaleDateString() : '------';
                            td.title = value ? date.toLocaleDateString() : '------';
                            break;
                        default:
                            td.textContent = value || '------';
                            td.title = value || '------';
                    }
                    td.dataset.row = i;
                    td.dataset.col = j;
                    row.appendChild(td);
                });
                tbody.appendChild(row);
            });
        }
        
        table.appendChild(tbody);
        const container = document.getElementById('table-container');
        if (container) {
            container.innerHTML = '';
            container.appendChild(wrapper);
            container.innerHTML += '<br><br>Hover over a value in the table in order to see its complete value. ';
        } else {
            console.error("Could not find table-container element");
        }
    });

    table.appendChild(tbody);
    wrapper.appendChild(table);
    return wrapper;
}

window.budgetingTransactionsTable = budgetingTransactionsTable;

export function transactionsTable(rowsPerPage) { //for temporary development, rowsPerPage is not needed
    const wrapper = document.createElement('div');
    wrapper.classList.add('table-responsive');
    wrapper.style.cssText = `
        max-height: 400px;
        overflow-y: auto;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    `;

    const table = document.createElement('table');
    table.classList.add('table', 'table-striped', 'table-bordered', 'table-hover');

    const thead = document.createElement('thead');
    thead.classList.add('thead-dark', 'sticky-top');
    const headerRow = document.createElement('tr');
    const headers = ['ID', 'Type', 'Amount', 'Date', 'Purchase Type', 'Description'];
    headers.forEach(headerText => {
        const th = document.createElement('th');
        th.textContent = headerText;
        th.scope = 'col';
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement('tbody');
    
    eel.get_account_transactions(100, 0)(function(transactions) {
        console.log("Received transactions:", transactions); // Debug log
        
        if (!transactions || transactions.length === 0) {
            const row = document.createElement('tr');
            const td = document.createElement('td');
            td.colSpan = 6;
            td.textContent = 'No transactions found';
            td.style.textAlign = 'center';
            row.appendChild(td);
            tbody.appendChild(row);
            return;
        }

        transactions.forEach((transaction, i) => {
            const row = document.createElement('tr');
            transaction.forEach((value, j) => {
                const td = document.createElement('td');
                // Format based on column
                switch(j) {
                    case 2: // Amount
                        td.textContent = value ? `$${parseFloat(value).toFixed(2)}` : '$0.00';
                        break;
                    case 3: // Date
                        const transDate = new Date(value);
                        transDate.setMinutes(transDate.getMinutes() + transDate.getTimezoneOffset());
                        td.textContent = value ? transDate.toLocaleDateString() : '------';
                        break;
                    default:
                        td.textContent = value || '------';
                }
                td.dataset.row = i;
                td.dataset.col = j;
                row.appendChild(td);
            });
            tbody.appendChild(row);
        });
    });

    table.appendChild(tbody);
    wrapper.appendChild(table);
    return wrapper;
}

window.transactionsTable = transactionsTable;
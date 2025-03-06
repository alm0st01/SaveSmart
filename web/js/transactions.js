export function budgetingTransactionsTable(category) {
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
    
    eel.get_account_transactions_by_category(category)(function(transactions) {
        transactions.forEach((transaction, i) => {
            const row = document.createElement('tr');
            transaction.forEach((value, j) => {
                const td = document.createElement('td');
                if ((typeof value === 'number') && (j == 2)) {
                    td.textContent = `$${value.toFixed(2)}`;
                } else {
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
        transactions.forEach((transaction, i) => {
            const row = document.createElement('tr');
            transaction.forEach((value, j) => {
                const td = document.createElement('td');
                if ((typeof value === 'number') && (j == 2)) {
                    td.textContent = `$${value.toFixed(2)}`;
                } else {
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
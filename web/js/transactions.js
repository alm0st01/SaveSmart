document.addEventListener('DOMContentLoaded', function () {
    function transactionsTable(rows) {
        const table = document.createElement('table');
        table.classList.add('table', 'table-striped', 'table-bordered', 'table-hover');

        const thead = document.createElement('thead');
        thead.classList.add('thead-dark');
        const headerRow = document.createElement('tr');
        const headers = ['ID', 'Type', 'Amount', 'Date', 'Balance After', 'Description'];
        headers.forEach(headerText => {
            const th = document.createElement('th');
            th.textContent = headerText;
            th.scope = 'col';
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        var filledRows = 0;
        eel.get_account_transactions(rows)(function(transactions) {
            filledRows = transactions.length;
        });

        const tbody = document.createElement('tbody');

        eel.get_account_transactions(rows)(function(transactions) {

            transactions.forEach((transaction, i) => {
                const row = document.createElement('tr');
                transaction.forEach((value, j) => {
                    const td = document.createElement('td');
                    td.textContent = value || '------';
                    td.dataset.row = i;
                    td.dataset.col = j;
                    row.appendChild(td);
                });
                tbody.appendChild(row);
            });


            const emptyRows = rows - transactions.length;
            for (let i = 1; i <= emptyRows; i++) {
                const row = document.createElement('tr');
                for (let j = 0; j < headers.length; j++) {
                    const td = document.createElement('td');
                    td.textContent = '------';
                    td.dataset.row = transactions.length + i;
                    td.dataset.col = j;
                    row.appendChild(td);
                }
                tbody.appendChild(row);
            }
        });

        table.appendChild(tbody);

        const wrapper = document.createElement('div');
        wrapper.classList.add('table-responsive');
        wrapper.appendChild(table);

        return wrapper;
    }
    window.transactionsTable = transactionsTable;
});
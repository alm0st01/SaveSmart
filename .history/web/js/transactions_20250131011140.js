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
        })
        thead.appendChild(headerRow);
        table.appendChild(thead);

        const tbody = document.createElement('tbody');
        for (let i = 0; i < rows; i++){
            const row = document.createElement('tr');
            headers.forEach(() => {
                const td = document.createElement('td');
                td.textContent = 'a'; // Replace with info
                row.appendChild(td);
            });
            tbody.appendChild(row);
        }
        table.appendChild(tbody);

        const wrapper = document.createElement('div');
        wrapper.classList.add('table-responsive');
        wrapper.appendChild(table);

        return wrapper;
    }
    window.transactionsTable = transactionsTable;
});
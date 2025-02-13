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

        // Create a 2D array to store cell data
        const tableData = Array(rows).fill().map(() => Array(headers.length).fill('----'));

        const tbody = document.createElement('tbody');
        for (let i = 0; i < rows; i++) {
            const row = document.createElement('tr');
            for (let j = 0; j < headers.length; j++) {
                const td = document.createElement('td');
                td.textContent = tableData[i][j];
                // Add data attributes to identify cell position
                td.dataset.row = i;
                td.dataset.col = j;
                row.appendChild(td);
            }
            tbody.appendChild(row);
        }
        table.appendChild(tbody);

        // Function to update cell content
        table.updateCell = function(row, col, value) {
            tableData[row][col] = value;
            const cell = tbody.querySelector(`td[data-row="${row}"][data-col="${col}"]`);
            if (cell) {
                cell.textContent = value;
            }
            return Boolean(cell);
        };

        const wrapper = document.createElement('div');
        wrapper.classList.add('table-responsive');
        wrapper.appendChild(table);

        return wrapper;
    }
    window.transactionsTable = transactionsTable;
});
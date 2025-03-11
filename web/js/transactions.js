function calculateCurrentBalance(transactions) {
    return transactions.reduce((balance, transaction) => {
        const amount = parseFloat(transaction[2]);
        const type = transaction[1];
        if (type === 'Deposit') {
            return balance + amount;
        } else {
            return balance - amount;
        }
    }, 0);
}

export function budgetingTransactionsTable(category, mode) {
    console.log(`Creating budgeting table for category: ${category}, mode: ${mode}`);
    
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
    
    console.log('Fetching transactions from server...');
    eel.get_account_transactions_by_category(category, mode)(function(transactions) {
        console.log("Received transactions:", transactions);
        
        if (!transactions || transactions.length === 0) {
            console.log('No transactions found for category:', category);
            const row = document.createElement('tr');
            const td = document.createElement('td');
            td.colSpan = 5;
            td.textContent = 'No transactions found for this category';
            td.style.textAlign = 'center';
            row.appendChild(td);
            tbody.appendChild(row);
        } else {
            console.log(`Processing ${transactions.length} transactions`);
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

        var container;
        if (mode == 1) {
            container = document.getElementById('table-container-1');
        }
        else if (mode == 2) {
            container = document.getElementById('table-container-2');
        }
        
        if (container) {
            console.log('Updating container with new table');
            container.innerHTML = '';
            container.appendChild(wrapper);
            container.innerHTML += '<br><br>Hover over a value in the table in order to see its complete value. ';
        } else {
            console.error("Could not find table container element");
        }
    });

    table.appendChild(tbody);
    wrapper.appendChild(table);
    return wrapper;
}

window.budgetingTransactionsTable = budgetingTransactionsTable;

export function transactionsTable(rowsPerPage) {
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
    thead.classList.add('sticky-top');
    thead.style.cssText = `
        background-color: #97CADB;
        color: white;
    `;
    
    const headerRow = document.createElement('tr');
    const headers = ['ID', 'Type', 'Amount', 'Date', 'Purchase Type', 'Description', 'Actions'];
    headers.forEach(headerText => {
        const th = document.createElement('th');
        th.textContent = headerText;
        th.scope = 'col';
        if (headerText === 'Actions') {
            th.style.width = '150px';
        }
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement('tbody');
    
    eel.get_account_transactions(100, 0)(function(transactions) {
        console.log("Received transactions:", transactions);
        
        if (!transactions || transactions.length === 0) {
            const row = document.createElement('tr');
            const td = document.createElement('td');
            td.colSpan = 7;
            td.textContent = 'No transactions found';
            td.style.textAlign = 'center';
            row.appendChild(td);
            tbody.appendChild(row);
            
            // Update current balance to 0 if no transactions
            const currentBalance = document.getElementById('current-balance');
            if (currentBalance) {
                currentBalance.textContent = '$0.00';
            }
            return;
        }

        // Calculate current balance from all transactions
        const balance = calculateCurrentBalance(transactions);
        const currentBalance = document.getElementById('current-balance');
        if (currentBalance) {
            currentBalance.textContent = `$${balance.toFixed(2)}`;
        }

        // Sort transactions by date in descending order (newest first)
        transactions.sort((a, b) => new Date(b[3]) - new Date(a[3]));

        transactions.forEach((transaction, i) => {
            const row = document.createElement('tr');
            
            // Add transaction data cells
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

            // Add action buttons cell
            const actionsTd = document.createElement('td');
            actionsTd.style.cssText = `
                display: flex;
                gap: 0.5rem;
                justify-content: center;
            `;

            // Edit button
            const editBtn = document.createElement('button');
            editBtn.className = 'btn btn-sm btn-primary';
            editBtn.textContent = 'Edit';
            editBtn.onclick = () => {
                const transactionId = transaction[0];
                window.location.href = `account/banking/edit_transaction.html?id=${transactionId}`;
            };

            // Delete button
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'btn btn-sm btn-danger';
            deleteBtn.textContent = 'Delete';
            deleteBtn.onclick = () => deleteTransaction(transaction[0]);

            actionsTd.appendChild(editBtn);
            actionsTd.appendChild(deleteBtn);
            row.appendChild(actionsTd);

            tbody.appendChild(row);
        });
    });

    table.appendChild(tbody);
    wrapper.appendChild(table);
    return wrapper;
}

export async function deleteTransaction(transactionId) {
    try {
        const confirmed = confirm("Are you sure you want to delete this transaction?");
        if (!confirmed) return;

        const success = await eel.delete_transaction(transactionId)();
        if (success) {
            // Refresh the table
            const tableContainer = document.getElementById('table-container');
            if (tableContainer) {
                tableContainer.innerHTML = '';
                tableContainer.appendChild(transactionsTable(5));
            }
        } else {
            alert("Failed to delete transaction. Please try again.");
        }
    } catch (error) {
        console.error("Error deleting transaction:", error);
        alert("An error occurred while deleting the transaction.");
    }
}

function showSearchDialog() {
    $('#searchModal').modal('show');
    $('#searchInput').focus();
}

function showNotification(message) {
    $('#notificationMessage').text(message);
    $('#notificationModal').modal('show');
}

function performSearch() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const tbody = document.querySelector('#table-container table tbody');
    let found = false;

    if (!tbody) return;

    if (searchTerm.trim() === '') {
        resetFilters();
        $('#searchModal').modal('hide');
        return;
    }

    // Remove any existing "no results" message
    const noResultsRow = tbody.querySelector('td[colspan="7"]')?.parentElement;
    if (noResultsRow) {
        tbody.removeChild(noResultsRow);
    }

    // Remove previous highlights
    document.querySelectorAll('.search-highlight').forEach(el => {
        el.classList.remove('search-highlight');
    });

    tbody.querySelectorAll('tr').forEach(row => {
        let rowMatch = false;
        
        // Search in all columns except the Actions column
        for (let i = 0; i < 6; i++) {
            const cell = row.cells[i];
            if (cell) {
                // Remove existing highlights
                cell.querySelectorAll('.search-highlight').forEach(el => {
                    el.replaceWith(document.createTextNode(el.textContent));
                });
                
                const cellText = cell.textContent.toLowerCase();
                if (cellText.includes(searchTerm)) {
                    rowMatch = true;
                    found = true;
                    // Highlight matching text
                    const regex = new RegExp(`(${searchTerm})`, 'gi');
                    cell.innerHTML = cell.textContent.replace(regex, '<span class="search-highlight">$1</span>');
                }
            }
        }

        row.style.display = rowMatch ? '' : 'none';
    });

    if (!found) {
        const noResultsRow = document.createElement('tr');
        noResultsRow.innerHTML = `
            <td colspan="7" style="text-align: center;">
                No transactions found matching "${searchTerm}"
            </td>
        `;
        tbody.insertBefore(noResultsRow, tbody.firstChild);
    }

    $('#searchModal').modal('hide');
}

function resetFilters() {
    const tableContainer = document.getElementById('table-container');
    if (tableContainer) {
        // Clear the container
        tableContainer.innerHTML = '';
        // Create and append a new table
        const table = transactionsTable(5);
        tableContainer.appendChild(table);
    }
}

// Make functions available globally
window.transactionsTable = transactionsTable;
window.deleteTransaction = deleteTransaction;
window.budgetingTransactionsTable = budgetingTransactionsTable;
window.showSearchDialog = showSearchDialog;
window.performSearch = performSearch;
window.resetFilters = resetFilters;
window.showNotification = showNotification;

function exportTransactionsToCSV() {
    eel.get_account_transactions(100, 0)(function(transactions) {
        if (!transactions || transactions.length === 0) {
            showNotification('No transactions to export');
            return;
        }

        // Get current balance
        const currentBalance = document.getElementById('current-balance').textContent;
        const monthlyGains = document.getElementById('avg-monthly-gains').textContent;
        const monthlyLosses = document.getElementById('avg-monthly-losses').textContent;
        const monthlyNet = document.getElementById('avg-monthly-net').textContent;

        // Create CSV content
        let csvContent = 'Transaction Report\n\n';
        csvContent += `Current Balance,${currentBalance}\n`;
        csvContent += `Average Monthly Gains,${monthlyGains}\n`;
        csvContent += `Average Monthly Losses,${monthlyLosses}\n`;
        csvContent += `Average Monthly Net,${monthlyNet}\n\n`;
        
        // Add headers
        csvContent += 'ID,Type,Amount,Date,Purchase Type,Description\n';

        // Sort transactions by date (newest first)
        transactions.sort((a, b) => new Date(b[3]) - new Date(a[3]));

        // Add transaction data
        transactions.forEach(transaction => {
            const formattedTransaction = transaction.map((value, index) => {
                if (index === 2) { // Amount
                    return `$${parseFloat(value).toFixed(2)}`;
                } else if (index === 3) { // Date
                    const date = new Date(value);
                    date.setMinutes(date.getMinutes() + date.getTimezoneOffset());
                    return date.toLocaleDateString();
                }
                return value || '';
            });
            csvContent += formattedTransaction.join(',') + '\n';
        });

        // Create and trigger download
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `transaction_report_${new Date().toLocaleDateString()}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });
}

window.exportTransactionsToCSV = exportTransactionsToCSV;

async function exportTransactionsToPDF() {
    try {
        const pdfData = await eel.generate_pdf_data()();
        // Create a Blob from the PDF data
        const blob = new Blob([new Uint8Array(pdfData)], { type: 'application/pdf' });
        
        // Create a download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `transactions_${new Date().toISOString().split('T')[0]}.pdf`;
        
        // Trigger download
        document.body.appendChild(a);
        a.click();
        
        // Cleanup
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        console.error('Error generating PDF:', error);
        showNotification('Error generating PDF. Please try again.');
    }
}

window.exportTransactionsToPDF = exportTransactionsToPDF;
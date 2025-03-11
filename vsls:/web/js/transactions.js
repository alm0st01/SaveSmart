// ...existing code...
export function showSearchDialog() {
    $('#searchDialog').modal('show');
    $('#searchInput').focus();
}

export function searchTransactions() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const tbody = document.querySelector('#table-container table tbody');
    let found = false;

    // Remove previous highlights
    document.querySelectorAll('.search-highlight').forEach(el => {
        el.classList.remove('search-highlight');
    });

    if (tbody) {
        tbody.querySelectorAll('tr').forEach(row => {
            let rowMatch = false;
            // Search in description and purchase type columns (indices 4 and 5)
            const searchColumns = [4, 5];
            
            searchColumns.forEach(colIndex => {
                const cell = row.cells[colIndex];
                if (cell && cell.textContent.toLowerCase().includes(searchTerm)) {
                    rowMatch = true;
                    found = true;
                    // Highlight the matching text
                    cell.classList.add('search-highlight');
                }
            });

            // Show/hide rows based on match
            row.style.display = rowMatch || searchTerm === '' ? '' : 'none';
        });
    }

    if (!found && searchTerm !== '') {
        alert('No matching transactions found.');
    }

    $('#searchDialog').modal('hide');
}

// Make search functions available globally
window.showSearchDialog = showSearchDialog;
window.searchTransactions = searchTransactions;

// ...existing code...

function performSearch() {
    const searchInput = document.querySelector('.search-input');
    const searchTerm = searchInput.value.toLowerCase();
    
    // Search in table contents
    const tableBody = document.querySelector('tbody');
    if (tableBody) {
        const rows = tableBody.getElementsByTagName('tr');
        
        for (let row of rows) {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Replace the form with a search container
    const searchForm = document.querySelector('form[role="search"]');
    if (searchForm) {
        const searchContainer = document.createElement('div');
        searchContainer.className = 'search-container';
        
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.className = 'search-input';
        searchInput.placeholder = 'Search...';
        
        const searchButton = document.createElement('button');
        searchButton.className = 'search-button';
        searchButton.innerHTML = '<i class="fas fa-search"></i>';
        searchButton.onclick = performSearch;
        
        searchContainer.appendChild(searchInput);
        searchContainer.appendChild(searchButton);
        
        // Add event listener for Enter key
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                performSearch();
            }
        });
        
        searchForm.parentNode.replaceChild(searchContainer, searchForm);
    }
});

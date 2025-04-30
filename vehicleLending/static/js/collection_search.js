// This script handles the search functionality for the site
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById("collectionSearchInput");
    const searchResults = document.getElementById("collectionSearchResults");
    const searchForm = document.getElementById("collectionSearchForm");

    const collectionName = document.querySelector('[data-collection-name]').getAttribute('data-collection-name');
    console.log('Collection Name:', collectionName);
    
    if (!searchInput || !searchResults || !searchForm) {
        console.error("Search elements not found:", { searchInput, searchResults, searchForm });
        return;
    }
    
    // Prevent normal form submission
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        console.log("Form submission prevented");
        return false;
    });
    
    // Handle search when typing
    let debounceTimer;
    searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(function() {
            const query = searchInput.value.trim();
            if (query.length > 0) {
                doSearch(query);
            } else {
                searchResults.classList.remove("show");
            }
        }, 300); // Debounce for 300ms
    });
    
    // Handle Enter key
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const query = searchInput.value.trim();
            if (query.length > 0) {
                doSearch(query);
            }
            return false;
        }
    });
    
    // Search button click
    const searchButton = document.getElementById("searchButton");
    if (searchButton) {
        searchButton.addEventListener('click', function() {
            const query = searchInput.value.trim();
            if (query.length > 0) {
                doSearch(query);
            }
        });
    }
    
    // Function to perform search
    function doSearch(query) {
        console.log("Performing search for:", query);
        
        // Show loading indicator
        searchResults.innerHTML = "<li class='dropdown-item'><i class='fas fa-spinner fa-spin me-2'></i>Searching...</li>";
        searchResults.classList.add("show");
        
        // Perform the AJAX search
        fetch(`/collection_search/?q=${encodeURIComponent(query)}&collection=${encodeURIComponent(collectionName)}`)
            .then(response => {
                console.log("Search response status:", response.status);
                return response.json();
            })
            .then(data => {
                console.log("Search results:", data);
                
                searchResults.innerHTML = "";
                const results = data.results || [];
                
                if (results.length > 0) {
                    results.forEach(result => {
                        const li = document.createElement('li');
                        const a = document.createElement('a');
                        a.href = new URL(result.url, window.location.origin).href;
                        a.className = 'dropdown-item';
                        a.textContent = result.text;
                        li.appendChild(a);
                        searchResults.appendChild(li);
                    });
                } else {
                    searchResults.innerHTML = "<li class='dropdown-item text-muted'>No results found</li>";
                }
                
                searchResults.classList.add("show");
            })
            .catch(error => {
                console.error("Search error:", error);
                searchResults.innerHTML = "<li class='dropdown-item text-danger'>Error searching</li>";
                searchResults.classList.add("show");
            });
    }
    
    // Hide results when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.classList.remove("show");
        }
    });
});

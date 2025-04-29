document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById("searchInput");
    const searchResults = document.getElementById("searchResults");
    const searchForm = document.getElementById("searchForm");

    if (!searchInput || !searchResults || !searchForm) {
        console.error("Search elements not found:", { searchInput, searchResults, searchForm });
        return;
    }

    // Function to perform search
    function doSearch(query) {
        console.log("Performing search for:", query);
        
        // *** Add more detailed logging here ***
        const encodedQuery = encodeURIComponent(query);
        const fetchUrl = `/search/?q=${encodedQuery}`;
        console.log("Preparing to fetch URL:", fetchUrl);
        console.log(`Query: '${query}', Encoded: '${encodedQuery}'`);
        // *** End of added logging ***

        // Show loading indicator
        searchResults.innerHTML = "<li class='dropdown-item'><i class='fas fa-spinner fa-spin me-2'></i>Searching...</li>";
        searchResults.classList.add("show");
        searchResults.style.display = "block";
        
        // Perform the AJAX search
        fetch(fetchUrl)
            .then(response => {
                console.log("Search response status:", response.status);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Search results received:", data);
                
                searchResults.innerHTML = "";
                const results = data.results || [];
                
                if (results.length > 0) {
                    results.forEach(result => {
                        const li = document.createElement('li');
                        const a = document.createElement('a');
                        // Make sure URL starts with / if it's a relative path
                        let url = result.url;
                        if (url && !url.startsWith('/') && !url.startsWith('http') && !url.startsWith('javascript:')) {
                            url = '/' + url;
                        }
                        a.href = url.startsWith('javascript:') ? result.url : new URL(url, window.location.origin).href;
                        a.className = 'dropdown-item';
                        a.textContent = result.text;
                        li.appendChild(a);
                        searchResults.appendChild(li);
                    });
                } else {
                    // Display 'No results found' if backend returns empty results or specific message
                    const noResultText = (data.results && data.results.length === 1 && data.results[0].url === "javascript:void(0)") 
                                         ? data.results[0].text 
                                         : "No results found";
                    searchResults.innerHTML = `<li class='dropdown-item text-muted'>${noResultText}</li>`;
                }
                
                searchResults.classList.add("show");
                searchResults.style.display = "block";
            })
            .catch(error => {
                console.error("Search error:", error);
                searchResults.innerHTML = "<li class='dropdown-item text-danger'>Error searching. Please try again.</li>";
                searchResults.classList.add("show");
                searchResults.style.display = "block";
            });
    }

    // Prevent normal form submission
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        console.log("Form submission prevented");
        const query = searchInput.value.trim();
        if (query.length > 0) {
            doSearch(query); // Also trigger search on explicit submit
        }
        return false;
    });
    
    // Handle search when typing with debounce
    let debounceTimer;
    searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            const query = searchInput.value.trim();
            if (query.length > 0) {
                doSearch(query);
            } else {
                searchResults.classList.remove("show");
                searchResults.style.display = "none";
            }
        }, 300); // Debounce for 300ms
    });
    
    // Handle Enter key more robustly (might be redundant with form submit)
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            clearTimeout(debounceTimer); // Prevent debounced search if Enter is pressed
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
             clearTimeout(debounceTimer); // Prevent debounced search on click
            const query = searchInput.value.trim();
            if (query.length > 0) {
                doSearch(query);
            }
        });
    }
    
    // Hide results when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.classList.remove("show");
            searchResults.style.display = "none";
        }
    });
});
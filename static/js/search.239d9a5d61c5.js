document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById("searchInput");
    if (!searchInput) return;
    
    // Prevent the form from submitting and redirecting
    const searchForm = searchInput.closest('form');
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
    });
    
    searchInput.addEventListener("input", function() {
        let query = this.value.trim();
        let resultsContainer = document.getElementById("searchResults");
        console.log("Search query:", query);

        // Clear previous results and hide dropdown if input is empty
        if (query.length > 0) {
            fetch(`/search/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    console.log("Search results:", data);

                    resultsContainer.innerHTML = ""; // Clear previous results

                    let results = data.results;

                    if (results.length > 0) {
                        results.forEach(item => {
                            let resultItem = document.createElement("li");
                            let link = document.createElement("a");
                            link.href = new URL(item.url, window.location.origin).href;
                            link.className = "dropdown-item";
                            link.textContent = item.text;
                            resultItem.appendChild(link);
                            resultsContainer.appendChild(resultItem);
                        });

                        // Show the dropdown
                        resultsContainer.classList.add("show");
                    } else {
                        resultsContainer.innerHTML = "<li class='dropdown-item text-muted'>No results found</li>";
                        resultsContainer.classList.add("show");
                    }
                })
                .catch(error => console.error("Error fetching search results:", error));
        } else {
            resultsContainer.classList.remove("show"); // Hide dropdown when empty
        }
    });

    // Hide dropdown when clicking outside
    document.addEventListener("click", function(event) {
        let searchBox = document.getElementById("searchInput");
        let resultsContainer = document.getElementById("searchResults");
        if (searchBox && resultsContainer && !searchBox.contains(event.target) && !resultsContainer.contains(event.target)) {
            resultsContainer.classList.remove("show");
        }
    });
});
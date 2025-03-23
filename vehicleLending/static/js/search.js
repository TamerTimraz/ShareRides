document.getElementById("searchInput").addEventListener("input", function() {
    let query = this.value.trim();
    let resultsContainer = document.getElementById("searchResults");
    console.log("Search query:", query);

    // Clear previous results and hide dropdown if input is empty
    if (query.length > 0) {
        fetch(`/search/?query=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                console.log("Search results:", data);

                resultsContainer.innerHTML = ""; // Clear previous results

                let results = data.results;

                if (results.length > 0) {
                    results.forEach(item => {
                        let resultItem = document.createElement("li");
                        let link = document.createElement("a");
                        link.href = "#"; // Adjust to a real link if needed
                        link.className = "dropdown-item";
                        link.textContent = item;
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
    if (!searchBox.contains(event.target) && !resultsContainer.contains(event.target)) {
        resultsContainer.classList.remove("show");
    }
});
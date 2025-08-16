// Fetch API version from the backend when the page loads
document.addEventListener('DOMContentLoaded', async () => {
    let apiVersion = '1.0.0'; // Default version if not fetched

    try {
        const response = await fetch('/api');
        const data = await response.json();

        if (data && data.info && data.info.version) {
            // Update the API version display
            apiVersion = data.info.version;
            document.getElementById('api-version').textContent = apiVersion;

            // Try to get real search data first
            try {
                const defaultQuery = document.getElementById('custom-query').value || 'ubuntu';
                await fetchRealSearchData(defaultQuery);
            } catch (searchError) {
                console.error('Error fetching search data:', searchError);
                // Hide loading spinner if search fails
                hideResponseLoading();
            }
        }
    } catch (error) {
        console.error('Error fetching API version:', error);
        // Hide loading spinner even if there's an error
        hideResponseLoading();
    }

    // Initialize dark mode from system preference or local storage
    initializeTheme();

    // Add animation effects
    animateElements();

    // Setup theme toggle
    setupThemeToggle();

    // Setup refresh button
    setupRefreshButton();

    // Setup custom query functionality
    setupCustomQuerySearch();

    // Setup copy button
    setupCopyButton();
});

// Setup custom query search functionality
function setupCustomQuerySearch() {
    const queryInput = document.getElementById('custom-query');
    const runQueryButton = document.getElementById('run-query');

    if (queryInput && runQueryButton) {
        // Run query when button is clicked
        runQueryButton.addEventListener('click', () => {
            executeCustomQuery(queryInput.value);
        });

        // Also run query when Enter key is pressed in the input field
        queryInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') {
                executeCustomQuery(queryInput.value);
            }
        });
    }
}

// Execute the custom query search
async function executeCustomQuery(query) {
    if (!query || query.trim() === '') {
        // Alert user if query is empty
        alert('Please enter a search query');
        return;
    }

    const sanitizedQuery = query.trim();

    // Show loading spinner
    const loadingElement = document.getElementById('response-loading');
    if (loadingElement) {
        loadingElement.style.display = 'flex';
    }

    // Update the example code with the new query
    updateExampleCode(sanitizedQuery);

    try {
        // Try to fetch data with the custom query
        await fetchRealSearchData(sanitizedQuery);
    } catch (error) {
        console.error('Error executing custom query:', error);
        hideResponseLoading();
    }
}

// Update the example code with the new query
function updateExampleCode(query) {
    const codeElement = document.getElementById('example-code');
    if (codeElement) {
        codeElement.textContent = `curl -X GET "https://tbd-api.tanmoy.xyz/search?query=${encodeURIComponent(query)}" -H "accept: application/json"`;
    }
}

// Setup refresh button functionality
function setupRefreshButton() {
    const refreshButton = document.getElementById('refresh-data');
    if (refreshButton) {
        refreshButton.addEventListener('click', async () => {
            // Get current query from input
            const queryInput = document.getElementById('custom-query');
            const currentQuery = queryInput ? queryInput.value.trim() : 'ubuntu';

            // Show loading spinner
            const loadingElement = document.getElementById('response-loading');
            if (loadingElement) {
                loadingElement.style.display = 'flex';
            }

            // Add spinning animation to refresh icon
            refreshButton.classList.add('animate-spin');

            try {
                // Try to fetch fresh data with current query
                await fetchRealSearchData(currentQuery);
            } catch (error) {
                console.error('Error refreshing data:', error);
                hideResponseLoading();
            } finally {
                // Remove spinning animation
                refreshButton.classList.remove('animate-spin');
            }
        });
    }
}

// Try to fetch real search data from the API
async function fetchRealSearchData(query = 'ubuntu') {
    try {
        // Attempt to fetch real search data with the provided query
        const searchResponse = await fetch(`/search?query=${encodeURIComponent(query)}`);
        const searchData = await searchResponse.json();

        if (searchData && searchData.result) {
            // Display exactly what the API returns without modifications
            const formattedJson = JSON.stringify(searchData, null, 2);
            document.getElementById('example-response').textContent = formattedJson;
            hideResponseLoading();
            return true;
        } else {
            throw new Error('Invalid search response format');
        }
    } catch (error) {
        throw error;
    }
}

// Hide the loading spinner
function hideResponseLoading() {
    const loadingElement = document.getElementById('response-loading');
    if (loadingElement) {
        loadingElement.style.display = 'none';
    }
}

// Setup copy button event listener
function setupCopyButton() {
    const copyBtn = document.querySelector('.copy-btn');
    if (copyBtn) {
        copyBtn.addEventListener('click', copyToClipboard);
    }
}

// Copy example code to clipboard
function copyToClipboard() {
    const codeElement = document.getElementById('example-code');
    if (!codeElement) {
        console.error('Code element not found');
        return;
    }

    const textToCopy = codeElement.textContent;

    // Log for debugging
    console.log('Copying text:', textToCopy);

    navigator.clipboard.writeText(textToCopy)
        .then(() => {
            const copyBtn = document.querySelector('.copy-btn');
            const originalIcon = copyBtn.innerHTML;

            // Change icon to indicate successful copy
            copyBtn.innerHTML = '<i class="fas fa-check"></i>';

            // Restore original icon after 2 seconds
            setTimeout(() => {
                copyBtn.innerHTML = originalIcon;
            }, 2000);
        })
        .catch(err => {
            console.error('Error copying text: ', err);
            // Provide fallback for browsers that don't support clipboard API
            fallbackCopyTextToClipboard(textToCopy);
        });
}

// Fallback copy method for older browsers
function fallbackCopyTextToClipboard(text) {
    try {
        // Create temporary textarea
        const textArea = document.createElement("textarea");
        textArea.value = text;

        // Make the textarea invisible
        textArea.style.position = 'fixed';
        textArea.style.top = 0;
        textArea.style.left = 0;
        textArea.style.width = '2em';
        textArea.style.height = '2em';
        textArea.style.padding = 0;
        textArea.style.border = 'none';
        textArea.style.outline = 'none';
        textArea.style.boxShadow = 'none';
        textArea.style.background = 'transparent';

        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();

        try {
            const successful = document.execCommand('copy');
            const copyBtn = document.querySelector('.copy-btn');
            if (successful) {
                copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                setTimeout(() => {
                    copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                }, 2000);
            }
        } catch (err) {
            console.error('Fallback: Error copying text', err);
        }

        document.body.removeChild(textArea);
    } catch (err) {
        console.error('Could not copy text: ', err);
    }
}

// Add animation effects to elements as they appear in viewport
function animateElements() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    // Observe all sections and endpoint cards
    document.querySelectorAll('section, .endpoint-card').forEach(el => {
        el.classList.add('animate-on-scroll');
        observer.observe(el);
    });
}

// Add event listeners for endpoint cards
document.querySelectorAll('.endpoint-card').forEach(card => {
    card.addEventListener('click', function(e) {
        // Only trigger if not clicking on the try button
        if (!e.target.closest('.try-button')) {
            const link = this.querySelector('.try-button a').getAttribute('href');
            window.location.href = link;
        }
    });
});

// Dark mode functionality
function initializeTheme() {
    // Check for saved theme preference or use system preference
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
        document.documentElement.classList.add('dark');
    } else {
        document.documentElement.classList.remove('dark');
    }
}

function setupThemeToggle() {
    const themeToggleBtn = document.getElementById('theme-toggle');
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            // Toggle dark mode
            if (document.documentElement.classList.contains('dark')) {
                document.documentElement.classList.remove('dark');
                localStorage.setItem('theme', 'light');
            } else {
                document.documentElement.classList.add('dark');
                localStorage.setItem('theme', 'dark');
            }
        });
    }
}

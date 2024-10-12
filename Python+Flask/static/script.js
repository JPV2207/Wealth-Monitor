const searchInput = document.getElementById('holding_list');
const suggestionsList = document.getElementById('suggestions');
let selectedSuggestionIndex = -1;

// Function to fetch stock suggestions from Python backend
async function fetchStockSuggestions(input) {
    try {
        const response = await fetch(`http://localhost:5000/autocomplete?query=${input}`);
        const data = await response.json();
        return data.suggestions;
    } catch (error) {
        console.error('Error fetching stock suggestions:', error);
        return [];
    }
}

// Function to display suggestions
function displaySuggestions(suggestions) {
    suggestionsList.innerHTML = '';
    suggestions.forEach((suggestion, index) => {
        const li = document.createElement('li');
        li.textContent = suggestion;
        li.dataset.index = index;
        li.classList.add('list-group-item'); // Add Bootstrap class
        suggestionsList.appendChild(li);
    });
    selectedSuggestionIndex = -1;
}

// Function to handle arrow key navigation for scrolling through suggestions
function handleArrowKeys(event) {
    const key = event.key;
    if (key === 'ArrowUp' && selectedSuggestionIndex > 0) {
        event.preventDefault();
        selectedSuggestionIndex--;
    } else if (key === 'ArrowDown' && selectedSuggestionIndex < suggestionsList.children.length - 1) {
        event.preventDefault();
        selectedSuggestionIndex++;
    }
    updateSelectedSuggestion();
}

// Function to update the selected suggestion and scroll it into view
function updateSelectedSuggestion() {
    for (let i = 0; i < suggestionsList.children.length; i++) {
        const suggestion = suggestionsList.children[i];
        if (i === selectedSuggestionIndex) {
            suggestion.classList.add('active'); // Add custom class for selected suggestion
            suggestion.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        } else {
            suggestion.classList.remove('active'); // Remove custom class from other suggestions
        }
    }
}

// Function to handle Enter key press
function handleEnterKey(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        if (selectedSuggestionIndex !== -1) {
            searchInput.value = suggestionsList.children[selectedSuggestionIndex].textContent;
        }
        suggestionsList.innerHTML = ''; // Clear suggestion list
    }
}

// Event listener for input changes
searchInput.addEventListener('input', async () => {
    const userInput = searchInput.value.trim();
    if (userInput.length < 2) {
        suggestionsList.innerHTML = '';
        return;
    }
    const suggestions = await fetchStockSuggestions(userInput);
    displaySuggestions(suggestions);
});

// Event listener for suggestion selection
suggestionsList.addEventListener('click', (event) => {
    if (event.target.tagName === 'LI') {
        searchInput.value = event.target.textContent;
        suggestionsList.innerHTML = '';
    }
});

// Event listener for arrow key events
window.addEventListener('keydown', handleArrowKeys);

// Event listener for Enter key press on input field
searchInput.addEventListener('keydown', handleEnterKey);

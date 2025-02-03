document.addEventListener('DOMContentLoaded', function() {
    console.log('Flag selector JS loaded');
    
    // Search functionality
    const searchInput = document.getElementById('flag-search');
    const flagOptions = document.querySelectorAll('.flag-option');
    
    console.log('Number of flag options found:', flagOptions.length);
    console.log('Search input found:', !!searchInput);

    searchInput?.addEventListener('input', function(e) {
        console.log('Search input value:', e.target.value);
        const searchText = e.target.value.toLowerCase();
        flagOptions.forEach(option => {
            const countryName = option.querySelector('span').textContent.toLowerCase();
            option.style.display = countryName.includes(searchText) ? 'flex' : 'none';
        });
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        const selector = document.getElementById('flag-selector');
        const flagDisplay = document.getElementById('flag-display');
        
        if (selector && !selector.contains(e.target) && e.target !== flagDisplay && !flagDisplay.contains(e.target)) {
            selector.classList.add('hidden');
        }
    });
});

function toggleFlagSelector() {
    console.log('Toggle flag selector called');
    const selector = document.getElementById('flag-selector');
    console.log('Selector found:', !!selector);
    selector.classList.toggle('hidden');
    console.log('Selector visibility:', !selector.classList.contains('hidden'));
}

function selectCountry(countryCode) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch('/accounts/update-country/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        },
        body: `country_code=${countryCode}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const flagDisplay = document.getElementById('flag-display');
            flagDisplay.innerHTML = `
                <img src="https://flagcdn.com/32x24/${countryCode}.png" 
                     alt="${countryCode}"
                     class="w-8 h-6">
            `;
            toggleFlagSelector();
        }
    })
    .catch(error => console.error('Error:', error));
}
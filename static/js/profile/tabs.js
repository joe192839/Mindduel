document.addEventListener('DOMContentLoaded', function() {
    const tabs = document.querySelectorAll('.stats-tab');
    const contents = document.querySelectorAll('.stats-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));
            // Add active class to clicked tab
            tab.classList.add('active');
            
            // Hide all content
            contents.forEach(content => content.classList.add('hidden'));
            // Show selected content
            document.getElementById(tab.dataset.tab + '-stats').classList.remove('hidden');
        });
    });
});
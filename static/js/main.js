// Main JavaScript file for AI Models Directory

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Search functionality
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 300));
    }

    // Filter functionality
    const filterSelects = document.querySelectorAll('.filter-select');
    filterSelects.forEach(select => {
        select.addEventListener('change', handleFilter);
    });
});

// Debounce function to limit API calls
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Handle search input
async function handleSearch(event) {
    const searchTerm = event.target.value.toLowerCase();
    const container = document.getElementById('models-container');
    
    if (!container) return;
    
    container.classList.add('loading');
    
    try {
        const response = await fetch(`/api/models?search=${encodeURIComponent(searchTerm)}`);
        const models = await response.json();
        updateModelsDisplay(models);
    } catch (error) {
        console.error('Error fetching models:', error);
        showError('An error occurred while searching. Please try again.');
    } finally {
        container.classList.remove('loading');
    }
}

// Handle filter changes
async function handleFilter(event) {
    const filters = {};
    document.querySelectorAll('.filter-select').forEach(select => {
        if (select.value) {
            filters[select.name] = select.value;
        }
    });
    
    const container = document.getElementById('models-container');
    if (!container) return;
    
    container.classList.add('loading');
    
    try {
        const queryString = Object.entries(filters)
            .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
            .join('&');
            
        const response = await fetch(`/api/models?${queryString}`);
        const models = await response.json();
        updateModelsDisplay(models);
    } catch (error) {
        console.error('Error applying filters:', error);
        showError('An error occurred while filtering. Please try again.');
    } finally {
        container.classList.remove('loading');
    }
}

// Update the display of models
function updateModelsDisplay(models) {
    const container = document.getElementById('models-container');
    if (!container) return;
    
    container.innerHTML = models.length ? 
        models.map(model => createModelCard(model)).join('') :
        '<div class="alert alert-info">No models found matching your criteria.</div>';
}

// Create HTML for a model card
function createModelCard(model) {
    return `
        <div class="col-md-4 mb-4">
            <div class="card h-100">
                <div class="card-body">
                    <h5 class="card-title">${escapeHtml(model.name)}</h5>
                    <span class="badge bg-primary">${escapeHtml(model.source)}</span>
                    ${model.category.map(cat => 
                        `<span class="badge bg-secondary">${escapeHtml(cat)}</span>`
                    ).join(' ')}
                    <p class="card-text mt-2">${escapeHtml(model.description)}</p>
                </div>
                <div class="card-footer">
                    <a href="/model/${encodeURIComponent(model.name.toLowerCase().replace(/\s+/g, '-'))}" 
                       class="btn btn-primary">View Details</a>
                </div>
            </div>
        </div>
    `;
}

// Show error message
function showError(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.innerHTML = `
        ${escapeHtml(message)}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('main.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
    }
}

// Escape HTML to prevent XSS
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Handle "Back to Top" button
window.onscroll = function() {
    const backToTopBtn = document.getElementById('back-to-top');
    if (backToTopBtn) {
        if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
            backToTopBtn.style.display = "block";
        } else {
            backToTopBtn.style.display = "none";
        }
    }
};

// DOM Elements
const uploadBox = document.getElementById('uploadBox');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const removeFileBtn = document.getElementById('removeFile');
const uploadForm = document.getElementById('uploadForm');
const sampleBtn = document.getElementById('sampleBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const loadingOverlay = document.getElementById('loadingOverlay');
const resultsSection = document.getElementById('results');

// File Upload Handlers
uploadBox.addEventListener('click', () => fileInput.click());

uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.classList.add('drag-over');
});

uploadBox.addEventListener('dragleave', () => {
    uploadBox.classList.remove('drag-over');
});

uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadBox.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0 && files[0].name.endsWith('.csv')) {
        fileInput.files = files;
        showFileInfo(files[0]);
    } else {
        alert('Please upload a CSV file');
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        showFileInfo(e.target.files[0]);
    }
});

removeFileBtn.addEventListener('click', () => {
    fileInput.value = '';
    fileInfo.style.display = 'none';
    uploadBox.style.display = 'block';
});

function showFileInfo(file) {
    fileName.textContent = file.name;
    uploadBox.style.display = 'none';
    fileInfo.style.display = 'flex';
}

// Form Submission
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    await analyzeData(new FormData(uploadForm));
});

sampleBtn.addEventListener('click', async () => {
    await analyzeData(new FormData()); // Empty form data triggers sample data
});

async function analyzeData(formData) {
    // Show loading
    loadingOverlay.style.display = 'flex';
    resultsSection.style.display = 'none';
    analyzeBtn.disabled = true;
    sampleBtn.disabled = true;
    
    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Analysis failed');
        }
        
        displayResults(data);
        
        // Scroll to results
        setTimeout(() => {
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }, 500);
        
    } catch (error) {
        alert('Error: ' + error.message);
        console.error(error);
    } finally {
        loadingOverlay.style.display = 'none';
        analyzeBtn.disabled = false;
        sampleBtn.disabled = false;
    }
}

function displayResults(data) {
    // Show results section
    resultsSection.style.display = 'block';
    
    // Display data summary
    displayDataSummary(data.data_summary);
    
    // Display metrics
    displayMetrics(data.metrics);
    
    // Display charts
    displayCharts(data.charts);
    
    // Display optimal prices
    displayOptimalPrices(data.optimal_prices);
    
    // Display coefficients
    displayCoefficients(data.coefficients);
}

function displayDataSummary(summary) {
    const container = document.getElementById('dataSummary');
    
    let categoryList = '';
    for (const [cat, count] of Object.entries(summary.categories)) {
        categoryList += `<li>${cat}: ${count}</li>`;
    }
    
    container.innerHTML = `
        <div class="summary-item">
            <div class="item-label">Total Observations</div>
            <div class="item-value">${summary.total_observations}</div>
        </div>
        <div class="summary-item">
            <div class="item-label">Unique Products</div>
            <div class="item-value">${summary.unique_products}</div>
        </div>
        <div class="summary-item">
            <div class="item-label">Price Range</div>
            <div class="item-value">$${summary.price_range[0]} - $${summary.price_range[1]}</div>
        </div>
        <div class="summary-item">
            <div class="item-label">Demand Range</div>
            <div class="item-value">${summary.demand_range[0]} - ${summary.demand_range[1]}</div>
            <div class="item-sublabel">units</div>
        </div>
        <div class="summary-item" style="grid-column: 1 / -1;">
            <div class="item-label">Categories Breakdown</div>
            <ul style="margin-top: 0.5rem; list-style-position: inside;">
                ${categoryList}
            </ul>
        </div>
    `;
}

function displayMetrics(metrics) {
    const container = document.getElementById('metricsGrid');
    
    const r2Status = metrics.test_r2 > 0.7 ? '✅ Excellent' : metrics.test_r2 > 0.5 ? '⚠️ Good' : '❌ Needs Improvement';
    
    container.innerHTML = `
        <div class="metric-item">
            <div class="item-label">R² Score (Test)</div>
            <div class="item-value">${metrics.test_r2}</div>
            <div class="item-sublabel">${r2Status}</div>
        </div>
        <div class="metric-item">
            <div class="item-label">R² Score (Train)</div>
            <div class="item-value">${metrics.train_r2}</div>
        </div>
        <div class="metric-item">
            <div class="item-label">RMSE</div>
            <div class="item-value">${metrics.rmse.toFixed(2)}</div>
            <div class="item-sublabel">units</div>
        </div>
        <div class="metric-item">
            <div class="item-label">MAE</div>
            <div class="item-value">${metrics.mae.toFixed(2)}</div>
            <div class="item-sublabel">units</div>
        </div>
    `;
}

function displayCharts(charts) {
    document.getElementById('scatterChart').src = 'data:image/png;base64,' + charts.scatter;
    document.getElementById('validationChart').src = 'data:image/png;base64,' + charts.validation;
    document.getElementById('curvesChart').src = 'data:image/png;base64,' + charts.curves;
}

function displayOptimalPrices(optimal) {
    const container = document.getElementById('optimalPrices');
    
    let html = '';
    for (const [category, data] of Object.entries(optimal)) {
        const emoji = {
            'Smartphone': '📱',
            'Tablet': '📲',
            'Smartwatch': '⌚',
            'Earbuds': '🎧'
        }[category] || '📦';
        
        html += `
            <div class="optimal-item">
                <div class="item-label">${emoji} ${category}</div>
                <div class="item-value">$${data.price}</div>
                <div class="item-sublabel">Expected Demand: ${data.demand} units</div>
                <div class="item-sublabel">Expected Revenue: $${data.revenue.toLocaleString()}</div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

function displayCoefficients(coefficients) {
    const container = document.getElementById('coefficients');
    
    let html = '';
    for (const [name, value] of Object.entries(coefficients)) {
        const interpretation = name === 'Price' 
            ? `Every $1 price increase → ${value.toFixed(2)} units change in demand`
            : name === 'Intercept'
            ? 'Base demand level'
            : `Baseline demand adjustment for ${name}`;
        
        html += `
            <div class="coef-item">
                <div class="item-label">${name}</div>
                <div class="item-value">${value.toFixed(4)}</div>
                <div class="item-sublabel">${interpretation}</div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

// Smooth Scroll for Navigation
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add animation on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe cards
document.querySelectorAll('.card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(card);
});

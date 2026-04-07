const uploadBox = document.getElementById("uploadBox");
const fileInput = document.getElementById("fileInput");
const fileInfo = document.getElementById("fileInfo");
const fileName = document.getElementById("fileName");
const removeFileBtn = document.getElementById("removeFile");
const uploadForm = document.getElementById("uploadForm");
const sampleBtn = document.getElementById("sampleBtn");
const sampleBtnHero = document.getElementById("sampleBtnHero");
const analyzeBtn = document.getElementById("analyzeBtn");
const loadingOverlay = document.getElementById("loadingOverlay");
const resultsSection = document.getElementById("results");

uploadBox.addEventListener("click", () => fileInput.click());

uploadBox.addEventListener("dragover", (event) => {
    event.preventDefault();
    uploadBox.classList.add("drag-over");
});

uploadBox.addEventListener("dragleave", () => {
    uploadBox.classList.remove("drag-over");
});

uploadBox.addEventListener("drop", (event) => {
    event.preventDefault();
    uploadBox.classList.remove("drag-over");

    const files = event.dataTransfer.files;
    if (files.length > 0 && files[0].name.toLowerCase().endsWith(".csv")) {
        fileInput.files = files;
        showFileInfo(files[0]);
    } else {
        window.alert("Please upload a CSV file.");
    }
});

fileInput.addEventListener("change", (event) => {
    if (event.target.files.length > 0) {
        showFileInfo(event.target.files[0]);
    }
});

removeFileBtn.addEventListener("click", () => {
    fileInput.value = "";
    fileInfo.style.display = "none";
    uploadBox.style.display = "flex";
});

uploadForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    await analyzeData(new FormData(uploadForm));
});

sampleBtn.addEventListener("click", async () => {
    await analyzeData(new FormData());
});

sampleBtnHero.addEventListener("click", async () => {
    await analyzeData(new FormData());
});

function showFileInfo(file) {
    fileName.textContent = file.name;
    uploadBox.style.display = "none";
    fileInfo.style.display = "flex";
}

async function analyzeData(formData) {
    setLoadingState(true);

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            body: formData,
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || "Analysis failed");
        }

        displayResults(data);

        setTimeout(() => {
            resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
        }, 250);
    } catch (error) {
        console.error(error);
        window.alert(`Error: ${error.message}`);
    } finally {
        setLoadingState(false);
    }
}

function setLoadingState(isLoading) {
    loadingOverlay.style.display = isLoading ? "flex" : "none";
    resultsSection.style.display = isLoading ? "none" : resultsSection.style.display;
    analyzeBtn.disabled = isLoading;
    sampleBtn.disabled = isLoading;
    sampleBtnHero.disabled = isLoading;
}

function displayResults(data) {
    resultsSection.style.display = "block";

    displayReportHeader(data.meta);
    displayHighlights(data.highlights);
    displayInsights(data.insights);
    displayDataSummary(data.data_summary, data.meta);
    displayCharts(data.charts);
    displayPlaybook(data.product_profiles, data.optimal_prices);
    displayMetrics(data.metrics);
    displayCoefficients(data.coefficients);
    showResultBlocks();
    revealVisibleBlocks();
}

function displayReportHeader(meta) {
    const reportSubtitle = document.getElementById("reportSubtitle");
    const reportMeta = document.getElementById("reportMeta");

    reportSubtitle.textContent =
        `${meta.records_analyzed} records from ${meta.dataset_name} analyzed with ${meta.model_name}. ` +
        `Baseline product: ${meta.baseline_product}.`;

    const metaItems = [
        ["Dataset", meta.dataset_name],
        ["Source", meta.data_source],
        ["Model", meta.model_name],
        ["Baseline", meta.baseline_product],
        ["Base Category", meta.baseline_category],
    ];

    reportMeta.innerHTML = metaItems
        .map(
            ([label, value]) => `
                <div class="meta-card">
                    <span>${label}</span>
                    <strong>${value}</strong>
                </div>
            `
        )
        .join("");
}

function displayHighlights(highlights) {
    const container = document.getElementById("highlightGrid");
    const cards = [
        {
            label: "Market Revenue",
            value: formatCurrency(highlights.current_market_revenue),
            body: "Observed revenue implied by the uploaded dataset.",
        },
        {
            label: "Average Price",
            value: formatCurrency(highlights.average_price),
            body: "Mean product price across all analyzed rows.",
        },
        {
            label: "Average Demand",
            value: `${numberFormat(highlights.average_units)} units`,
            body: "Average unit volume observed across the dataset.",
        },
        {
            label: "Best Revenue Product",
            value: highlights.best_revenue_product,
            body: "Product with the strongest modeled revenue peak.",
        },
        {
            label: "Most Sensitive Product",
            value: highlights.most_sensitive_product,
            body: "Product that reacts most strongly to price changes.",
        },
    ];

    container.innerHTML = cards
        .map(
            (card) => `
                <article class="highlight-card">
                    <span>${card.label}</span>
                    <strong>${card.value}</strong>
                    <p>${card.body}</p>
                </article>
            `
        )
        .join("");
}

function displayInsights(insights) {
    const container = document.getElementById("insightList");
    container.innerHTML = insights.map((item) => `<li>${item}</li>`).join("");
}

function displayDataSummary(summary, meta) {
    const container = document.getElementById("dataSummary");
    const categoryBreakdown = Object.entries(summary.categories)
        .map(([category, count]) => `${category}: ${count}`)
        .join(" | ");

    const items = [
        ["Observations", numberFormat(summary.total_observations)],
        ["Unique Products", numberFormat(summary.unique_products)],
        ["Price Range", `${formatCurrency(summary.price_range[0])} to ${formatCurrency(summary.price_range[1])}`],
        ["Demand Range", `${numberFormat(summary.demand_range[0])} to ${numberFormat(summary.demand_range[1])}`],
        ["Category Mix", categoryBreakdown],
        ["Source Type", meta.data_source],
    ];

    container.innerHTML = items
        .map(
            ([label, value]) => `
                <div class="summary-stat">
                    <span>${label}</span>
                    <strong>${value}</strong>
                </div>
            `
        )
        .join("");
}

function displayCharts(charts) {
    document.getElementById("scatterChart").src = `data:image/png;base64,${charts.scatter}`;
    document.getElementById("curvesChart").src = `data:image/png;base64,${charts.curves}`;
    document.getElementById("revenueChart").src = `data:image/png;base64,${charts.revenue}`;
}

function displayPlaybook(profiles, optimalPrices) {
    const container = document.getElementById("productPlaybook");
    const groupedProfiles = {};

    Object.entries(profiles).forEach(([product, profile]) => {
        if (!groupedProfiles[profile.category]) {
            groupedProfiles[profile.category] = [];
        }

        groupedProfiles[profile.category].push([product, profile]);
    });

    if (Object.keys(groupedProfiles).length === 0) {
        container.innerHTML = `
            <section class="playbook-group">
                <div class="playbook-group-header">
                    <span class="card-topline">No Playbook Data</span>
                    <h4>No product recommendations were generated</h4>
                </div>
            </section>
        `;
        return;
    }

    container.innerHTML = Object.keys(groupedProfiles)
        .sort()
        .map((category) => {
            const cards = groupedProfiles[category]
                .sort((a, b) => b[1].optimal_revenue - a[1].optimal_revenue)
                .map(([product, profile]) => {
                    const optimal = optimalPrices[product];
                    return `
                        <article class="profile-card">
                            <div class="profile-top">
                                <div>
                                    <span>${category}</span>
                                    <strong>${product}</strong>
                                    <p>Recommended zone at ${formatCurrency(optimal.price)} with ${profile.sensitivity_band.toLowerCase()} behavior.</p>
                                </div>
                                <div class="profile-band">${profile.sensitivity_band}</div>
                            </div>

                            <div class="profile-metrics">
                                <div>
                                    <span>Optimal Price</span>
                                    <strong>${formatCurrency(optimal.price)}</strong>
                                </div>
                                <div>
                                    <span>Optimal Revenue</span>
                                    <strong>${formatCurrency(optimal.revenue)}</strong>
                                </div>
                                <div>
                                    <span>Expected Demand</span>
                                    <strong>${numberFormat(optimal.demand)} units</strong>
                                </div>
                                <div>
                                    <span>Observed Window</span>
                                    <strong>${formatCurrency(profile.observed_min)} to ${formatCurrency(profile.observed_max)}</strong>
                                </div>
                                <div>
                                    <span>Revenue Uplift</span>
                                    <strong>${formatCurrency(profile.revenue_uplift)}</strong>
                                </div>
                                <div>
                                    <span>Elasticity</span>
                                    <strong>${profile.elasticity}</strong>
                                </div>
                                <div>
                                    <span>Price Points</span>
                                    <strong>${profile.unique_prices}</strong>
                                </div>
                            </div>
                        </article>
                    `;
                })
                .join("");

            return `
                <section class="playbook-group">
                    <div class="playbook-group-header">
                        <span class="card-topline">${category}</span>
                        <h4>${groupedProfiles[category].length} product recommendations</h4>
                    </div>
                    <div class="profile-grid">${cards}</div>
                </section>
            `;
        })
        .join("");
}

function displayMetrics(metrics) {
    const container = document.getElementById("metricsGrid");
    const cards = [
        {
            label: "Test R2",
            value: metrics.test_r2,
            body: describeR2(metrics.test_r2),
        },
        {
            label: "Train R2",
            value: metrics.train_r2,
            body: "Training fit for the in-sample split.",
        },
        {
            label: "RMSE",
            value: `${metrics.rmse.toFixed(2)} units`,
            body: "Typical prediction error magnitude.",
        },
        {
            label: "MAE",
            value: `${metrics.mae.toFixed(2)} units`,
            body: "Average absolute error across holdout rows.",
        },
    ];

    container.innerHTML = cards
        .map(
            (card) => `
                <article class="metric-card">
                    <span>${card.label}</span>
                    <strong>${card.value}</strong>
                    <p>${card.body}</p>
                </article>
            `
        )
        .join("");
}

function displayCoefficients(coefficients) {
    const container = document.getElementById("coefficients");

    container.innerHTML = Object.entries(coefficients)
        .map(([name, value]) => {
            const displayValue =
                typeof value === "number" ? value.toFixed(4) : value;

            return `
                <article class="coef-card">
                    <span>${normalizeCoefficientName(name)}</span>
                    <strong>${displayValue}</strong>
                    <p>${describeCoefficient(name, value)}</p>
                </article>
            `;
        })
        .join("");
}

function normalizeCoefficientName(name) {
    return name
        .replaceAll("_x_", " x ")
        .replaceAll("_", " ")
        .replace("Product ", "")
        .trim();
}

function describeCoefficient(name, value) {
    if (name === "Intercept") {
        return "Base expected demand level before product adjustments are applied.";
    }

    if (name === "Price") {
        return "Core price slope applied to the baseline product.";
    }

    if (name === "Baseline Product") {
        return "This product acts as the reference segment for the model.";
    }

    if (name.startsWith("Product_")) {
        return "Intercept adjustment for this product relative to the baseline product.";
    }

    if (name.startsWith("Category_")) {
        return "Baseline demand adjustment for this category relative to the baseline category.";
    }

    if (name.startsWith("Price_x_Category_")) {
        return "Category-specific change to the shared price slope.";
    }

    if (name.startsWith("Price_x_")) {
        return "Extra product-specific price slope layered on top of the baseline price effect.";
    }

    return typeof value === "number"
        ? "Model coefficient used during prediction."
        : "Model metadata.";
}

function describeR2(value) {
    if (value >= 0.8) {
        return "Very strong holdout fit for exploratory pricing work.";
    }
    if (value >= 0.6) {
        return "Healthy directional fit for pricing experiments.";
    }
    if (value >= 0.4) {
        return "Useful signal, but recommendations should be treated cautiously.";
    }
    return "Weak fit. More data or feature engineering would help.";
}

function formatCurrency(value) {
    return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        maximumFractionDigits: 2,
    }).format(value);
}

function numberFormat(value) {
    return new Intl.NumberFormat("en-US").format(value);
}

const revealObserver = new IntersectionObserver(
    (entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add("is-visible");
            }
        });
    },
    {
        threshold: 0.15,
        rootMargin: "0px 0px -60px 0px",
    }
);

function revealVisibleBlocks() {
    document.querySelectorAll("[data-reveal]").forEach((element) => {
        revealObserver.observe(element);
    });
}

function showResultBlocks() {
    resultsSection.querySelectorAll("[data-reveal]").forEach((element) => {
        element.classList.add("is-visible");
    });
}

revealVisibleBlocks();

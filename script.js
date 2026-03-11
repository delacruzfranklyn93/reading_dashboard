// script.js Outline

const CSV_URL = 'final_scoreboard.csv';

// State to hold parsed data
let readingData = [];

document.addEventListener('DOMContentLoaded', () => {
    fetchData();
});

async function fetchData() {
    try {
        const response = await fetch(CSV_URL);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const csvText = await response.text();
        
        // Parse CSV using PapaParse
        Papa.parse(csvText, {
            header: true,
            skipEmptyLines: true,
            complete: function(results) {
                console.log("Parsed CSV Data:", results.data);
                readingData = results.data;
                processData();
            }
        });
    } catch (error) {
        console.error("Could not fetch the CSV data:", error);
    }
}

function processData() {
    let globalPages = 0;
    let globalBooks = 0;

    const stats = {
        'Savannah': { pages: 0, books: 0, recentBook: '', dates: [] },
        'Franklyn': { pages: 0, books: 0, recentBook: '', dates: [] }
    };

    // Sort data chronologically to get the most recent book correctly, and build time series
    readingData.sort((a, b) => new Date(a['Date Read']) - new Date(b['Date Read']));

    // Activity feed (we want it reverse chronological)
    const reversedData = [...readingData].reverse();
    populateActivityFeed(reversedData);

    readingData.forEach(row => {
        const reader = row['Reader'];
        const pages = parseInt(row['Adjusted Pages'], 10) || 0;
        const bookTitle = row['Book Title'];
        const dateRead = row['Date Read'];

        if (reader && stats[reader]) {
            stats[reader].pages += pages;
            stats[reader].books += 1;
            stats[reader].recentBook = bookTitle;
            
            // For Timeline
            stats[reader].dates.push({
                date: dateRead,
                pages: pages,
                cumulative: stats[reader].pages
            });

            globalPages += pages;
            globalBooks += 1;
        }
    });

    // Update DOM
    document.getElementById('global-pages').innerText = globalPages.toLocaleString();
    document.getElementById('global-books').innerText = globalBooks.toLocaleString();

    Object.keys(stats).forEach(reader => {
        const lowerReader = reader.toLowerCase();
        
        // Count animations for a premium feel
        animateValue(`${lowerReader}-pages`, 0, stats[reader].pages, 1500);
        animateValue(`${lowerReader}-books`, 0, stats[reader].books, 1500);
        
        document.getElementById(`${lowerReader}-recent`).innerText = stats[reader].recentBook || 'No books yet';
    });

    // Show crown for winner
    if (stats['Savannah'].pages > stats['Franklyn'].pages) {
        document.getElementById('crown-savannah').style.display = 'block';
    } else if (stats['Franklyn'].pages > stats['Savannah'].pages) {
        document.getElementById('crown-franklyn').style.display = 'block';
    }

    renderChart(stats);
}

function animateValue(id, start, end, duration) {
    if (start === end) return;
    const obj = document.getElementById(id);
    if (!obj) return;
    
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        
        // Easing function (easeOutExpo)
        const easeProgress = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
        
        obj.innerHTML = Math.floor(easeProgress * (end - start) + start).toLocaleString();
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

function populateActivityFeed(data) {
    const list = document.getElementById('activity-list');
    list.innerHTML = ''; // Clear default

    // Show up to 10 recent items
    const recentItems = data.slice(0, 10);
    
    recentItems.forEach(item => {
        if (!item.Reader) return; // skip empty lines

        const readerClass = item.Reader.toLowerCase();
        const icon = readerClass === 'savannah' ? 'fa-book-open-reader' : 'fa-book-journal-whills';
        const pages = item['Adjusted Pages'];
        
        // Format date nice
        const dateObj = new Date(item['Date Read']);
        const dateStr = dateObj.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });

        const li = document.createElement('li');
        li.className = 'feed-item';
        li.innerHTML = `
            <div class="feed-item-icon ${readerClass}">
                <i class="fa-solid ${icon}"></i>
            </div>
            <div class="feed-item-content">
                <h4>${item['Book Title']}</h4>
                <p>${item.Reader} &bull; ${dateStr}</p>
            </div>
            <div class="feed-item-pages ${readerClass}">
                +${pages}
            </div>
        `;
        list.appendChild(li);
    });
}

function renderChart(stats) {
    const ctx = document.getElementById('timelineChart').getContext('2d');
    
    // Extract unique dates for X-axis
    const allDatesSet = new Set();
    stats['Savannah'].dates.forEach(d => allDatesSet.add(d.date));
    stats['Franklyn'].dates.forEach(d => allDatesSet.add(d.date));
    
    // Sort all dates
    const allDates = Array.from(allDatesSet).sort((a, b) => new Date(a) - new Date(b));

    // Helper to build step-data for the graph
    function getCumulativeData(readerDates) {
        let lastVal = 0;
        return allDates.map(date => {
            const found = readerDates.filter(d => d.date === date);
            if (found.length > 0) {
                // If multiple books per day, take the last one's cumulative
                lastVal = found[found.length - 1].cumulative;
            }
            return lastVal;
        });
    }

    const savannahData = getCumulativeData(stats['Savannah'].dates);
    const franklynData = getCumulativeData(stats['Franklyn'].dates);

    // Format dates for labels
    const labels = allDates.map(d => {
        const date = new Date(d);
        return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    });

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Savannah',
                    data: savannahData,
                    borderColor: '#f472b6',
                    backgroundColor: 'rgba(244, 114, 182, 0.1)',
                    borderWidth: 3,
                    pointBackgroundColor: '#f472b6',
                    tension: 0.3, // smooth curves
                    fill: true
                },
                {
                    label: 'Franklyn',
                    data: franklynData,
                    borderColor: '#60a5fa',
                    backgroundColor: 'rgba(96, 165, 250, 0.1)',
                    borderWidth: 3,
                    pointBackgroundColor: '#60a5fa',
                    tension: 0.3,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    labels: { color: '#f8f9fa', font: { family: "'Outfit', sans-serif" } }
                },
                tooltip: {
                    backgroundColor: 'rgba(0,0,0,0.8)',
                    titleFont: { family: "'Outfit', sans-serif" },
                    bodyFont: { family: "'Outfit', sans-serif" },
                    padding: 10,
                    cornerRadius: 8,
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#9ca3af', font: { family: "'Outfit', sans-serif" } }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#9ca3af', font: { family: "'Outfit', sans-serif" } },
                    beginAtZero: true
                }
            }
        }
    });
}

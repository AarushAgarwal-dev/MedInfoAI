// --- Navigation: Smooth Scroll ---
document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', function(e) {
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// --- Medicine Search Logic ---
const form = document.getElementById('search-form');
const input = document.getElementById('medicine-input');
const resultsContainer = document.getElementById('results-container');
const loader = document.getElementById('loader');

if (form) {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const userQuery = input.value.trim();
        if (!userQuery) return;
        resultsContainer.innerHTML = '';
        loader.style.display = 'block';
        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ medicine_name: userQuery })
            });
            const data = await response.json();
            if (!response.ok || data.error) {
                throw new Error(data.error || 'An unknown error occurred.');
            }
            displayResults(data, userQuery);
        } catch (error) {
            displayError(error.message);
        } finally {
            loader.style.display = 'none';
        }
    });
}

function displayResults(data, userQuery) {
    let resultsHtml = `<div class="results-card">`;
    resultsHtml += `<div class="results-header">`;
    if (data.image_url) {
        resultsHtml += `<img src="${data.image_url}" alt="Image of ${data.identified_medicine}">`;
    }
    resultsHtml += `<div class="title-block">
            <h2>${data.identified_medicine || userQuery}</h2>
            <div class="info-line">
                <span class="label">Generic Name:</span>
                <span class="value">${data.generic_name || "N/A"}</span>
            </div>
            <div class="info-line">
                <span class="label">Composition:</span>
                <span class="value">${data.composition || "Not specified"}</span>
            </div>
        </div>
    </div>`;
    resultsHtml += `
        <div class="tabs">
            <button class="tab-button active" data-tab="tab-generic-info">About</button>
            <button class="tab-button" data-tab="tab-alternatives">Alternatives</button>
            <button class="tab-button" data-tab="tab-uses">Uses</button>
            <button class="tab-button" data-tab="tab-side-effects">Side Effects</button>
            <button class="tab-button" data-tab="tab-warnings">Warnings</button>
        </div>
    `;
    const createList = (items) => (items && items.length > 0) ? `<ul>${items.filter(i => i).map(item => `<li>${item}</li>`).join('')}</ul>` : '<p>No specific information was found in the search results.</p>';
    resultsHtml += `<div id="tab-generic-info" class="tab-content active">${data.generic_info_paragraph ? `<p class="generic-info-paragraph">${data.generic_info_paragraph}</p>` : createList([])}</div>`;
    resultsHtml += `<div id="tab-uses" class="tab-content">${createList(data.summary?.uses)}</div>`;
    resultsHtml += `<div id="tab-side-effects" class="tab-content">${createList(data.summary?.side_effects)}</div>`;
    resultsHtml += `<div id="tab-warnings" class="tab-content">${createList(data.summary?.warnings)}</div>`;
    resultsHtml += `<div id="tab-alternatives" class="tab-content">`;
    if (data.alternatives && data.alternatives.length > 0) {
        const originalDrugName = (data.identified_medicine || userQuery).toLowerCase();
        const filteredAlternatives = data.alternatives.filter(alt => alt && alt.brand_name && alt.brand_name.toLowerCase() !== originalDrugName);
        if (filteredAlternatives.length > 0) {
            resultsHtml += `<div class="alternatives-grid">`;
            filteredAlternatives.forEach(alt => {
                resultsHtml += `
                    <div class="alternative-card">
                        <h4>${alt.brand_name}</h4>
                        <p class="manufacturer">by ${alt.manufacturer}</p>
                    </div>`;
            });
            resultsHtml += `</div>`;
        } else {
             resultsHtml += `<p>No other brand alternatives were found.</p>`;
        }
    } else {
        resultsHtml += `<p>No brand alternatives were found.</p>`;
    }
    resultsHtml += `</div>`;
    resultsHtml += `</div>`;
    resultsContainer.innerHTML = resultsHtml;
    addTabListeners();
}

function addTabListeners() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            button.classList.add('active');
            document.getElementById(button.dataset.tab).classList.add('active');
        });
    });
}

function displayError(message) {
    resultsContainer.innerHTML = `<div class="error-card"><p>${message}</p></div>`;
}

// --- Kendra Finder Map with Real Locations ---
window.addEventListener('DOMContentLoaded', () => {
    const mapDiv = document.getElementById('kendra-map');
    const kendraListDiv = document.getElementById('kendra-list');
    if (mapDiv && window.L) {
        const kendras = [
            {
                name: 'Jan Aushadhi Kendra - Connaught Place',
                address: 'Shop No. 5, Palika Bazar, Connaught Place',
                city: 'Delhi',
                lat: 28.6315,
                lng: 77.2167
            },
            {
                name: 'Jan Aushadhi Kendra - Andheri',
                address: 'Shop 12, Andheri West, Near Station',
                city: 'Mumbai',
                lat: 19.1197,
                lng: 72.8468
            },
            {
                name: 'Jan Aushadhi Kendra - Jayanagar',
                address: 'No. 44, 4th Block, Jayanagar',
                city: 'Bangalore',
                lat: 12.9250,
                lng: 77.5938
            },
            {
                name: 'Jan Aushadhi Kendra - Salt Lake',
                address: 'CF-123, Sector 1, Salt Lake',
                city: 'Kolkata',
                lat: 22.5867,
                lng: 88.4172
            },
            {
                name: 'Jan Aushadhi Kendra - T Nagar',
                address: 'Shop 8, North Usman Road, T Nagar',
                city: 'Chennai',
                lat: 13.0446,
                lng: 80.2337
            }
        ];
        const map = L.map('kendra-map').setView([22.9734, 78.6569], 5.2); // Center of India
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
        kendras.forEach(kendra => {
            const marker = L.marker([kendra.lat, kendra.lng]).addTo(map);
            marker.bindPopup(`<b>${kendra.name}</b><br>${kendra.address}<br>${kendra.city}`);
        });
        // List below the map
        if (kendraListDiv) {
            kendraListDiv.innerHTML = kendras.map(k => `
                <div class="kendra-card">
                    <h4>${k.name}</h4>
                    <div class="kendra-address">${k.address}</div>
                    <div class="kendra-city">${k.city}</div>
                </div>
            `).join('');
        }
    }
});

// --- AI Assistant Chat UI ---
function createAIChatUI() {
    const container = document.getElementById('ai-chat-container');
    if (!container) return;
    container.innerHTML = `
        <div class="ai-chat-window" id="ai-chat-window"></div>
        <form id="ai-chat-form" class="ai-chat-form">
            <input type="text" id="ai-chat-input" placeholder="Type your question..." autocomplete="off" required />
            <button type="submit">Send</button>
        </form>
    `;
    const chatWindow = document.getElementById('ai-chat-window');
    const chatForm = document.getElementById('ai-chat-form');
    const chatInput = document.getElementById('ai-chat-input');
    let isLoading = false;

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const userMsg = chatInput.value.trim();
        if (!userMsg || isLoading) return;
        appendMessage('user', userMsg);
        chatInput.value = '';
        chatInput.disabled = true;
        isLoading = true;
        appendMessage('ai', '<span class="ai-loading">...</span>');
        chatWindow.scrollTop = chatWindow.scrollHeight;
        try {
            const res = await fetch('/ai-assistant', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMsg })
            });
            const data = await res.json();
            const aiReply = data.reply || 'Sorry, I could not process your request.';
            replaceLastAIMessage(aiReply);
        } catch (err) {
            replaceLastAIMessage('Sorry, there was an error contacting the AI.');
        } finally {
            chatInput.disabled = false;
            chatInput.focus();
            isLoading = false;
            chatWindow.scrollTop = chatWindow.scrollHeight;
        }
    });

    function appendMessage(sender, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'ai-chat-msg ' + (sender === 'user' ? 'user-msg' : 'ai-msg');
        msgDiv.innerHTML = text;
        chatWindow.appendChild(msgDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
    function replaceLastAIMessage(text) {
        const msgs = chatWindow.querySelectorAll('.ai-msg');
        if (msgs.length > 0) {
            msgs[msgs.length - 1].innerHTML = text;
        }
    }
}
window.addEventListener('DOMContentLoaded', createAIChatUI);

// --- Price Comparison Feature ---
function createPriceComparisonUI() {
    const container = document.getElementById('price-comparison-container');
    if (!container) return;
    container.innerHTML = `
        <form id="price-compare-form" class="price-compare-form">
            <input type="text" id="price-compare-input" placeholder="Enter medicine name..." required />
            <button type="submit">Compare</button>
        </form>
        <div id="price-compare-loader" class="loader" style="display:none;"></div>
        <div id="price-compare-results"></div>
    `;
    const form = document.getElementById('price-compare-form');
    const input = document.getElementById('price-compare-input');
    const loader = document.getElementById('price-compare-loader');
    const resultsDiv = document.getElementById('price-compare-results');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const medName = input.value.trim();
        if (!medName) return;
        resultsDiv.innerHTML = '';
        loader.style.display = 'block';
        try {
            // TODO: Replace with real backend call
            // const res = await fetch('/compare-prices', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ medicine_name: medName }) });
            // const data = await res.json();
            await new Promise(r => setTimeout(r, 900));
            const data = {
                prices: [
                    { source: '1mg', price: '₹25', url: '#' },
                    { source: 'Netmeds', price: '₹24', url: '#' },
                    { source: 'Apollo', price: '₹26', url: '#' },
                    { source: 'PharmEasy', price: '₹23', url: '#' }
                ]
            };
            if (!data.prices || data.prices.length === 0) {
                resultsDiv.innerHTML = '<div class="error-card">No prices found for this medicine.</div>';
            } else {
                resultsDiv.innerHTML = `
                    <table class="price-table">
                        <thead><tr><th>Source</th><th>Price</th><th>Link</th></tr></thead>
                        <tbody>
                            ${data.prices.map(p => `<tr><td>${p.source}</td><td>${p.price}</td><td><a href="${p.url}" target="_blank">Visit</a></td></tr>`).join('')}
                        </tbody>
                    </table>
                `;
            }
        } catch (err) {
            resultsDiv.innerHTML = '<div class="error-card">Error fetching price data.</div>';
        } finally {
            loader.style.display = 'none';
        }
    });
}
window.addEventListener('DOMContentLoaded', createPriceComparisonUI);

// --- Save for Future Purchase Feature ---
function createSaveForFutureUI() {
    const container = document.getElementById('save-future-container');
    if (!container) return;
    container.innerHTML = `
        <form id="save-future-form" class="save-future-form">
            <input type="text" id="save-future-input" placeholder="Enter medicine name..." required />
            <button type="submit">Save</button>
        </form>
        <div id="save-future-list"></div>
    `;
    const form = document.getElementById('save-future-form');
    const input = document.getElementById('save-future-input');
    const listDiv = document.getElementById('save-future-list');

    function getSaved() {
        return JSON.parse(localStorage.getItem('saved_medicines') || '[]');
    }
    function setSaved(arr) {
        localStorage.setItem('saved_medicines', JSON.stringify(arr));
    }
    function renderList() {
        const saved = getSaved();
        if (!saved.length) {
            listDiv.innerHTML = '<div class="info-card">No medicines saved for future purchase.</div>';
            return;
        }
        listDiv.innerHTML = `
            <ul class="save-future-list">
                ${saved.map((med, i) => `
                    <li>
                        <span>${med}</span>
                        <button class="remove-btn" data-idx="${i}" title="Remove">&times;</button>
                    </li>
                `).join('')}
            </ul>
        `;
        listDiv.querySelectorAll('.remove-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const idx = parseInt(this.getAttribute('data-idx'));
                const arr = getSaved();
                arr.splice(idx, 1);
                setSaved(arr);
                renderList();
            });
        });
    }
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const med = input.value.trim();
        if (!med) return;
        const arr = getSaved();
        if (!arr.includes(med)) {
            arr.push(med);
            setSaved(arr);
            renderList();
        }
        input.value = '';
    });
    renderList();
}
window.addEventListener('DOMContentLoaded', createSaveForFutureUI);

// --- Daily Essentials Feature ---
function createEssentialsUI() {
    const container = document.getElementById('essentials-container');
    if (!container) return;
    const essentials = [
        {
            name: 'Paracetamol 500mg',
            category: 'Pain Relief',
            img: 'https://cdn.1mg.com/images/medicine-img/paracetamol.jpg',
            desc: 'Common pain and fever reducer, safe for most ages.'
        },
        {
            name: 'ORS Sachet',
            category: 'Hydration',
            img: 'https://cdn.1mg.com/images/medicine-img/ors.jpg',
            desc: 'Oral rehydration salts for dehydration and diarrhea.'
        },
        {
            name: 'Digital Thermometer',
            category: 'Health Devices',
            img: 'https://cdn.1mg.com/images/medicine-img/thermometer.jpg',
            desc: 'Accurate temperature measurement for all ages.'
        },
        {
            name: 'Hand Sanitizer',
            category: 'Hygiene',
            img: 'https://cdn.1mg.com/images/medicine-img/sanitizer.jpg',
            desc: 'Kills 99.9% of germs, essential for hand hygiene.'
        },
        {
            name: 'Bandages',
            category: 'First Aid',
            img: 'https://cdn.1mg.com/images/medicine-img/bandage.jpg',
            desc: 'For minor cuts, scrapes, and wound protection.'
        },
        {
            name: 'Vitamin C Tablets',
            category: 'Supplements',
            img: 'https://cdn.1mg.com/images/medicine-img/vitamin-c.jpg',
            desc: 'Boosts immunity and overall health.'
        }
    ];
    container.innerHTML = `
        <div class="essentials-grid">
            ${essentials.map(item => `
                <div class="essential-card">
                    <img src="${item.img}" alt="${item.name}" class="essential-img" />
                    <div class="essential-info">
                        <h4>${item.name}</h4>
                        <div class="essential-category">${item.category}</div>
                        <div class="essential-desc">${item.desc}</div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}
window.addEventListener('DOMContentLoaded', createEssentialsUI);

// --- Awareness Blog Feature ---
function createBlogUI() {
    const container = document.getElementById('blog-container');
    if (!container) return;
    const blogs = [
        {
            title: 'Understanding Generic Medicines: Myths & Facts',
            summary: 'Learn the truth about generic medicines, their safety, and how they compare to branded drugs.',
            author: 'Dr. A. Sharma',
            date: '2024-06-01',
            img: 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=400&q=80',
            content: 'Generic medicines are as effective and safe as branded medicines. They undergo rigorous testing and are approved by regulatory authorities. The main difference is the price, making them more affordable for everyone.'
        },
        {
            title: 'How to Read a Medicine Label',
            summary: 'A step-by-step guide to understanding the information on your medicine packaging.',
            author: 'Pharm. R. Gupta',
            date: '2024-06-03',
            img: 'https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?auto=format&fit=crop&w=400&q=80',
            content: 'Medicine labels contain vital information: active ingredients, dosage, expiry, manufacturer, and warnings. Always check the expiry date and follow the prescribed dosage.'
        },
        {
            title: 'Why You Should Not Self-Medicate',
            summary: 'The dangers of self-medicating and why consulting a doctor is crucial.',
            author: 'Dr. S. Iyer',
            date: '2024-06-05',
            img: 'https://images.unsplash.com/photo-1464983953574-0892a716854b?auto=format&fit=crop&w=400&q=80',
            content: 'Self-medication can lead to incorrect diagnosis, drug interactions, and resistance. Always consult a healthcare professional before taking any medicine.'
        },
        {
            title: 'Affordable Healthcare: The Role of Jan Aushadhi Kendras',
            summary: 'How government-run Kendras are making medicines accessible and affordable.',
            author: 'Health Ministry',
            date: '2024-06-07',
            img: 'https://images.unsplash.com/photo-1505751172876-fa1923c5c528?auto=format&fit=crop&w=400&q=80',
            content: 'Jan Aushadhi Kendras provide quality generic medicines at low prices, helping millions access essential drugs. Find your nearest Kendra and save on healthcare costs.'
        },
        {
            title: 'Antibiotic Resistance: What You Need to Know',
            summary: 'Understanding the global threat of antibiotic resistance and how to prevent it.',
            author: 'Dr. M. Khan',
            date: '2024-06-10',
            img: 'https://images.unsplash.com/photo-1516574187841-cb9cc2ca948b?auto=format&fit=crop&w=400&q=80',
            content: 'Misuse of antibiotics leads to resistance, making infections harder to treat. Always complete your antibiotic course and never use leftover medicines.'
        },
        {
            title: 'Safe Storage of Medicines at Home',
            summary: 'Tips for storing medicines safely to maintain their effectiveness.',
            author: 'Pharm. L. Patel',
            date: '2024-06-12',
            img: 'https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=400&q=80',
            content: 'Store medicines in a cool, dry place, away from sunlight and children. Check expiry dates regularly and dispose of expired medicines safely.'
        },
        {
            title: 'Essential First Aid Items for Every Home',
            summary: 'A checklist of must-have first aid items for emergencies.',
            author: 'Red Cross India',
            date: '2024-06-14',
            img: 'https://images.unsplash.com/photo-1503457574465-494bba506e52?auto=format&fit=crop&w=400&q=80',
            content: 'Every home should have bandages, antiseptic, pain relievers, thermometer, and ORS. Keep your first aid kit updated and accessible.'
        },
        {
            title: 'The Importance of Completing Your Medicine Course',
            summary: 'Why you should always finish your prescribed medicine course.',
            author: 'Dr. P. Verma',
            date: '2024-06-16',
            img: 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?auto=format&fit=crop&w=400&q=80',
            content: 'Stopping medicines early can lead to relapse and resistance. Always complete the full course as prescribed by your doctor.'
        },
        {
            title: 'How to Dispose of Expired Medicines Safely',
            summary: 'Proper disposal methods to protect your family and the environment.',
            author: 'Pharm. S. Rao',
            date: '2024-06-18',
            img: 'https://images.unsplash.com/photo-1467271383972-6d771c1e1a49?auto=format&fit=crop&w=400&q=80',
            content: 'Do not throw medicines in the trash or flush them. Return them to a pharmacy or follow local disposal guidelines to prevent harm.'
        },
        {
            title: 'Vitamins and Supplements: Do You Really Need Them?',
            summary: 'A guide to understanding when supplements are necessary.',
            author: 'Dr. N. Singh',
            date: '2024-06-20',
            img: 'https://images.unsplash.com/photo-1501594907352-04cda38ebc29?auto=format&fit=crop&w=400&q=80',
            content: 'Most people get enough vitamins from a balanced diet. Supplements may be needed for deficiencies, pregnancy, or certain conditions. Consult your doctor before starting any supplement.'
        },
        {
            title: 'What to Do in Case of Medicine Allergy',
            summary: 'Recognizing and responding to medicine allergies.',
            author: 'Dr. R. Mehta',
            date: '2024-06-22',
            img: 'https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?auto=format&fit=crop&w=400&q=80',
            content: 'Allergic reactions can range from mild rashes to severe anaphylaxis. Stop the medicine and seek medical help immediately if you suspect an allergy.'
        },
        {
            title: 'How to Talk to Your Doctor About Medicines',
            summary: 'Tips for effective communication with your healthcare provider.',
            author: 'Dr. S. Banerjee',
            date: '2024-06-24',
            img: 'https://images.unsplash.com/photo-1465101178521-c1a9136a3b41?auto=format&fit=crop&w=400&q=80',
            content: 'Be honest about your symptoms, allergies, and other medicines you take. Ask questions if you are unsure about your prescription.'
        },
        {
            title: 'Children and Medicines: Safety Tips for Parents',
            summary: 'How to safely give medicines to children and avoid common mistakes.',
            author: 'Pediatric Assoc.',
            date: '2024-06-26',
            img: 'https://images.unsplash.com/photo-1505751172876-fa1923c5c528?auto=format&fit=crop&w=400&q=80',
            content: 'Use the correct dosage and measuring device. Never give adult medicines to children. Store all medicines out of reach.'
        },
        {
            title: 'The Role of Pharmacists in Your Healthcare',
            summary: 'Why pharmacists are an important part of your health team.',
            author: 'Pharm. T. Joshi',
            date: '2024-06-28',
            img: 'https://images.unsplash.com/photo-1516574187841-cb9cc2ca948b?auto=format&fit=crop&w=400&q=80',
            content: 'Pharmacists can advise on medicine use, side effects, and interactions. Consult them for any doubts about your prescription.'
        }
    ];
    container.innerHTML = `
        <div class="blog-grid">
            ${blogs.map((blog, i) => `
                <div class="blog-card" data-idx="${i}">
                    <img src="${blog.img}" alt="${blog.title}" class="blog-img" />
                    <div class="blog-info">
                        <h4>${blog.title}</h4>
                        <div class="blog-meta">By ${blog.author} | ${blog.date}</div>
                        <div class="blog-summary">${blog.summary}</div>
                    </div>
                </div>
            `).join('')}
        </div>
        <div id="blog-modal" class="blog-modal" style="display:none;">
            <div class="blog-modal-content">
                <span class="blog-modal-close">&times;</span>
                <img id="modal-img" class="blog-modal-img" src="" alt="" />
                <h3 id="modal-title"></h3>
                <div id="modal-meta" class="blog-modal-meta"></div>
                <div id="modal-content" class="blog-modal-body"></div>
            </div>
        </div>
    `;
    // Modal logic
    const modal = document.getElementById('blog-modal');
    const closeBtn = modal.querySelector('.blog-modal-close');
    const modalImg = document.getElementById('modal-img');
    const modalTitle = document.getElementById('modal-title');
    const modalMeta = document.getElementById('modal-meta');
    const modalContent = document.getElementById('modal-content');
    container.querySelectorAll('.blog-card').forEach(card => {
        card.addEventListener('click', function() {
            const idx = parseInt(this.getAttribute('data-idx'));
            const blog = blogs[idx];
            modalImg.src = blog.img;
            modalImg.alt = blog.title;
            modalTitle.textContent = blog.title;
            modalMeta.textContent = `By ${blog.author} | ${blog.date}`;
            modalContent.textContent = blog.content;
            modal.style.display = 'flex';
        });
    });
    closeBtn.addEventListener('click', () => { modal.style.display = 'none'; });
    modal.addEventListener('click', (e) => { if (e.target === modal) modal.style.display = 'none'; });
}
window.addEventListener('DOMContentLoaded', createBlogUI);

// --- Other Features Placeholders ---
// TODO: Implement price comparison, save for future, daily essentials, blog, etc. 
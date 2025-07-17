// --- Navigation: Page Links & Active State ---
// No smooth scroll needed for multi-page site, but we'll handle active state.
document.addEventListener('DOMContentLoaded', () => {
    const navLinks = document.querySelectorAll('.nav-links a');
    const currentPath = window.location.pathname;

    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
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
function initializeKendraFinder() {
    const mapDiv = document.getElementById('kendra-map');
    const kendraListDiv = document.getElementById('kendra-list');

    if (!mapDiv || !window.L || mapDiv._leaflet_id) {
        return; // Exit if no map div, no Leaflet, or map already initialized
    }
    const kendras = [
        { name: 'Jan Aushadhi Kendra - Connaught Place', address: 'Shop No. 5, Palika Bazar, Connaught Place', city: 'Delhi', lat: 28.6315, lng: 77.2167 },
        { name: 'Jan Aushadhi Kendra - Andheri', address: 'Shop 12, Andheri West, Near Station', city: 'Mumbai', lat: 19.1197, lng: 72.8468 },
        { name: 'Jan Aushadhi Kendra - Jayanagar', address: 'No. 44, 4th Block, Jayanagar', city: 'Bangalore', lat: 12.9250, lng: 77.5938 },
        { name: 'Jan Aushadhi Kendra - Salt Lake', address: 'CF-123, Sector 1, Salt Lake', city: 'Kolkata', lat: 22.5867, lng: 88.4172 },
        { name: 'Jan Aushadhi Kendra - T Nagar', address: 'Shop 8, North Usman Road, T Nagar', city: 'Chennai', lat: 13.0446, lng: 80.2337 }
    ];
    const map = L.map('kendra-map').setView([22.9734, 78.6569], 5.2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    kendras.forEach(kendra => {
        const marker = L.marker([kendra.lat, kendra.lng]).addTo(map);
        marker.bindPopup(`<b>${kendra.name}</b><br>${kendra.address}<br>${kendra.city}`);
    });

    // This is the critical fix. It tells the map to re-check its size after
    // the browser has finished rendering the page layout, ensuring it draws correctly.
    setTimeout(function() {
        map.invalidateSize();
    }, 100);

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
    const converter = new showdown.Converter({
        simplifiedAutoLink: true,
        strikethrough: true,
        tables: true
    });

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
            const htmlReply = converter.makeHtml(aiReply);
            replaceLastAIMessage(htmlReply);
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
        if (sender === 'user') {
            msgDiv.textContent = text;
        } else {
            msgDiv.innerHTML = text;
        }
        chatWindow.appendChild(msgDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
    function replaceLastAIMessage(html) {
        const msgs = chatWindow.querySelectorAll('.ai-msg');
        if (msgs.length > 0) {
            msgs[msgs.length - 1].innerHTML = html;
        }
    }
}

// --- Price Comparison Feature ---
function createPriceComparisonUI() {
    const container = document.getElementById('price-comparison-container');
    if (!container) return;
    container.innerHTML = `
        <h3>Price Comparison</h3>
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

// --- Save for Future Purchase Feature ---
function createSaveForFutureUI() {
    const container = document.getElementById('save-future-container');
    if (!container) return;
    container.innerHTML = `
        <h3>Save for Future</h3>
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

// --- Daily Essentials Feature ---
function createEssentialsUI() {
    const container = document.getElementById('essentials-container');
    if (!container) return;
    const essentials = [
        { name: 'Paracetamol 500mg', category: 'Pain Relief', img: 'https://images.unsplash.com/photo-1587854692152-cbe660dbde88?auto=format&fit=crop&w=800&q=80', desc: 'Common pain and fever reducer.' },
        { name: 'ORS Sachet', category: 'Hydration', img: 'https://images.unsplash.com/photo-1613565373398-6902f31005a8?auto=format&fit=crop&w=800&q=80', desc: 'Oral rehydration for dehydration.' },
        { name: 'Digital Thermometer', category: 'Health Devices', img: 'https://images.unsplash.com/photo-1627342375752-ce3734a3621f?auto=format&fit=crop&w=800&q=80', desc: 'Accurate temperature measurement.' },
        { name: 'Hand Sanitizer', category: 'Hygiene', img: 'https://images.unsplash.com/photo-1584308666744-84804044039b?auto=format&fit=crop&w=800&q=80', desc: 'Essential for hand hygiene on the go.' },
        { name: 'Bandages', category: 'First Aid', img: 'https://images.unsplash.com/photo-1568311913139-994380a4843d?auto=format&fit=crop&w=800&q=80', desc: 'For minor cuts and wound protection.' },
        { name: 'Vitamin C Tablets', category: 'Supplements', img: 'https://images.unsplash.com/photo-1607619056574-7d8d3ee536b2?auto=format&fit=crop&w=800&q=80', desc: 'Boosts immunity and overall health.' }
    ];
    container.innerHTML = `
        <h3>Daily Essentials</h3>
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

// --- Awareness Blog Feature ---
function createBlogUI() {
    const container = document.getElementById('blog-container');
    if (!container) return;
    const blogs = [
        {
            title: 'Understanding Generic vs. Branded Medicines',
            summary: 'Learn the truth about generic medicines and how they compare to branded drugs.',
            author: 'Dr. A. Sharma',
            date: '2024-07-10',
            img: 'https://images.unsplash.com/photo-1584515933487-779824d29309?auto=format&fit=crop&w=800&q=80',
            content: 'Generic medicines are required to have the same active ingredient, strength, dosage form, and route of administration as the brand-name drug. They are just as safe and effective but often cost much less.'
        },
        {
            title: 'The Importance of Reading Medicine Labels',
            summary: 'A guide to understanding the crucial information on your medicine packaging.',
            author: 'Pharm. R. Gupta',
            date: '2024-07-09',
            img: 'https://images.unsplash.com/photo-1584515933487-779824d29309?auto=format&fit=crop&w=800&q=80',
            content: 'Medicine labels contain vital information: active ingredients, dosage instructions, expiration date, and warnings. Always check these details before taking any medication.'
        },
        {
            title: 'Dangers of Self-Medication',
            summary: 'Why consulting a doctor before taking medication is essential for your health.',
            author: 'Dr. S. Iyer',
            date: '2024-07-08',
            img: 'https://images.unsplash.com/photo-1550831107-1553da8c8464?auto=format&fit=crop&w=800&q=80',
            content: 'Self-medication can lead to incorrect diagnosis, adverse drug reactions, and may mask the symptoms of a more serious underlying condition. Always seek professional medical advice.'
        },
        {
            title: 'What is Antibiotic Resistance?',
            summary: 'Understanding the global threat of antibiotic resistance and our role in preventing it.',
            author: 'Dr. M. Khan',
            date: '2024-07-07',
            img: 'static/img/Antibiotic.jpg',
            content: 'Antibiotic resistance occurs when bacteria change in response to the use of these medicines. It is crucial to only take antibiotics when prescribed by a doctor and to always complete the full course.'
        },
        {
            title: 'Safe Storage of Medicines at Home',
            summary: 'Simple tips for storing your medicines safely to maintain their effectiveness.',
            author: 'Pharm. L. Patel',
            date: '2024-07-06',
            img: 'https://images.unsplash.com/photo-1516574187841-cb9cc2ca948b?auto=format&fit=crop&w=800&q=80',
            content: 'Store medicines in a cool, dry place away from direct sunlight and out of reach of children and pets. Do not store them in the bathroom medicine cabinet due to humidity.'
        },
        {
            title: 'Why You Should Not Self-Medicate',
            summary: 'The dangers of self-medicating and why consulting a doctor is crucial.',
            author: 'Dr. S. Iyer',
            date: '2024-06-05',
            img: 'static/img/self medicate.jpg',
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
            date: '2024-07-05',
            img: 'https://images.unsplash.com/photo-1603398938378-e54eab446dde?auto=format&fit=crop&w=800&q=80',
            content: 'Every home should have bandages, antiseptic wipes, pain relievers, a thermometer, and ORS. Keep your first aid kit updated and easily accessible.'
        },
        {
            title: 'How to Dispose of Expired Medicines Safely',
            summary: 'Proper disposal methods to protect your family and the environment.',
            author: 'Pharm. S. Rao',
            date: '2024-07-04',
            img: 'static/img/Expired.jpg',
            content: 'Do not throw medicines in the trash or flush them down the toilet. Return them to a pharmacy take-back program or follow local disposal guidelines to prevent environmental harm.'
        },
        {
            title: 'How to Talk to Your Doctor About Medicines',
            summary: 'Tips for effective communication with your healthcare provider.',
            author: 'Dr. S. Banerjee',
            date: '2024-07-03',
            img: 'static/img/doctor.jpg',
            content: 'Be prepared to discuss your symptoms, current medications (including supplements), and any allergies. Ask questions if you are unsure about your prescription or treatment plan.'
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

// --- Central Page Initializer ---
document.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;

    if (path.includes('kendra-finder-page')) {
        initializeKendraFinder();
    }
    if (path.includes('ai-assistant-page')) {
        createAIChatUI();
    }
    if (path.includes('tools-page')) {
        createPriceComparisonUI();
        createSaveForFutureUI();
        createEssentialsUI();
    }
    if (path.includes('blog-page')) {
        createBlogUI();
    }
});
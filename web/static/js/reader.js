/**
 * Storywizard Reader — Kindle-like page navigation and reading experience.
 */

let currentPage = 0;
let totalPages = 0;
let novelData = null;

function initReader(novel, slug) {
    novelData = novel;
    const pages = document.querySelectorAll('.page');
    totalPages = pages.length;

    document.getElementById('totalPages').textContent = totalPages;
    buildTOC(novel);
    goToPage(0);
    bindEvents();
    applyStoredPreferences();
}

/* ---- Navigation ---- */

function goToPage(index) {
    if (index < 0 || index >= totalPages) return;
    currentPage = index;

    const container = document.getElementById('pageContainer');
    container.style.transform = `translateX(-${index * 100}%)`;

    document.getElementById('currentPage').textContent = index + 1;
    document.getElementById('prevPage').disabled = index === 0;
    document.getElementById('nextPage').disabled = index === totalPages - 1;

    // Progress bar
    const progress = totalPages > 1 ? (index / (totalPages - 1)) * 100 : 0;
    document.getElementById('progressBar').style.width = progress + '%';

    // Update TOC active state
    document.querySelectorAll('.toc-item').forEach(item => {
        item.classList.toggle('active', parseInt(item.dataset.page) === index);
    });

    // Scroll page content to top
    const pages = document.querySelectorAll('.page');
    if (pages[index]) pages[index].scrollTop = 0;
}

function nextPage() {
    goToPage(currentPage + 1);
}

function prevPage() {
    goToPage(currentPage - 1);
}

/* ---- Table of Contents ---- */

function buildTOC(novel) {
    const list = document.getElementById('tocList');

    // Title page
    const titleItem = document.createElement('a');
    titleItem.className = 'toc-item';
    titleItem.dataset.page = '0';
    titleItem.innerHTML = '<span class="toc-scene-num">Cover</span>' + novel.metadata.title;
    titleItem.onclick = () => { goToPage(0); toggleTOC(); };
    list.appendChild(titleItem);

    // Style guide
    const styleItem = document.createElement('a');
    styleItem.className = 'toc-item';
    styleItem.dataset.page = '1';
    styleItem.innerHTML = '<span class="toc-scene-num">Reference</span>Visual Style Guide';
    styleItem.onclick = () => { goToPage(1); toggleTOC(); };
    list.appendChild(styleItem);

    // Scenes
    novel.panel_scripts.forEach((script, i) => {
        const item = document.createElement('a');
        item.className = 'toc-item';
        item.dataset.page = String(i + 2);
        item.innerHTML =
            `<span class="toc-scene-num">Scene ${script.scene_number}</span>` +
            script.scene_title;
        item.onclick = () => { goToPage(i + 2); toggleTOC(); };
        list.appendChild(item);
    });

    // End page
    const endItem = document.createElement('a');
    endItem.className = 'toc-item';
    endItem.dataset.page = String(novel.panel_scripts.length + 2);
    endItem.innerHTML = '<span class="toc-scene-num">Epilogue</span>The End';
    endItem.onclick = () => { goToPage(novel.panel_scripts.length + 2); toggleTOC(); };
    list.appendChild(endItem);
}

function toggleTOC() {
    document.getElementById('tocSidebar').classList.toggle('open');
}

/* ---- Style Settings ---- */

function toggleStylePanel() {
    document.getElementById('stylePanel').classList.toggle('open');
}

function adjustFontSize(delta) {
    const page = document.querySelector('.reader-page');
    const current = parseFloat(getComputedStyle(page).getPropertyValue('--font-size-base'));
    const newSize = Math.max(0.75, Math.min(1.5, current + delta * 0.1));
    page.style.setProperty('--font-size-base', newSize + 'rem');
    localStorage.setItem('sw-font-size', newSize);
}

function setTheme(theme) {
    const page = document.querySelector('.reader-page');
    page.classList.remove('theme-light', 'theme-sepia', 'theme-dark');
    if (theme !== 'default') {
        page.classList.add('theme-' + theme);
    }
    localStorage.setItem('sw-theme', theme);
}

function applyStoredPreferences() {
    const fontSize = localStorage.getItem('sw-font-size');
    if (fontSize) {
        document.querySelector('.reader-page').style.setProperty('--font-size-base', fontSize + 'rem');
    }
    const theme = localStorage.getItem('sw-theme');
    if (theme) {
        setTheme(theme);
    }
}

/* ---- Fullscreen ---- */

function toggleFullscreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {});
    } else {
        document.exitFullscreen();
    }
}

/* ---- Event Binding ---- */

function bindEvents() {
    document.getElementById('prevPage').onclick = prevPage;
    document.getElementById('nextPage').onclick = nextPage;
    document.getElementById('btnToc').onclick = toggleTOC;
    document.getElementById('tocClose').onclick = toggleTOC;
    document.getElementById('btnStyle').onclick = toggleStylePanel;
    document.getElementById('btnFullscreen').onclick = toggleFullscreen;

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight' || e.key === ' ') {
            e.preventDefault();
            nextPage();
        } else if (e.key === 'ArrowLeft') {
            e.preventDefault();
            prevPage();
        } else if (e.key === 'Escape') {
            document.getElementById('tocSidebar').classList.remove('open');
            document.getElementById('stylePanel').classList.remove('open');
        }
    });

    // Touch swipe navigation
    let touchStartX = 0;
    let touchStartY = 0;
    const viewport = document.getElementById('readerViewport');

    viewport.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
        touchStartY = e.changedTouches[0].screenY;
    }, { passive: true });

    viewport.addEventListener('touchend', (e) => {
        const dx = e.changedTouches[0].screenX - touchStartX;
        const dy = e.changedTouches[0].screenY - touchStartY;
        // Only swipe if horizontal movement is dominant
        if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) {
            if (dx < 0) nextPage();
            else prevPage();
        }
    }, { passive: true });

    // Click on viewport edges for navigation
    viewport.addEventListener('click', (e) => {
        const rect = viewport.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const width = rect.width;
        // Left 20% = prev, right 20% = next
        if (x < width * 0.2) prevPage();
        else if (x > width * 0.8) nextPage();
    });

    // Close panels on outside click
    document.addEventListener('click', (e) => {
        const stylePanel = document.getElementById('stylePanel');
        const btnStyle = document.getElementById('btnStyle');
        if (stylePanel.classList.contains('open') &&
            !stylePanel.contains(e.target) &&
            e.target !== btnStyle) {
            stylePanel.classList.remove('open');
        }
    });
}

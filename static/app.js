/**
 * 🛒 Liste de Courses — Frontend Application
 * Handles all UI interactions, API calls, and state management.
 */

// ─── State ───────────────────────────────────────────────────────────────────

const state = {
    recettes: [],
    selectedIndices: new Set(),
    listeCompilee: null,
    texteExport: '',
    checkedItems: new Set(),
};

// ─── API Layer ───────────────────────────────────────────────────────────────

const api = {
    async getRecettes() {
        const res = await fetch('/api/recettes');
        return res.json();
    },

    async addRecette(recette) {
        const res = await fetch('/api/recettes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(recette),
        });
        return res.json();
    },

    async deleteRecette(index) {
        const res = await fetch(`/api/recettes/${index}`, { method: 'DELETE' });
        return res.json();
    },

    async compilerListe(indices) {
        const res = await fetch('/api/compiler', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ indices }),
        });
        return res.json();
    },

    async gitPush(token) {
        const res = await fetch('/api/git-push', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        return res.json();
    },
};

// ─── DOM References ──────────────────────────────────────────────────────────

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const dom = {
    recipesGrid: $('#recipes-grid'),
    selectionList: $('#selection-list'),
    selectionBadge: $('#selection-badge'),
    btnGenerate: $('#btn-generate'),
    listeEmpty: $('#liste-empty'),
    listeContent: $('#liste-content'),
    listeRecettesSummary: $('#liste-recettes-summary'),
    listeItems: $('#liste-items'),
    listeStats: $('#liste-stats'),
    toastContainer: $('#toast-container'),
};

// ─── Tab Navigation ──────────────────────────────────────────────────────────

function initTabs() {
    $$('.tab').forEach((tab) => {
        tab.addEventListener('click', () => {
            $$('.tab').forEach((t) => t.classList.remove('active'));
            $$('.tab-content').forEach((c) => c.classList.remove('active'));

            tab.classList.add('active');
            $(`#tab-${tab.dataset.tab}`).classList.add('active');
        });
    });
}

function switchToTab(tabName) {
    $$('.tab').forEach((t) => t.classList.remove('active'));
    $$('.tab-content').forEach((c) => c.classList.remove('active'));
    $(`.tab[data-tab="${tabName}"]`).classList.add('active');
    $(`#tab-${tabName}`).classList.add('active');
}

// ─── Toast Notifications ─────────────────────────────────────────────────────

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = { success: '✅', error: '❌', info: 'ℹ️' };
    toast.innerHTML = `<span>${icons[type] || ''}</span> ${message}`;

    dom.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('toast-exit');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ─── Render Recipes Grid ─────────────────────────────────────────────────────

function renderRecipes() {
    if (state.recettes.length === 0) {
        dom.recipesGrid.innerHTML = `
            <div class="empty-state" style="grid-column: 1/-1">
                <span class="empty-icon">📖</span>
                <h3>Aucune recette</h3>
                <p>Cliquez sur "Ajouter" pour créer votre première recette.</p>
            </div>
        `;
        return;
    }

    dom.recipesGrid.innerHTML = state.recettes
        .map((r, i) => {
            const topIngredients = r.ingredients.slice(0, 4);
            const moreCount = r.ingredients.length - 4;
            return `
                <div class="recipe-card" data-index="${i}">
                    <div class="recipe-card-title">
                        <span>🍽️</span>
                        ${escapeHtml(r.nom)}
                    </div>
                    <div class="recipe-card-meta">
                        <span>🥄 ${r.ingredients.length} ingrédient${r.ingredients.length > 1 ? 's' : ''}</span>
                        <span>👤 ${r.portions} portion${r.portions > 1 ? 's' : ''}</span>
                    </div>
                    <div class="recipe-card-ingredients">
                        ${topIngredients.map((ing) => `<span class="ingredient-chip">${escapeHtml(ing.nom)}</span>`).join('')}
                        ${moreCount > 0 ? `<span class="ingredient-chip">+${moreCount}</span>` : ''}
                    </div>
                </div>
            `;
        })
        .join('');

    // Click handlers
    $$('.recipe-card').forEach((card) => {
        card.addEventListener('click', () => {
            showRecipeDetail(parseInt(card.dataset.index));
        });
    });
}

// ─── Render Selection List ───────────────────────────────────────────────────

function renderSelection() {
    dom.selectionList.innerHTML = state.recettes
        .map((r, i) => {
            const isSelected = state.selectedIndices.has(i);
            return `
                <div class="selection-item ${isSelected ? 'selected' : ''}" data-index="${i}">
                    <div class="custom-checkbox"></div>
                    <div class="selection-item-info">
                        <div class="selection-item-name">${escapeHtml(r.nom)}</div>
                        <div class="selection-item-meta">
                            ${r.ingredients.length} ingrédients · ${r.portions} portion${r.portions > 1 ? 's' : ''}
                        </div>
                    </div>
                </div>
            `;
        })
        .join('');

    // Click handlers
    $$('.selection-item').forEach((item) => {
        item.addEventListener('click', () => {
            const idx = parseInt(item.dataset.index);
            if (state.selectedIndices.has(idx)) {
                state.selectedIndices.delete(idx);
            } else {
                state.selectedIndices.add(idx);
            }
            renderSelection();
            updateSelectionUI();
        });
    });
}

function updateSelectionUI() {
    const count = state.selectedIndices.size;

    // Badge
    if (count > 0) {
        dom.selectionBadge.textContent = count;
        dom.selectionBadge.classList.remove('hidden');
    } else {
        dom.selectionBadge.classList.add('hidden');
    }

    // Generate button
    dom.btnGenerate.disabled = count === 0;
}

// ─── Render Shopping List ────────────────────────────────────────────────────

function renderListe(data) {
    state.listeCompilee = data.liste;
    state.texteExport = data.texte_export;
    state.checkedItems.clear();

    // Header tags
    dom.listeRecettesSummary.innerHTML = data.recettes
        .map((nom) => `<span class="recette-tag">📖 ${escapeHtml(nom)}</span>`)
        .join('');

    // Items
    renderListeItems();

    // Stats
    dom.listeStats.textContent = `${data.liste.length} article${data.liste.length > 1 ? 's' : ''} au total`;

    // Show content
    dom.listeEmpty.classList.add('hidden');
    dom.listeContent.classList.remove('hidden');
}

function renderListeItems() {
    dom.listeItems.innerHTML = state.listeCompilee
        .map((ing, i) => {
            const checked = state.checkedItems.has(i);
            return `
                <div class="liste-item ${checked ? 'checked' : ''}" data-index="${i}">
                    <div class="liste-item-left">
                        <div class="liste-item-checkbox"></div>
                        <span class="liste-item-name">${escapeHtml(ing.nom)}</span>
                    </div>
                    <span class="liste-item-qty">${ing.quantite} ${escapeHtml(ing.unite)}</span>
                </div>
            `;
        })
        .join('');

    $$('.liste-item').forEach((item) => {
        item.addEventListener('click', () => {
            const idx = parseInt(item.dataset.index);
            if (state.checkedItems.has(idx)) {
                state.checkedItems.delete(idx);
            } else {
                state.checkedItems.add(idx);
            }
            renderListeItems();
        });
    });
}

// ─── Recipe Detail Modal ─────────────────────────────────────────────────────

let currentDetailIndex = -1;

function showRecipeDetail(index) {
    currentDetailIndex = index;
    const r = state.recettes[index];

    $('#detail-title').textContent = `🍽️ ${r.nom}`;
    $('#detail-portions').textContent = `${r.portions} portion${r.portions > 1 ? 's' : ''}`;

    $('#detail-ingredients').innerHTML = r.ingredients
        .map(
            (ing) => `
            <div class="detail-ing-row">
                <span class="detail-ing-name">${escapeHtml(ing.nom)}</span>
                <span class="detail-ing-qty">${ing.quantite} ${escapeHtml(ing.unite)}</span>
            </div>
        `
        )
        .join('');

    $('#modal-detail-overlay').classList.remove('hidden');
}

function closeDetailModal() {
    $('#modal-detail-overlay').classList.add('hidden');
    currentDetailIndex = -1;
}

// ─── Add Recipe Modal ────────────────────────────────────────────────────────

function openAddModal() {
    $('#input-nom').value = '';
    $('#input-portions').value = '1';
    $('#ingredients-list').innerHTML = '';
    addIngredientRow();
    addIngredientRow();
    addIngredientRow();
    $('#modal-overlay').classList.remove('hidden');
    $('#input-nom').focus();
}

function closeAddModal() {
    $('#modal-overlay').classList.add('hidden');
}

function addIngredientRow() {
    const row = document.createElement('div');
    row.className = 'ingredient-row';
    row.innerHTML = `
        <input type="text" placeholder="Ingrédient" class="ing-name">
        <input type="number" placeholder="Qté" class="ing-qty" min="0" step="any">
        <input type="text" placeholder="Unité" class="ing-unit" value="g">
        <button class="btn-remove-ing" title="Supprimer">✕</button>
    `;
    row.querySelector('.btn-remove-ing').addEventListener('click', () => {
        row.remove();
    });
    $('#ingredients-list').appendChild(row);
    row.querySelector('.ing-name').focus();
}

async function saveRecipe() {
    const nom = $('#input-nom').value.trim();
    const portions = parseInt($('#input-portions').value) || 1;

    if (!nom) {
        showToast('Entrez un nom de recette', 'error');
        return;
    }

    const ingredients = [];
    $$('.ingredient-row').forEach((row) => {
        const name = row.querySelector('.ing-name').value.trim();
        const qty = parseFloat(row.querySelector('.ing-qty').value);
        const unit = row.querySelector('.ing-unit').value.trim() || 'pièce(s)';

        if (name && !isNaN(qty) && qty > 0) {
            ingredients.push({ nom: name, quantite: qty, unite: unit });
        }
    });

    if (ingredients.length === 0) {
        showToast('Ajoutez au moins un ingrédient', 'error');
        return;
    }

    try {
        await api.addRecette({ nom, portions, ingredients });
        state.recettes = await api.getRecettes();
        renderRecipes();
        renderSelection();
        closeAddModal();
        showToast(`Recette "${nom}" ajoutée !`);
    } catch (e) {
        showToast('Erreur lors de l\'ajout', 'error');
    }
}

// ─── Delete Recipe ───────────────────────────────────────────────────────────

async function deleteRecipe() {
    if (currentDetailIndex < 0) return;

    const nom = state.recettes[currentDetailIndex].nom;

    if (!confirm(`Supprimer la recette "${nom}" ?`)) return;

    try {
        await api.deleteRecette(currentDetailIndex);
        state.recettes = await api.getRecettes();
        state.selectedIndices.clear();
        renderRecipes();
        renderSelection();
        updateSelectionUI();
        closeDetailModal();
        showToast(`Recette "${nom}" supprimée`, 'info');
    } catch (e) {
        showToast('Erreur lors de la suppression', 'error');
    }
}

// ─── Generate List ───────────────────────────────────────────────────────────

async function generateList() {
    const indices = Array.from(state.selectedIndices);

    dom.btnGenerate.disabled = true;
    dom.btnGenerate.innerHTML = '<span class="spinner"></span> Compilation...';

    try {
        const data = await api.compilerListe(indices);

        if (!data.success) {
            showToast(data.error || 'Erreur', 'error');
            return;
        }

        renderListe(data);
        switchToTab('liste');
        showToast(`${data.liste.length} articles compilés !`);
    } catch (e) {
        showToast('Erreur de compilation', 'error');
    } finally {
        dom.btnGenerate.disabled = false;
        dom.btnGenerate.innerHTML = '<span>🛒</span> Générer la liste';
    }
}

// ─── Export Functions ────────────────────────────────────────────────────────

async function copyToClipboard() {
    try {
        await navigator.clipboard.writeText(state.texteExport);
        showToast('Liste copiée ! Collez dans Samsung Notes 📋');
    } catch (e) {
        // Fallback
        const ta = document.createElement('textarea');
        ta.value = state.texteExport;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        ta.remove();
        showToast('Liste copiée ! Collez dans Samsung Notes 📋');
    }
}

function downloadTxt() {
    const blob = new Blob([state.texteExport], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `liste_courses_${new Date().toISOString().slice(0, 10)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('Fichier téléchargé ! 💾');
}

// ─── Git Push ────────────────────────────────────────────────────────────────

async function gitPush() {
    const token = prompt("Veuillez entrer le token d'authentification pour le Git Push :");
    if (!token) {
        showToast("Authentification annulée", "error");
        return;
    }

    const overlay = $('#modal-git-overlay');
    const stepsDiv = $('#git-steps');
    const statusDiv = $('#git-status');

    overlay.classList.remove('hidden');
    stepsDiv.innerHTML = '<div class="git-step">⏳ Synchronisation en cours...</div>';
    statusDiv.innerHTML = '';
    statusDiv.className = 'git-status';

    try {
        const data = await api.gitPush(token);

        stepsDiv.innerHTML = data.steps
            .map((step) => `<div class="git-step">✅ ${escapeHtml(step)}</div>`)
            .join('');

        if (data.success) {
            statusDiv.className = 'git-status success';
            statusDiv.textContent = data.message || 'Succès !';
            showToast('Git push réussi ! 🚀');
        } else {
            stepsDiv.innerHTML += `<div class="git-step error">❌ ${escapeHtml(data.error || 'Erreur inconnue')}</div>`;
            statusDiv.className = 'git-status error';
            statusDiv.textContent = 'Le push a échoué';
            showToast('Git push échoué', 'error');
        }
    } catch (e) {
        stepsDiv.innerHTML = '<div class="git-step error">❌ Erreur de connexion au serveur</div>';
        statusDiv.className = 'git-status error';
        statusDiv.textContent = 'Erreur réseau';
        showToast('Erreur réseau', 'error');
    }
}

// ─── Utilities ───────────────────────────────────────────────────────────────

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// ─── Event Listeners ─────────────────────────────────────────────────────────

function initEvents() {
    // Tabs
    initTabs();

    // Add recipe
    $('#btn-add-recipe').addEventListener('click', openAddModal);
    $('#btn-modal-close').addEventListener('click', closeAddModal);
    $('#btn-cancel').addEventListener('click', closeAddModal);
    $('#btn-save-recipe').addEventListener('click', saveRecipe);
    $('#btn-add-ingredient').addEventListener('click', addIngredientRow);

    // Detail modal
    $('#btn-detail-close').addEventListener('click', closeDetailModal);
    $('#btn-detail-ok').addEventListener('click', closeDetailModal);
    $('#btn-delete-recipe').addEventListener('click', deleteRecipe);

    // Generate list
    $('#btn-generate').addEventListener('click', generateList);

    // Export
    $('#btn-copy').addEventListener('click', copyToClipboard);
    $('#btn-download').addEventListener('click', downloadTxt);

    // Git push
    $('#btn-git-push').addEventListener('click', gitPush);
    $('#btn-git-close').addEventListener('click', () => $('#modal-git-overlay').classList.add('hidden'));
    $('#btn-git-ok').addEventListener('click', () => $('#modal-git-overlay').classList.add('hidden'));

    // Close modals on overlay click
    $('#modal-overlay').addEventListener('click', (e) => {
        if (e.target === e.currentTarget) closeAddModal();
    });
    $('#modal-detail-overlay').addEventListener('click', (e) => {
        if (e.target === e.currentTarget) closeDetailModal();
    });
    $('#modal-git-overlay').addEventListener('click', (e) => {
        if (e.target === e.currentTarget) $('#modal-git-overlay').classList.add('hidden');
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeAddModal();
            closeDetailModal();
            $('#modal-git-overlay').classList.add('hidden');
        }
    });
}

// ─── Init ────────────────────────────────────────────────────────────────────

async function init() {
    try {
        state.recettes = await api.getRecettes();
        renderRecipes();
        renderSelection();
        initEvents();
    } catch (e) {
        showToast('Erreur de chargement des recettes', 'error');
        console.error(e);
    }
}

document.addEventListener('DOMContentLoaded', init);

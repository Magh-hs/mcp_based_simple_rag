// Global variables
let currentPage = 1;
const pageSize = 20;
let allMessages = [];
let filteredMessages = [];
let sortColumn = 'timestamp';
let sortDirection = 'desc';

// API base URL - automatically detect environment
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000'  // Local development
    : `${window.location.protocol}//${window.location.host}`;  // Docker environment (proxy through nginx)

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    loadMessages();
    loadStats();
    
    // Set up periodic refresh
    setInterval(() => {
        loadStats();
        if (currentPage === 1) {
            loadMessages();
        }
    }, 30000); // Refresh every 30 seconds
});

async function initializeDashboard() {
    try {
        // Set up event listeners
        setupEventListeners();
        
        // Set default date filter to today
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('dateFilter').value = today;
        
        console.log('Dashboard initialized successfully');
    } catch (error) {
        console.error('Error initializing dashboard:', error);
        showError('Failed to initialize dashboard');
    }
}

function setupEventListeners() {
    // Search input
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchMessages();
        }
    });
    
    // Modal close when clicking outside
    const modal = document.getElementById('messageModal');
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeModal();
        }
    });
}

async function loadStats() {
    try {
        // Load total message count
        const countResponse = await fetch(`${API_BASE_URL}/messages/count`);
        if (!countResponse.ok) throw new Error('Failed to fetch message count');
        const countData = await countResponse.json();
        
        document.getElementById('totalMessages').textContent = countData.count || 0;
        
        // Load today's messages count
        const today = new Date().toISOString().split('T')[0];
        const todayResponse = await fetch(`${API_BASE_URL}/messages?limit=1000`);
        if (!todayResponse.ok) throw new Error('Failed to fetch today\'s messages');
        const todayData = await todayResponse.json();
        
        const todayCount = todayData.filter(msg => 
            msg.timestamp.startsWith(today)
        ).length;
        
        document.getElementById('todayMessages').textContent = todayCount;
        
        // Calculate unique conversations
        const uniqueConversations = new Set(
            todayData
                .filter(msg => msg.conversation_id)
                .map(msg => msg.conversation_id)
        ).size;
        
        document.getElementById('activeConversations').textContent = uniqueConversations;
        
    } catch (error) {
        console.error('Error loading stats:', error);
        showError('Failed to load statistics');
    }
}

async function loadMessages() {
    try {
        showLoading();
        
        const offset = (currentPage - 1) * pageSize;
        const conversationFilter = document.getElementById('conversationFilter').value;
        
        let url = `${API_BASE_URL}/messages?limit=${pageSize}&offset=${offset}`;
        if (conversationFilter) {
            url += `&conversation_id=${encodeURIComponent(conversationFilter)}`;
        }
        
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch messages');
        
        const messages = await response.json();
        allMessages = messages;
        
        // Apply client-side filters
        applyClientFilters();
        
        // Update conversation filter dropdown
        updateConversationFilter(messages);
        
        hideLoading();
        
    } catch (error) {
        console.error('Error loading messages:', error);
        showError('Failed to load messages');
        hideLoading();
    }
}

function applyClientFilters() {
    filteredMessages = [...allMessages];
    
    // Apply search filter
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    if (searchTerm) {
        filteredMessages = filteredMessages.filter(msg => 
            msg.user_query.toLowerCase().includes(searchTerm) ||
            msg.refined_query.toLowerCase().includes(searchTerm) ||
            msg.answer.toLowerCase().includes(searchTerm) ||
            (msg.conversation_id && msg.conversation_id.toLowerCase().includes(searchTerm))
        );
    }
    
    // Apply date filter
    const dateFilter = document.getElementById('dateFilter').value;
    if (dateFilter) {
        filteredMessages = filteredMessages.filter(msg => 
            msg.timestamp.startsWith(dateFilter)
        );
    }
    
    // Apply sorting
    sortMessages();
    
    // Update display
    displayMessages();
    updatePagination();
}

function sortMessages() {
    filteredMessages.sort((a, b) => {
        let aVal = a[sortColumn];
        let bVal = b[sortColumn];
        
        // Handle different data types
        if (sortColumn === 'timestamp') {
            aVal = new Date(aVal);
            bVal = new Date(bVal);
        } else if (typeof aVal === 'string') {
            aVal = aVal.toLowerCase();
            bVal = bVal.toLowerCase();
        }
        
        if (sortDirection === 'asc') {
            return aVal > bVal ? 1 : -1;
        } else {
            return aVal < bVal ? 1 : -1;
        }
    });
}

function displayMessages() {
    const tbody = document.getElementById('messagesTableBody');
    tbody.innerHTML = '';
    
    if (filteredMessages.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; padding: 40px; color: #718096;">
                    No messages found
                </td>
            </tr>
        `;
        return;
    }
    
    filteredMessages.forEach(message => {
        const row = document.createElement('tr');
        row.onclick = () => showMessageDetails(message);
        
        row.innerHTML = `
            <td>${formatTimestamp(message.timestamp)}</td>
            <td class="truncate" title="${escapeHtml(message.user_query)}">${escapeHtml(message.user_query)}</td>
            <td class="truncate" title="${escapeHtml(message.refined_query)}">${escapeHtml(message.refined_query)}</td>
            <td class="truncate" title="${escapeHtml(message.answer)}">${escapeHtml(message.answer)}</td>
            <td class="truncate" title="${message.conversation_id || 'N/A'}">${message.conversation_id || 'N/A'}</td>
        `;
        
        tbody.appendChild(row);
    });
    
    document.getElementById('showingCount').textContent = filteredMessages.length;
}

function updateConversationFilter(messages) {
    const select = document.getElementById('conversationFilter');
    const currentValue = select.value;
    
    // Get unique conversation IDs
    const conversationIds = [...new Set(
        messages
            .filter(msg => msg.conversation_id)
            .map(msg => msg.conversation_id)
    )].sort();
    
    // Clear existing options (except "All Conversations")
    select.innerHTML = '<option value="">All Conversations</option>';
    
    // Add conversation ID options
    conversationIds.forEach(id => {
        const option = document.createElement('option');
        option.value = id;
        option.textContent = `${id.substring(0, 8)}...`;
        option.title = id;
        select.appendChild(option);
    });
    
    // Restore previous selection if it still exists
    if (currentValue && conversationIds.includes(currentValue)) {
        select.value = currentValue;
    }
}

function showMessageDetails(message) {
    const modal = document.getElementById('messageModal');
    const modalContent = document.getElementById('modalContent');
    
    modalContent.innerHTML = `
        <div class="detail-item">
            <div class="detail-label">Timestamp</div>
            <div class="detail-content">${formatTimestamp(message.timestamp)}</div>
        </div>
        <div class="detail-item">
            <div class="detail-label">User Query</div>
            <div class="detail-content">${escapeHtml(message.user_query)}</div>
        </div>
        <div class="detail-item">
            <div class="detail-label">Refined Query</div>
            <div class="detail-content">${escapeHtml(message.refined_query)}</div>
        </div>
        <div class="detail-item">
            <div class="detail-label">Answer</div>
            <div class="detail-content">${escapeHtml(message.answer)}</div>
        </div>
        <div class="detail-item">
            <div class="detail-label">Conversation ID</div>
            <div class="detail-content">${message.conversation_id || 'N/A'}</div>
        </div>
    `;
    
    modal.style.display = 'block';
}

function closeModal() {
    document.getElementById('messageModal').style.display = 'none';
}

function sortTable(column) {
    if (sortColumn === column) {
        sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        sortColumn = column;
        sortDirection = 'desc';
    }
    
    applyClientFilters();
}

function searchMessages() {
    currentPage = 1;
    applyClientFilters();
}

function applyFilters() {
    currentPage = 1;
    loadMessages();
}

function refreshData() {
    loadMessages();
    loadStats();
}

function previousPage() {
    if (currentPage > 1) {
        currentPage--;
        loadMessages();
    }
}

function nextPage() {
    currentPage++;
    loadMessages();
}

function updatePagination() {
    const prevButton = document.getElementById('prevButton');
    const nextButton = document.getElementById('nextButton');
    const pageInfo = document.getElementById('pageInfo');
    
    prevButton.disabled = currentPage === 1;
    nextButton.disabled = filteredMessages.length < pageSize;
    
    pageInfo.textContent = `Page ${currentPage}`;
}

// Utility functions
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showLoading() {
    const tbody = document.getElementById('messagesTableBody');
    tbody.innerHTML = `
        <tr>
            <td colspan="5" style="text-align: center; padding: 40px;">
                <div class="loading"></div>
                <div style="margin-top: 10px;">Loading messages...</div>
            </td>
        </tr>
    `;
}

function hideLoading() {
    // Loading will be hidden when displayMessages() is called
}

function showError(message) {
    const tbody = document.getElementById('messagesTableBody');
    tbody.innerHTML = `
        <tr>
            <td colspan="5" style="text-align: center; padding: 40px; color: #e53e3e;">
                <div>❌ ${message}</div>
                <div style="margin-top: 10px; font-size: 0.9rem; color: #718096;">
                    Please check your connection and try again.
                </div>
            </td>
        </tr>
    `;
}

// Export functions for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        formatTimestamp,
        escapeHtml,
        sortMessages,
        applyClientFilters
    };
}
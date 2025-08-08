// Global variables
let currentConversationId = null;
let conversationHistory = [];
let isTyping = false;
let quickActionsVisible = false;
let sidebarOpen = false;

// API Configuration
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000'  // Local development
    : `${window.location.protocol}//${window.location.host}`;  // Docker environment

// Initialize chat interface
document.addEventListener('DOMContentLoaded', function() {
    initializeChat();
    setupEventListeners();
    checkConnection();
    loadConversationHistory();
});

function initializeChat() {
    // Generate new conversation ID
    currentConversationId = generateConversationId();
    
    // Initialize conversation history
    conversationHistory = [];
    
    // Focus on input
    const input = document.getElementById('messageInput');
    if (input) {
        input.focus();
    }
    
    console.log('Chat interface initialized');
}

function setupEventListeners() {
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    
    // Message input events
    messageInput.addEventListener('input', handleInputChange);
    messageInput.addEventListener('keydown', handleKeyDown);
    
    // Auto-resize textarea
    messageInput.addEventListener('input', autoResizeTextarea);
    
    // Click outside to close quick actions
    document.addEventListener('click', handleDocumentClick);
    
    // Prevent form submission
    messageInput.closest('form')?.addEventListener('submit', (e) => e.preventDefault());
}

function handleInputChange(event) {
    const input = event.target;
    const sendBtn = document.getElementById('sendBtn');
    const charCount = document.getElementById('charCount');
    
    // Update character count
    charCount.textContent = input.value.length;
    
    // Enable/disable send button
    sendBtn.disabled = input.value.trim().length === 0;
}

function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function autoResizeTextarea() {
    const textarea = document.getElementById('messageInput');
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

function handleDocumentClick(event) {
    const quickActions = document.getElementById('quickActions');
    const attachBtn = document.querySelector('.attach-btn');
    
    if (quickActionsVisible && 
        !quickActions.contains(event.target) && 
        !attachBtn.contains(event.target)) {
        hideQuickActions();
    }
}

// Connection Management
async function checkConnection() {
    const statusElement = document.getElementById('connectionStatus');
    
    try {
        statusElement.innerHTML = '<i class="fas fa-circle"></i> Connecting...';
        statusElement.className = 'status connecting';
        
        const response = await fetch(`${API_BASE_URL}/health`);
        
        if (response.ok) {
            statusElement.innerHTML = '<i class="fas fa-circle"></i> Connected';
            statusElement.className = 'status connected';
            showToast('Connected to chatbot service', 'success');
        } else {
            throw new Error('Service unavailable');
        }
    } catch (error) {
        statusElement.innerHTML = '<i class="fas fa-circle"></i> Disconnected';
        statusElement.className = 'status disconnected';
        showToast('Unable to connect to chatbot service', 'error');
        showErrorModal('Connection failed. Please check if the backend service is running.');
    }
}

// Message Handling
async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    
    if (!message || isTyping) return;
    
    // Clear input and reset height
    messageInput.value = '';
    messageInput.style.height = 'auto';
    document.getElementById('charCount').textContent = '0';
    document.getElementById('sendBtn').disabled = true;
    
    // Add user message to chat
    addMessage(message, 'user');
    
    // Add to conversation history
    conversationHistory.push({
        role: 'user',
        content: message,
        timestamp: new Date().toISOString()
    });
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Send to backend
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_query: message,
                conversation_history: conversationHistory.slice(0, -1) // Exclude current message
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Hide typing indicator
        hideTypingIndicator();
        
        // Add bot response
        addMessage(data.answer, 'bot');
        
        // Add to conversation history
        conversationHistory.push({
            role: 'assistant',
            content: data.answer,
            timestamp: new Date().toISOString()
        });
        
        // Update conversation ID if provided
        if (data.conversation_id) {
            currentConversationId = data.conversation_id;
        }
        
        // Save conversation to local storage
        saveConversationToStorage();
        
        // Update sidebar
        updateConversationList();
        
    } catch (error) {
        console.error('Error sending message:', error);
        hideTypingIndicator();
        
        addMessage('Sorry, I encountered an error while processing your message. Please try again.', 'bot', true);
        showToast('Failed to send message', 'error');
    }
}

function addMessage(content, sender, isError = false) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `${sender}-message`;
    
    const avatarIcon = sender === 'user' ? 'fas fa-user' : 'fas fa-robot';
    const bubbleClass = sender === 'user' ? 'user-bubble' : 'bot-bubble';
    
    if (isError) {
        content = `⚠️ ${content}`;
    }
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="${avatarIcon}"></i>
        </div>
        <div class="message-content">
            <div class="message-bubble ${bubbleClass}">
                <p>${escapeHtml(content)}</p>
            </div>
            <div class="message-time">${formatTime(new Date())}</div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

function showTypingIndicator() {
    isTyping = true;
    const typingIndicator = document.getElementById('typingIndicator');
    typingIndicator.style.display = 'flex';
    scrollToBottom();
}

function hideTypingIndicator() {
    isTyping = false;
    const typingIndicator = document.getElementById('typingIndicator');
    typingIndicator.style.display = 'none';
}

function scrollToBottom() {
    const chatMessages = document.getElementById('chatMessages');
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 100);
}

// Quick Actions
function showQuickActions() {
    const quickActions = document.getElementById('quickActions');
    quickActions.style.display = 'block';
    quickActionsVisible = true;
}

function hideQuickActions() {
    const quickActions = document.getElementById('quickActions');
    quickActions.style.display = 'none';
    quickActionsVisible = false;
}

function insertQuickMessage(message) {
    const messageInput = document.getElementById('messageInput');
    messageInput.value = message;
    messageInput.focus();
    
    // Trigger input event to update char count and enable send button
    messageInput.dispatchEvent(new Event('input'));
    
    hideQuickActions();
    autoResizeTextarea();
}

// Conversation History Management
function generateConversationId() {
    return 'conv_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function saveConversationToStorage() {
    if (conversationHistory.length === 0) return;
    
    const conversations = getStoredConversations();
    const conversationData = {
        id: currentConversationId,
        messages: conversationHistory,
        timestamp: new Date().toISOString(),
        preview: conversationHistory[0]?.content?.substring(0, 50) + '...' || 'New conversation'
    };
    
    // Update existing or add new
    const existingIndex = conversations.findIndex(c => c.id === currentConversationId);
    if (existingIndex >= 0) {
        conversations[existingIndex] = conversationData;
    } else {
        conversations.unshift(conversationData);
    }
    
    // Keep only last 50 conversations
    if (conversations.length > 50) {
        conversations.splice(50);
    }
    
    localStorage.setItem('chatConversations', JSON.stringify(conversations));
}

function getStoredConversations() {
    try {
        return JSON.parse(localStorage.getItem('chatConversations') || '[]');
    } catch (error) {
        console.error('Error parsing stored conversations:', error);
        return [];
    }
}

function loadConversationHistory() {
    const conversations = getStoredConversations();
    updateConversationList(conversations);
}

function updateConversationList(conversations = null) {
    if (!conversations) {
        conversations = getStoredConversations();
    }
    
    const conversationList = document.getElementById('conversationList');
    
    if (conversations.length === 0) {
        conversationList.innerHTML = `
            <div style="text-align: center; padding: 40px 20px; color: #94a3b8;">
                <i class="fas fa-comments" style="font-size: 2rem; margin-bottom: 10px; opacity: 0.5;"></i>
                <p>No conversations yet</p>
                <p style="font-size: 0.9rem;">Start chatting to see your history here</p>
            </div>
        `;
        return;
    }
    
    conversationList.innerHTML = conversations.map(conv => `
        <div class="conversation-item ${conv.id === currentConversationId ? 'active' : ''}" 
             onclick="loadConversation('${conv.id}')">
            <div class="conversation-preview">${escapeHtml(conv.preview)}</div>
            <div class="conversation-time">${formatTime(new Date(conv.timestamp))}</div>
        </div>
    `).join('');
}

function loadConversation(conversationId) {
    const conversations = getStoredConversations();
    const conversation = conversations.find(c => c.id === conversationId);
    
    if (!conversation) return;
    
    // Clear current chat
    clearChatMessages();
    
    // Load conversation
    currentConversationId = conversationId;
    conversationHistory = [...conversation.messages];
    
    // Display messages
    conversation.messages.forEach(msg => {
        addMessage(msg.content, msg.role === 'user' ? 'user' : 'bot');
    });
    
    // Update UI
    updateConversationList();
    toggleSidebar();
    
    showToast('Conversation loaded', 'info');
}

// UI Controls
function clearChat() {
    if (confirm('Are you sure you want to clear the current chat?')) {
        clearChatMessages();
        conversationHistory = [];
        currentConversationId = generateConversationId();
        showToast('Chat cleared', 'info');
    }
}

function clearChatMessages() {
    const chatMessages = document.getElementById('chatMessages');
    // Keep only the welcome message
    const welcomeMessage = chatMessages.querySelector('.welcome-message');
    chatMessages.innerHTML = '';
    if (welcomeMessage) {
        chatMessages.appendChild(welcomeMessage);
    }
}

function newChat() {
    clearChatMessages();
    conversationHistory = [];
    currentConversationId = generateConversationId();
    updateConversationList();
    toggleSidebar();
    
    // Focus on input
    document.getElementById('messageInput').focus();
    showToast('New chat started', 'info');
}

function exportChat() {
    if (conversationHistory.length === 0) {
        showToast('No conversation to export', 'info');
        return;
    }
    
    const chatData = {
        conversationId: currentConversationId,
        timestamp: new Date().toISOString(),
        messages: conversationHistory
    };
    
    const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat_${currentConversationId}_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showToast('Chat exported successfully', 'success');
}

function toggleDashboard() {
    // Open dashboard in new tab
    const dashboardUrl = window.location.hostname === 'localhost' 
        ? 'http://localhost:3000' 
        : window.location.origin.replace(':3001', ':3000'); // Assuming chat is on 3001, dashboard on 3000
    
    window.open(dashboardUrl, '_blank');
}

function toggleSidebar() {
    const sidebar = document.getElementById('conversationSidebar');
    sidebarOpen = !sidebarOpen;
    
    if (sidebarOpen) {
        sidebar.classList.add('open');
        loadConversationHistory();
    } else {
        sidebar.classList.remove('open');
    }
}

// Error Handling
function showErrorModal(message) {
    const modal = document.getElementById('errorModal');
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    modal.style.display = 'flex';
}

function closeErrorModal() {
    const modal = document.getElementById('errorModal');
    modal.style.display = 'none';
}

function retryConnection() {
    closeErrorModal();
    checkConnection();
}

// Toast Notifications
function showToast(message, type = 'info', duration = 3000) {
    const toastContainer = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const iconMap = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        info: 'fas fa-info-circle'
    };
    
    toast.innerHTML = `
        <i class="${iconMap[type]}"></i>
        <span>${escapeHtml(message)}</span>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto remove
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, duration);
}

// Utility Functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatTime(date) {
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) { // Less than 1 minute
        return 'Just now';
    } else if (diff < 3600000) { // Less than 1 hour
        const minutes = Math.floor(diff / 60000);
        return `${minutes}m ago`;
    } else if (diff < 86400000) { // Less than 1 day
        const hours = Math.floor(diff / 3600000);
        return `${hours}h ago`;
    } else {
        return date.toLocaleDateString();
    }
}

// Keyboard Shortcuts
document.addEventListener('keydown', function(event) {
    // Ctrl/Cmd + Enter to send message
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
        sendMessage();
    }
    
    // Ctrl/Cmd + K to focus on input
    if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault();
        document.getElementById('messageInput').focus();
    }
    
    // Ctrl/Cmd + Shift + C to clear chat
    if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'C') {
        event.preventDefault();
        clearChat();
    }
    
    // Ctrl/Cmd + Shift + H to toggle sidebar
    if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'H') {
        event.preventDefault();
        toggleSidebar();
    }
});

// Periodic connection check
setInterval(checkConnection, 30000); // Check every 30 seconds

// Export functions for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        escapeHtml,
        formatTime,
        generateConversationId
    };
}
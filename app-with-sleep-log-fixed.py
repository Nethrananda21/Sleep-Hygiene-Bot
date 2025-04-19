from flask import Flask, request, jsonify, render_template_string
import os
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai
from datetime import datetime
import json


# Create Flask app
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SleepBot - Your AI-Powered Sleep Coach</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .hero-bg {
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        }
        .section-bg {
            background-color: #2d2d2d;
        }
        .card-bg {
            background-color: #3a3a3a;
            border-radius: 0.5rem;
        }
        .moon-icon {
            color: #ffd700;
        }
        body {
            background: linear-gradient(90deg, #1a1a1a 0%, #2d2d2d 20%, #2d2d2d 80%, #1a1a1a 100%);
        }
    </style>
</head>
<body class="bg-gray-900 text-white min-h-screen flex flex-col">
    <div class="w-full">
    
        <section class="hero-bg py-20 md:py-24 text-center flex flex-col items-center justify-center flex-3">
            <h1 class="text-4xl font-bold mb-4"><span class="moon-icon">🌙</span> SleepBot</h1>
            <p class="text-lg text-gray-400 mb-8">Your AI-powered sleep coach for better rest and healthier habits</p>
            <div class="space-x-4">
                <a href="/sleep-log" class="inline-block px-6 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600">Sleep Log</a>
                <a href="/chat" class="inline-block px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700">Chat with SleepBot</a>
            </div>
        </section>

        <section class="section-bg py-12 md:py-16 flex-2">
            <div class="text-center">
                <h2 class="text-3xl font-semibold mb-2">How SleepBot Helps You Sleep Better</h2>
                <p class="text-gray-400 mb-8">Personalized features designed to improve your sleep quality</p>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                <div class="card-bg p-6 text-center">
                    <div class="text-3xl mb-4">⏳</div>
                    <h3 class="text-xl font-semibold mb-2">Sleep Tracking</h3>
                    <p class="text-gray-400">Log your sleep patterns and track your progress over time.</p>
                </div>
                <div class="card-bg p-6 text-center">
                    <div class="text-3xl mb-4">💡</div>
                    <h3 class="text-xl font-semibold mb-2">Smart Recommendations</h3>
                    <p class="text-gray-400">Get personalized sleep advice based on your habits and goals.</p>
                </div>
                <div class="card-bg p-6 text-center">
                    <div class="text-3xl mb-4">💬</div>
                    <h3 class="text-xl font-semibold mb-2">AI Sleep Assistant</h3>
                    <p class="text-gray-400">Chat with our AI to get answers to all your sleep-related questions.</p>
                </div>
                <div class="card-bg p-6 text-center">
                    <div class="text-3xl mb-4">⭐</div>
                    <h3 class="text-xl font-semibold mb-2">Relaxation Tools</h3>
                    <p class="text-gray-400">Access guided breathing exercises and soothing sounds to help you fall asleep.</p>
                </div>
            </div>
        </section>

        <section class="section-bg py-12 md:py-16 flex-1">
            <h2 class="text-3xl font-semibold text-center mb-6">Sleep Stats Preview</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="card-bg p-6 text-center">
                    <div class="text-3xl mb-4">📊</div>
                    <h3 class="text-xl font-semibold mb-2">Sleep Duration</h3>
                    <p class="text-gray-400">Track your average sleep hours per night.</p>
                </div>
                <div class="card-bg p-6 text-center">
                    <div class="text-3xl mb-4">🌙</div>
                    <h3 class="text-xl font-semibold mb-2">Sleep Quality</h3>
                    <p class="text-gray-400">Monitor your sleep quality trends over time.</p>
                </div>
            </div>
        </section>
    </div>
</body>
</html>
"""

# HTML template for the chat page (with modified JavaScript)
CHAT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat with SleepBot</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        :root {
            --background-color: #1a2526;
            --chat-bg-color: #2a3536;
            --text-color: #e0e0e0;
            --bot-message-bg: #3a4546;
            --user-message-bg: #4a86e8;
            --input-bg: #3a4546;
            --border-color: #4a5556;
            --indigo-400: #818cf8;
        }
        .moon-icon { color: #818cf8; }
        #chat-container { max-height: 70vh; overflow-y: auto; }
        #chat-container::-webkit-scrollbar { width: 6px; }
        #chat-container::-webkit-scrollbar-track { background: var(--chat-bg-color); }
        #chat-container::-webkit-scrollbar-thumb { background-color: var(--bot-message-bg); border-radius: 3px; }
        .typing-indicator span { animation: blink 1.4s infinite both; display: inline-block; background-color: #e0e0e0; width: 8px; height: 8px; border-radius: 50%; margin: 0 1px; }
        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes blink { 0% { opacity: 0.2; } 20% { opacity: 1; } 100% { opacity: 0.2; } }
        .log-checkbox { margin-right: 8px; }
        .log-list { max-height: 200px; overflow-y: auto; padding: 8px; }
        .log-item { margin-bottom: 4px; }
    </style>
</head>
<body class="bg-gray-900 text-white min-h-screen flex flex-col">
    <div class="container mx-auto px-4 sm:px-6 py-6 flex flex-col flex-1">
        <div class="flex items-center mb-6">
            <span class="moon-icon text-2xl mr-2">🌙</span>
            <h1 class="text-2xl font-semibold">Chat with SleepBot</h1>
        </div>
        <div class="bg-gray-800 p-4 rounded-lg mb-4 flex-1 overflow-y-auto" id="chat-container">
            <div class="flex items-start mb-2">
                <span class="text-xl mr-2">🌙</span>
                <div class="bg-gray-700 p-2 rounded-lg max-w-[80%]">
                    <p>Hello! I'm SleepBot. Ask me anything about sleep, or tell me about your sleep habits. I can use your saved sleep logs to give better advice!</p>
                    <span class="text-xs text-gray-400 block mt-1">Just now</span>
                </div>
            </div>
            <div id="typing-indicator" class="flex items-start mb-2 hidden">
                 <span class="text-xl mr-2">🌙</span>
                 <div class="bg-gray-700 p-2 rounded-lg">
                    <div class="typing-indicator"><span></span><span></span><span></span></div>
                 </div>
            </div>
        </div>
        <div class="bg-gray-800 p-4 rounded-lg mb-4" id="log-selection">
            <label class="flex items-center mb-2">
                <input type="checkbox" id="include-logs" class="log-checkbox">
                <span class="ml-2">Include sleep log data in analysis</span>
            </label>
            <div class="log-list bg-gray-700 p-2 rounded-lg hidden" id="log-list">
                <!-- Log items will be dynamically populated here -->
            </div>
            <button id="deselect-all" class="text-indigo-400 hover:text-indigo-300 text-sm mt-2 hidden">Deselect All</button>
        </div>
        <div class="flex items-center bg-gray-700 rounded-lg p-2">
            <input type="text" id="user-input" placeholder="Ask about your sleep patterns..." class="flex-1 bg-transparent text-white border-none outline-none px-2">
            <button id="send-button" class="text-blue-400 hover:text-blue-300 ml-2 text-xl">✈️</button>
        </div>
    </div>
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const chatContainer = document.getElementById('chat-container');
        const userInput = document.getElementById('user-input');
        const sendButton = document.getElementById('send-button');
        const typingIndicator = document.getElementById('typing-indicator');
        const includeLogsCheckbox = document.getElementById('include-logs');
        const logList = document.getElementById('log-list');
        const deselectAllButton = document.getElementById('deselect-all');

        function getCurrentTime() {
            return new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
        }

        function escapeHtml(unsafe) {
            return unsafe
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }

        function addMessage(message, isUser = false) {
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('flex', 'items-start', 'mb-2');

            const contentDiv = document.createElement('div');
            contentDiv.classList.add('p-2', 'rounded-lg', 'max-w-[80%]');

            if (isUser) {
                contentDiv.classList.add('ml-auto', 'bg-blue-600', 'text-white');
                messageDiv.classList.add('justify-end');
            } else {
                const icon = document.createElement('span');
                icon.classList.add('text-xl', 'mr-2');
                icon.textContent = '🌙';
                messageDiv.appendChild(icon);
                contentDiv.classList.add('bg-gray-700');
            }

            let formattedMessage = escapeHtml(message)
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>');

            contentDiv.innerHTML = `<p>${formattedMessage}</p><span class="text-xs text-gray-400 block mt-1">${getCurrentTime()}</span>`;
            const indicator = chatContainer.querySelector('#typing-indicator');
            if (indicator) {
                chatContainer.insertBefore(messageDiv, indicator);
            } else {
                chatContainer.appendChild(messageDiv);
            }

            messageDiv.appendChild(contentDiv);
            chatContainer.scrollTo(0, chatContainer.scrollHeight);
            console.log('Message added to DOM:', message);
        }

        function loadSleepLogs() {
            const savedLogs = localStorage.getItem('sleepLogs');
            if (savedLogs) {
                try {
                    return JSON.parse(savedLogs).map(log => ({
                        ...log,
                        date: new Date(log.date)
                    })).sort((a, b) => b.date - a.date).slice(0, 5);
                } catch (e) {
                    console.error("Error parsing sleep logs from localStorage:", e);
                    return [];
                }
            }
            return [];
        }

        function populateLogList(logs) {
            logList.innerHTML = '';
            logs.forEach(log => {
                const dateStr = log.date.toLocaleDateString('en-US', { month: 'numeric', day: 'numeric', year: '2-digit' });
                const item = document.createElement('div');
                item.className = 'log-item flex items-center';
                item.innerHTML = `
                    <input type="checkbox" class="log-checkbox" data-date="${log.date.toISOString()}" data-bed="${log.bedTime}" data-wake="${log.wakeTime}" data-quality="${log.sleepQuality}" data-notes="${encodeURIComponent(log.notes || '')}">
                    <span>${dateStr} - ${log.bedTime} to ${log.wakeTime} - Quality: ${log.sleepQuality}/5</span>
                `;
                logList.appendChild(item);
            });
            logList.classList.toggle('hidden', !includeLogsCheckbox.checked);
            deselectAllButton.classList.toggle('hidden', !includeLogsCheckbox.checked);
        }

        includeLogsCheckbox.addEventListener('change', function() {
            logList.classList.toggle('hidden', !this.checked);
            deselectAllButton.classList.toggle('hidden', !this.checked);
            if (this.checked) {
                const logs = loadSleepLogs();
                populateLogList(logs);
            }
        });

        deselectAllButton.addEventListener('click', function() {
            logList.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                checkbox.checked = false;
            });
        });

        async function sendMessage(message) {
            try {
                typingIndicator.classList.remove('hidden');
                chatContainer.scrollTo(0, chatContainer.scrollHeight);

                let logsToSend = [];
                if (includeLogsCheckbox.checked) {
                    const checkedLogs = Array.from(logList.querySelectorAll('input[type="checkbox"]:checked'));
                    logsToSend = checkedLogs.map(checkbox => ({
                        date: checkbox.dataset.date,
                        bedTime: checkbox.dataset.bed,
                        wakeTime: checkbox.dataset.wake,
                        sleepQuality: parseInt(checkbox.dataset.quality),
                        notes: decodeURIComponent(checkbox.dataset.notes)
                    }));
                }

                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message, logs: logsToSend })
                });

                typingIndicator.classList.add('hidden');

                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`Server error: ${response.status} - ${errorText}`);
                }

                const data = await response.json();
                console.log('Received data:', data);

                if (data.error) {
                    addMessage(`Error: ${data.error}`, false);
                } else if (data.response) {
                    console.log('Attempting to add response:', data.response);
                    addMessage(data.response, false);
                } else {
                    addMessage('Unexpected response format from server.', false);
                }
            } catch (error) {
                console.error('Fetch error:', error);
                typingIndicator.classList.add('hidden');
                addMessage(`Error: ${error.message || 'Could not reach server.'}`, false);
            }
        }

        function handleSend() {
            const message = userInput.value.trim();
            if (message) {
                addMessage(message, true);
                sendMessage(message);
                userInput.value = '';
            }
        }

        sendButton.addEventListener('click', handleSend);

        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
            }
        });

        userInput.focus();
        const initialLogs = loadSleepLogs();
        if (initialLogs.length > 0) {
            populateLogList(initialLogs);
        }
    });
</script>

</body>
</html>
"""

# HTML template for Sleep Log page (using localStorage)
SLEEP_LOG_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sleep Log</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        :root {
            --primary-color: #4a86e8;
            --secondary-color: #f1f3f4;
            --text-color: #202124;
            --light-text: #5f6368;
            --border-color: #dadce0;
            --indigo-400: #818cf8;
            --indigo-500: #6366f1;
            --gray-400: #9ca3af;
            --gray-500: #6b7280;
            --gray-800: #1f2937;
            --gray-900: #111827;
        }
        body { background-color: var(--gray-900); color: white; }
        .calendar { background W-color: var(--gray-800); border-radius: 0.5rem; }
        input[type="time"], textarea { background-color: var(--gray-800); color: white; border: none; }
        .quality-button { background-color: var(--gray-800); }
        .quality-button.selected { background-color: var(--indigo-400); }
        .submit-button { background-color: var(--indigo-400); }
        .submit-button:hover { background-color: var(--indigo-500); }
        .log-entry { border-left: 4px solid #818cf8; padding-left: 8px; }
    </style>
</head>
<body>
    <div class="container mx-auto px-4 sm:px-6 py-6">
        <div class="text-center py-4 border-b border-gray-700 mb-4">
            <h1 class="text-3xl font-semibold">Sleep Log</h1>
            <p class="text-gray-400">Track your sleep patterns and quality</p>
        </div>
        <div class="flex justify-center mb-4 space-x-4">
             <a href="/" class="text-indigo-400 hover:underline">Home</a>
             <a href="/chat" class="text-indigo-400 hover:underline">Chat</a>
             <a href="/sleep-log" class="text-indigo-400 font-bold">Sleep Log</a>
        </div>
        <div class="mb-6">
            <h1 class="text-2xl font-semibold mb-2">Log Your Sleep</h1>
            <p class="text-gray-400 mb-4">Record your sleep details to get personalized recommendations</p>
        </div>
        <div class="mb-6">
            <h2 class="text-xl font-semibold mb-2">Date</h2>
            <div class="calendar p-4" id="calendar"></div>
        </div>
        <div class="mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
                <h2 class="text-xl font-semibold mb-2">Bed Time</h2>
                <input type="time" id="bed-time" value="22:00" class="w-full p-2 rounded-lg">
            </div>
            <div>
                <h2 class="text-xl font-semibold mb-2">Wake Time</h2>
                <input type="time" id="wake-time" value="07:00" class="w-full p-2 rounded-lg">
            </div>
        </div>
        <div class="mb-6">
            <h2 class="text-xl font-semibold mb-2">Sleep Quality</h2>
            <div class="grid grid-cols-5 gap-2 mb-2" id="quality-buttons">
                <button class="quality-button p-2 rounded-lg" data-value="1">1</button>
                <button class="quality-button p-2 rounded-lg" data-value="2">2</button>
                <button class="quality-button p-2 rounded-lg selected" data-value="3">3</button>
                <button class="quality-button p-2 rounded-lg" data-value="4">4</button>
                <button class="quality-button p-2 rounded-lg" data-value="5">5</button>
            </div>
            <div class="text-gray-400 text-center" id="quality-label">Good</div>
        </div>
        <div class="mb-6">
            <h2 class="text-xl font-semibold mb-2">Notes</h2>
            <textarea id="notes" placeholder="Any factors that affected your sleep..." class="w-full p-2 rounded-lg h-24"></textarea>
        </div>
        <button class="submit-button w-full p-3 rounded-lg flex items-center justify-center" id="save-button">
            <span>+</span> Add / Update Sleep Record
        </button>
         <div class="mt-8" id="log-display">
             <h2 class="text-xl font-semibold mb-4">Your Recent Logs</h2>
             <div id="log-list" class="space-y-2">
             </div>
         </div>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const calendarEl = document.getElementById('calendar');
            const bedTimeEl = document.getElementById('bed-time');
            const wakeTimeEl = document.getElementById('wake-time');
            const qualityButtonsEl = document.getElementById('quality-buttons');
            const qualityLabelEl = document.getElementById('quality-label');
            const notesEl = document.getElementById('notes');
            const saveButtonEl = document.getElementById('save-button');
            const logListEl = document.getElementById('log-list');

            let currentMonth = new Date();
            let selectedDate = new Date();
            selectedDate.setHours(0, 0, 0, 0);
            let sleepQuality = 3;
            let sleepLogs = [];

            const qualityLabels = { 1: 'Poor', 2: 'Fair', 3: 'Good', 4: 'Very Good', 5: 'Excellent' };

            function loadSleepLogs() {
                const savedLogs = localStorage.getItem('sleepLogs');
                if (savedLogs) {
                    try {
                        sleepLogs = JSON.parse(savedLogs).map(log => ({
                            ...log,
                            date: new Date(log.date)
                        }));
                        sleepLogs.sort((a, b) => b.date - a.date);
                    } catch (e) {
                        console.error("Error parsing sleep logs from localStorage:", e);
                        sleepLogs = [];
                    }
                }
                displayLogs();
            }

            function saveSleepLogs() {
                sleepLogs.sort((a, b) => b.date - a.date);
                const logsToStore = sleepLogs.map(log => ({
                    ...log,
                    date: log.date.toISOString()
                }));
                localStorage.setItem('sleepLogs', JSON.stringify(logsToStore));
                displayLogs();
            }

            function formatMonthYear(date) { return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' }); }
            function getDaysInMonth(year, month) { return new Date(year, month + 1, 0).getDate(); }
            function getFirstDayOfMonth(year, month) { return new Date(year, month, 1).getDay(); }

            function renderCalendar() {
                const month = currentMonth.getMonth();
                const year = currentMonth.getFullYear();
                const daysInMonth = getDaysInMonth(year, month);
                const firstDayOfMonth = getFirstDayOfMonth(year, month);

                calendarEl.innerHTML = '';

                const header = document.createElement('div');
                header.className = 'flex justify-between items-center mb-2';
                header.innerHTML = `
                    <button class="text-gray-500 hover:text-gray-400 px-2 py-1 rounded"><</button>
                    <h2 class="text-lg font-semibold">${formatMonthYear(currentMonth)}</h2>
                    <button class="text-gray-500 hover:text-gray-400 px-2 py-1 rounded">></button>
                `;
                calendarEl.appendChild(header);

                header.children[0].addEventListener('click', () => {
                    currentMonth.setMonth(currentMonth.getMonth() - 1);
                    renderCalendar();
                });
                header.children[2].addEventListener('click', () => {
                    currentMonth.setMonth(currentMonth.getMonth() + 1);
                    renderCalendar();
                });

                const grid = document.createElement('div');
                grid.className = 'grid grid-cols-7 gap-1';

                ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'].forEach(day => {
                    const dayNameEl = document.createElement('div');
                    dayNameEl.className = 'text-center text-xs text-gray-500 font-medium';
                    dayNameEl.textContent = day;
                    grid.appendChild(dayNameEl);
                });

                const daysInPrevMonth = getDaysInMonth(year, month - 1);
                for (let i = firstDayOfMonth - 1; i >= 0; i--) {
                    const dayEl = document.createElement('div');
                    dayEl.className = 'text-center text-gray-600 p-1 rounded text-sm';
                    dayEl.textContent = daysInPrevMonth - i;
                    grid.appendChild(dayEl);
                }

                const today = new Date();
                today.setHours(0, 0, 0, 0);

                for (let i = 1; i <= daysInMonth; i++) {
                    const dayEl = document.createElement('div');
                    dayEl.className = 'text-center p-1 cursor-pointer rounded text-sm';
                    dayEl.textContent = i;

                    const date = new Date(year, month, i);
                    date.setHours(0, 0, 0, 0);

                    const isToday = today.getTime() === date.getTime();
                    const isSelected = selectedDate.getTime() === date.getTime();
                    const hasLog = sleepLogs.some(log => log.date.getTime() === date.getTime());

                    if (isToday) dayEl.classList.add('font-bold', 'text-indigo-400');
                    if (isSelected) {
                        dayEl.classList.add('bg-indigo-400', 'text-white');
                    } else if (hasLog) {
                        dayEl.classList.add('bg-indigo-400/20');
                    } else {
                        dayEl.classList.add('hover:bg-gray-700');
                    }

                    dayEl.addEventListener('click', () => {
                        selectedDate = date;
                        renderCalendar();
                        loadExistingLogForSelectedDate();
                    });

                    grid.appendChild(dayEl);
                }

                const totalCells = firstDayOfMonth + daysInMonth;
                const remainingCells = totalCells % 7 === 0 ? 0 : 7 - (totalCells % 7);
                for (let i = 1; i <= remainingCells; i++) {
                    const dayEl = document.createElement('div');
                    dayEl.className = 'text-center text-gray-600 p-1 rounded text-sm';
                    dayEl.textContent = i;
                    grid.appendChild(dayEl);
                }

                calendarEl.appendChild(grid);
            }

            function loadExistingLogForSelectedDate() {
                const existingLog = sleepLogs.find(log => log.date.getTime() === selectedDate.getTime());

                if (existingLog) {
                    bedTimeEl.value = existingLog.bedTime;
                    wakeTimeEl.value = existingLog.wakeTime;
                    sleepQuality = existingLog.sleepQuality;
                    notesEl.value = existingLog.notes || "";
                    saveButtonEl.textContent = 'Update Sleep Record';
                } else {
                    bedTimeEl.value = "22:00";
                    wakeTimeEl.value = "07:00";
                    sleepQuality = 3;
                    notesEl.value = "";
                    saveButtonEl.textContent = '+ Add Sleep Record';
                }
                updateQualitySelection();
            }

            function updateQualitySelection() {
                qualityButtonsEl.querySelectorAll('.quality-button').forEach(button => {
                    const buttonValue = parseInt(button.dataset.value);
                    button.classList.toggle('selected', buttonValue === sleepQuality);
                });
                qualityLabelEl.textContent = qualityLabels[sleepQuality] || 'Select Quality';
            }

            qualityButtonsEl.querySelectorAll('.quality-button').forEach(button => {
                button.addEventListener('click', () => {
                    sleepQuality = parseInt(button.dataset.value);
                    updateQualitySelection();
                });
            });

            saveButtonEl.addEventListener('click', () => {
                const logEntry = {
                    date: new Date(selectedDate.getFullYear(), selectedDate.getMonth(), selectedDate.getDate()),
                    bedTime: bedTimeEl.value,
                    wakeTime: wakeTimeEl.value,
                    sleepQuality: sleepQuality,
                    notes: notesEl.value.trim()
                };

                const existingLogIndex = sleepLogs.findIndex(log => log.date.getTime() === logEntry.date.getTime());

                if (existingLogIndex !== -1) {
                    sleepLogs[existingLogIndex] = logEntry;
                } else {
                    sleepLogs.push(logEntry);
                }

                saveSleepLogs();
                renderCalendar();
                alert('Sleep log saved!');
            });

            function displayLogs() {
                logListEl.innerHTML = '';
                if (sleepLogs.length === 0) {
                    logListEl.innerHTML = '<p class="text-gray-500">No sleep logs recorded yet.</p>';
                    return;
                }

                const logsToDisplay = sleepLogs.slice(0, 5);

                logsToDisplay.forEach(log => {
                    const logEl = document.createElement('div');
                    logEl.className = 'log-entry p-2 border border-gray-700 rounded bg-gray-800 text-sm';
                    const logDate = log.date.toLocaleDateString('en-CA');
                    logEl.innerHTML = `
                        <strong>${logDate}:</strong> Quality: ${qualityLabels[log.sleepQuality]}
                        <span class="text-gray-400">(${log.bedTime} - ${log.wakeTime})</span>
                        ${log.notes ? `<p class="text-gray-300 mt-1"><em>Notes:</em> ${log.notes}</p>` : ''}
                    `;
                    logListEl.appendChild(logEl);
                });
            }

            loadSleepLogs();
            renderCalendar();
            loadExistingLogForSelectedDate();
        });
    </script>
</body>
</html>
"""

# --- End: Template Definitions ---

# --- Start: AI Model Initialization (Stateful) ---
model = None
chat_session = None
try:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        generation_config = {
            "temperature": 0.8,
            "top_p": 0.95,
            "top_k": 40,
            "response_mime_type": "text/plain",
        }
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config=generation_config,
            system_instruction="""You are SleepBot, an AI assistant focused on analyzing sleep patterns and providing helpful, actionable advice based on user-provided sleep logs and questions if the logs are not provided give other relevent answer to the question . Be empathetic and supportive.

You will structure your answers as a bulleted list of key recommendations or insights. Each point should be concise and directly address the user's query. If providing more detailed advice, use sub-bullets under a main point or introduce a brief heading followed by bullet points.

Here are a few examples of how you should format your responses:

User Input: "I'm having trouble falling asleep."
SleepBot Response:
 Try to establish a relaxing bedtime routine.
 Ensure your bedroom is dark, quiet, and cool.
 Avoid caffeine and large meals close to bedtime.

User Input: "What are the benefits of waking up at the same time every day?"
SleepBot Response:
 Improved Sleep Quality:
     Helps regulate your body's natural sleep-wake cycle (circadian rhythm).
     Can lead to more restful and deeper sleep.
 Increased Daytime Energy:**
     Your body becomes more accustomed to a consistent schedule.
     Can reduce feelings of grogginess and fatigue during the day.
 Better Mood:
     Consistent sleep patterns can positively impact your emotional well-being.

Now, respond to the user's input following this format. NOTE:!!!If there is a sideheading go to the next Line!!!""",
        )
        chat_session = model.start_chat(history=[])
        print("Generative AI model configured and chat session started successfully.")
    else:
        print("Warning: GOOGLE_API_KEY not found. AI features will be limited.")

except Exception as e:
    print(f"Error configuring Generative AI or starting chat: {e}")

def format_sleep_logs_for_ai(logs):
    if not logs or not isinstance(logs, list):
        return "No recent sleep logs available."

    formatted_string = "Recent Sleep Logs:\n"
    try:
        parsed_logs = []
        for log in logs:
            if isinstance(log, dict) and 'date' in log:
                try:
                    log['date_obj'] = datetime.fromisoformat(log['date'].replace('Z', '+00:00'))
                    parsed_logs.append(log)
                except ValueError:
                    print(f"Could not parse date: {log.get('date')}")
        parsed_logs.sort(key=lambda x: x['date_obj'], reverse=True)
    except Exception as e:
        print(f"Error processing logs for sorting: {e}")
        parsed_logs = logs

    for log in parsed_logs:
        try:
            date_str = log['date_obj'].strftime('%Y-%m-%d') if 'date_obj' in log else log.get('date', 'N/A')
            quality = log.get('sleepQuality', 'N/A')
            bed_time = log.get('bedTime', 'N/A')
            wake_time = log.get('wakeTime', 'N/A')
            notes = log.get('notes', 'No notes.')
            formatted_string += f"- {date_str}: Bedtime={bed_time}, Waketime={wake_time}, Quality={quality}/5. Notes: {notes if notes else 'None'}\n"
        except Exception as e:
            print(f"Error formatting log entry: {log}, Error: {e}")
            formatted_string += f"- Error formatting log entry.\n"

    return formatted_string.strip()



@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat')
def chat_route():
    return render_template_string(CHAT_TEMPLATE)

@app.route('/sleep-log')
def sleep_log():
    return render_template_string(SLEEP_LOG_TEMPLATE)

@app.route('/ask', methods=['POST'])
def ask_question():
    global chat_session

    if not model or not chat_session:
        return jsonify({'response': 'Sorry, the AI model is not available. Please check if the GOOGLE_API_KEY is set.'}), 503

    try:
        data = request.get_json()
        user_message = data.get('message')
        sleep_logs_from_frontend = data.get('logs', [])

        if not user_message:
            return jsonify({'error': 'No message provided.'}), 400

        log_context = format_sleep_logs_for_ai(sleep_logs_from_frontend)
        prompt = f"Context:\n{log_context}\n\nUser Question:\n{user_message}"
        response = chat_session.send_message(prompt)

        return jsonify({'response': response.text}), 200

    except Exception as e:
        print(f"Error during AI processing or sending message: {str(e)}")
        return jsonify({'response': f"Sorry, I encountered an error: {str(e)}"}), 500

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'status': 'ok', 'message': 'API is working properly'}), 200


if __name__ == '__main__':
    if not os.environ.get("GOOGLE_API_KEY"):
        print("\n" + "="*80)
        print("WARNING: GOOGLE_API_KEY environment variable is not set!")
        print("The AI chat features require this key to function.")
        print("="*80 + "\n")

    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    print(f"Starting Flask app on http://localhost:{port} with debug mode {'on' if debug_mode else 'off'}...")
    app.run(debug=debug_mode, host='0.0.0.0', port=port)


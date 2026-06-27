document.addEventListener('DOMContentLoaded', () => {
    
    // UI Elements
    const body = document.getElementById('body-container');
    const behaviorStatus = document.getElementById('behavior-status');
    const statusSubtitle = document.getElementById('status-subtitle');
    const poseScore = document.getElementById('pose-score');
    const audioScore = document.getElementById('audio-score');
    const poseBar = document.getElementById('pose-bar');
    const audioBar = document.getElementById('audio-bar');
    const actionLogs = document.getElementById('action-logs');

    let isCurrentlyAggressive = false;

    function formatTime(date) {
        return date.toLocaleTimeString([], { hour12: false });
    }

    function addLog(message, isAlert=false) {
        const li = document.createElement('li');
        if (isAlert) li.className = 'alert-log';
        li.innerHTML = `<span class="log-time">${formatTime(new Date())}</span> ${message}`;
        actionLogs.prepend(li); // add to top
        
        // keep only latest 5 logs
        if (actionLogs.children.length > 5) {
            actionLogs.removeChild(actionLogs.lastChild);
        }
    }

    async function fetchStatus() {
        try {
            const response = await fetch('/status');
            const data = await response.json();

            // Handle Scores & Progress bars
            // Pose score is heuristic based, we cap it at 1.0 for UI purposes ideally
            const pVal = Math.min(data.pose_score, 1.0);
            poseScore.textContent = data.pose_score.toFixed(2);
            poseBar.style.width = `${(pVal / 1.0) * 100}%`;

            const aVal = Math.min(data.audio_vol, 1.0);
            audioScore.textContent = data.audio_vol.toFixed(2);
            audioBar.style.width = `${(aVal / 0.3) * 100}%`; // 0.3 is roughly max loud talking

            // State Machine Transition
            if (data.is_aggressive && !isCurrentlyAggressive) {
                // Just turned aggressive
                isCurrentlyAggressive = true;
                body.classList.remove('normal-state');
                body.classList.add('aggressive-state');
                behaviorStatus.textContent = "AGGRESSIVE DETECTED";
                statusSubtitle.textContent = "Caution! Behavioral anomalies triggered.";
                addLog("Aggressive action detected! Triggering SMS...", true);
                
            } else if (!data.is_aggressive && isCurrentlyAggressive) {
                // Just turned normal
                isCurrentlyAggressive = false;
                body.classList.remove('aggressive-state');
                body.classList.add('normal-state');
                behaviorStatus.textContent = "NORMAL";
                statusSubtitle.textContent = "Monitoring environment safely.";
                addLog("Situation normalized.");
            }

        } catch (error) {
            console.error("Failed to fetch camera status:", error);
        }
    }

    // Poll the backend 3 times a second
    setInterval(fetchStatus, 333);
});

import { load } from './fingerprint.js';

document.addEventListener("DOMContentLoaded", async () => {
  const userstatusDisplay = document.getElementById('userstatus');
  const videoidDisplay = document.getElementById('videoid');
  const reportstatusDisplay = document.getElementById('reportstatus');
  const openSiteBtn = document.getElementById('openSite');
  const outputDiv = document.getElementById("output");
  const API_URL = 'http://127.0.0.1:8000';
  // const API_URL = 'http://satya-auto-scaling-group-elb-2037468619.ap-south-1.elb.amazonaws.com:80';

  // Reload the extension popup
  document.getElementById("reloadExt").addEventListener("click", () => {
    location.reload(); 
  });
  
  // Close the extension popup
  document.getElementById("closeExt").addEventListener("click", () => {
    window.close(); 
  });
  
  // Open site in full Chrome tab
  openSiteBtn.addEventListener('click', () => {
    chrome.tabs.create({ url: 'https://www.thesoftmax.com' });
  });
  
  // Generate deviceID using fingerprintJS
  async function getDeviceId() {
      try {
          const fpPromise = load({
              token: 'WiLe8qnlR2HdOoQiX4A4'
          });
          
          const fp = await fpPromise;
          const result = await fp.get();
          
          return result.visitorId;
      } catch (error) {
          console.log("Failed to generate Device ID:", error);
          return null;
      }
  }

  // Copy Video ID to clipboard on click
  videoidDisplay.style.cursor = "pointer"; // show it's clickable
  videoidDisplay.addEventListener("click", () => {
    const textToCopy = videoidDisplay.textContent.replace("Video ID ", "").trim();
    
    navigator.clipboard.writeText(textToCopy).then(() => {
      videoidDisplay.textContent = "Copied !";
      setTimeout(() => {
        videoidDisplay.innerHTML = `Video ID <span style="color: #0099ff; font-weight: bold; text-decoration: underline;">${textToCopy}</span>`;
      }, 1200);
    });
  });

  // redirect to user profile
  userstatusDisplay.style.cursor = "pointer";
  userstatusDisplay.addEventListener("click", () => {
    chrome.tabs.create({ url: `${API_URL}/user/` });
  });

  // Fetch cookies from the domain localhost:8000
  chrome.cookies.getAll({ url: API_URL }, async function(cookies) {

    // if no cookies found
    if (cookies.length === 0) {
        userstatusDisplay.innerHTML = `<img title="Log In" src="icons/user.svg" width="30" height="30">`;
        videoidDisplay.innerHTML = `Please login`;
        return;
    };

    try {
        const response = await fetch(`${API_URL}/api/health`, { // Fetch login status
            method: "GET",
            credentials: "include", // Include cookies with this request, even if the request is to another origin.
        });

        if (!response.ok) { // Handling the server’s response. Checks if HTTP response was OK (status 200–299). Converts the response into JSON safely. Throws an error if it wasn’t OK.
          console.log("Unable to fetch login status")
          throw new Error("HTTP " + response.status);
        }

        // convert response to JSON
        const data = await response.json().catch(() => ({}));

        // Using the login data. If the /api/health endpoint returns { logged_in: true }, the popup shows "Logged In". Otherwise, "Logged Out".
        if (data && data.logged_in) {
             userstatusDisplay.innerHTML = `<img title="Manage Profile" src="icons/user.svg" width="30" height="30">`;
        } else {
             userstatusDisplay.innerHTML = `<img title="Log In" src="icons/user.svg" width="30" height="30">`;
             videoidDisplay.innerHTML = `Please login`;
             return;
        }

    // Handling any network or fetch errors. Handles issues like: Server unreachable, Network failure, Invalid JSON. Displays "Logged Out" as a fallback.
    } catch (err) {
        userstatusDisplay.innerHTML = `<img title="Log In" src="icons/user.svg" width="30" height="30">`;
        videoidDisplay.innerHTML = `Something went wrong. Please try again later.`;
        return;
    }

    chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
      const url = tabs[0].url; // Get the current tab's URL
      const youtubeRegex = /^https:\/\/(?:www\.)?youtube\.com\/watch\?v=([\w-]{11})/;
      const match = url.match(youtubeRegex);

      // Check if the URL is a valid YouTube video URL
      if (match && match[1]) {
        const videoId = match[1];
        videoidDisplay.innerHTML = `Video ID <span style="color: #0099ff; font-weight: bold; text-decoration: underline;">${videoId}</span>`;
        reportstatusDisplay.innerHTML = `Analyzing video...`;

        // Fetch comments from the YouTube API and make sentiment predictions
        const analyzedData = await fetchAnalyzedData(videoId);
        if (!analyzedData || analyzedData.length === 0) {
            reportstatusDisplay.innerHTML = "No comments found or analysis failed.";
            return;
        }

        // Prepare data for Word Cloud (Array of comment strings)
        const rawCommentsForWordCloud = analyzedData.map(item => item.Original_Comment);

        // Prepare data for Trend Graph (Array of objects with timestamp & sentiment)
        const sentimentData = analyzedData.map(item => ({
            timestamp: item.timestamp,
            sentiment: parseInt(item.sentiment)
        }));

        // Prepare data for Pie Chart (Count of each sentiment)
        const sentimentCounts = { "1": 0, "0": 0, "-1": 0 };
        analyzedData.forEach(item => {
            const key = String(item.sentiment); 
            if (sentimentCounts[key] !== undefined) {
                sentimentCounts[key]++;
            }
        });

        // Calculate summary metrics
        const totalComments = analyzedData.length;
        const uniqueCommenters = new Set(analyzedData.map(item => item.AuthorID)).size;
        const totalSentimentScore = analyzedData.reduce((sum, item) => sum + parseInt(item.sentiment), 0);
        const totalWords = analyzedData.reduce((sum, item) => sum + item.Original_Comment.split(/\s+/).filter(word => word.length > 0).length, 0);
        const avgWordLength = (totalWords / totalComments).toFixed(2);
        const avgSentimentScore = (totalSentimentScore / totalComments).toFixed(2);
        const normalizedSentimentScore = (((parseFloat(avgSentimentScore) + 1) / 2) * 10).toFixed(2); // Normalize the average sentiment score to a scale of 0 to 10

        // Add the Comment Analysis Summary section
        outputDiv.innerHTML += `
          <div class="section">
            <div class="section-title">Sentiment Analysis Summary</div>
            <div class="metrics-container">
              <div class="metric">
                <div class="metric-title">Total Comments</div>
                <div class="metric-value">${totalComments}</div>
              </div>
              <div class="metric">
                <div class="metric-title">Unique Commenters</div>
                <div class="metric-value">${uniqueCommenters}</div>
              </div>
              <div class="metric">
                <div class="metric-title">Avg Comment Length</div>
                <div class="metric-value">${avgWordLength} words</div>
              </div>
              <div class="metric">
                <div class="metric-title">Avg Sentiment Score</div>
                <div class="metric-value">${normalizedSentimentScore}/10</div>
              </div>
            </div>
          </div>`;

        // Add the Sentiment Analysis Results section with a placeholder for the chart
        outputDiv.innerHTML += `
          <div class="section">
            <div id="chart-container"></div>
          </div>`;

        // Display the pie chart
        await fetchAndDisplayChart(sentimentCounts);

        // Display the Sentiment Trend Graph
        outputDiv.innerHTML += `
          <div class="section">
            <div class="section-title">Sentiment Trend Over Time</div>
            <div id="trend-graph-container"></div>
          </div>`;
        await fetchAndDisplayTrendGraph(sentimentData);

        // Display the Word Cloud
        outputDiv.innerHTML += `
          <div class="section">
            <div class="section-title">Comment Wordcloud</div>
            <div id="wordcloud-container"></div>
          </div>`;
        await fetchAndDisplayWordCloud(rawCommentsForWordCloud);

        // Display the top comments
        outputDiv.innerHTML += `
          <div class="section">
            <div class="section-title">Top 25 Comments with Sentiments</div>
            <ul class="comment-list">
              ${analyzedData.slice(0, 25).map((item, index) => `
                <li class="comment-item">
                  <span>${index + 1}. ${item.Original_Comment}</span><br>
                  <span class="comment-sentiment">Sentiment: ${item.sentiment}</span>
                </li>`).join('')}
            </ul>
          </div>`;

      } else {
        reportstatusDisplay.innerHTML = "This is not a valid YouTube URL.";
      }
    });

    // Fetch the comments and predictions
    async function fetchAnalyzedData(videoId) {
      try {
        // We don't need to generate deviceId here because the server handles logic
        // But if your /api/analyze_video endpoint requires it for credit deduction, include it.
        // Based on your previous app.py, analyze_video only checked for login, not deviceId.
        const device_id = await getDeviceId();
        const response = await fetch(`${API_URL}/api/analyze_video`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ videoId: videoId, visitorId : device_id }),
          credentials: "include" // IMPORTANT: Sends the session cookies
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Server error');
        }

        return await response.json(); // Returns the list of analyzed comments
      } catch (error) {
        console.log("Error fetching analyzed data:", error);
        return null;
      }
    }

    // Display the Pie chart
    async function fetchAndDisplayChart(sentimentCounts) {
      try {
        const response = await fetch(`${API_URL}/api/generate_chart`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ sentiment_counts: sentimentCounts }),
          credentials: "include"
        });
        if (!response.ok) {
          throw new Error('Failed to fetch chart image');
        }
        const blob = await response.blob();
        const imgURL = URL.createObjectURL(blob);
        const img = document.createElement('img');
        img.src = imgURL;
        img.style.width = '100%';
        img.style.marginTop = '20px';
        // Append the image to the chart-container div
        const chartContainer = document.getElementById('chart-container');
        chartContainer.appendChild(img);
      } catch (error) {
        outputDiv.innerHTML += "<p>Error fetching chart image.</p>";
      }
    }

    // Display the word cloud
    async function fetchAndDisplayWordCloud(comments) {
      try {
        const response = await fetch(`${API_URL}/api/generate_wordcloud`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ comments }),
          credentials: "include"
        });
        if (!response.ok) {
          throw new Error('Failed to fetch word cloud image');
        }
        const blob = await response.blob();
        const imgURL = URL.createObjectURL(blob);
        const img = document.createElement('img');
        img.src = imgURL;
        img.style.width = '100%';
        img.style.marginTop = '20px';
        // Append the image to the wordcloud-container div
        const wordcloudContainer = document.getElementById('wordcloud-container');
        wordcloudContainer.appendChild(img);
      } catch (error) {
        outputDiv.innerHTML += "<p>Error fetching word cloud image.</p>";
      }
    }

    // Display the sentiment trend graph
    async function fetchAndDisplayTrendGraph(sentimentData) {
      try {
        const response = await fetch(`${API_URL}/api/generate_trend_graph`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ sentiment_data: sentimentData }),
          credentials: "include"
        });
        if (!response.ok) {
          throw new Error('Failed to fetch trend graph image');
        }
        const blob = await response.blob();
        const imgURL = URL.createObjectURL(blob);
        const img = document.createElement('img');
        img.src = imgURL;
        img.style.width = '100%';
        img.style.marginTop = '20px';
        // Append the image to the trend-graph-container div
        const trendGraphContainer = document.getElementById('trend-graph-container');
        trendGraphContainer.appendChild(img);
      } catch (error) {
        outputDiv.innerHTML += "<p>Error fetching trend graph image.</p>";
      }
    }
  });
});
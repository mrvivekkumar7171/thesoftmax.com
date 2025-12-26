# TheSoftmax.com – AI/ML/DS Educational Blog & Resume Site

Welcome to **TheSoftmax.com**, a personal website built to showcase my resume and regularly post educational content on Artificial Intelligence (AI), Machine Learning (ML), and Data Science (DS). This project is designed to help students, beginners, and enthusiasts learn through well-structured blog posts, practical examples, and curated resources.

## 🌐 Website Structure

The website contains the following major components:

- **Homepage (index.html)** – Introduction to the website and latest blog updates.
- **Resume Page (Vivek-Kumar.html)** – A detailed, stylized HTML version of my resume.
- **Post Page (post.html)** – A list of individual blog posts with titles, thumbnails, reading times, and like counts.
- **Individual Blog Pages** – Each post includes a full article with visuals, estimated reading time, publication date, and interactive like functionality.
- **Minimal Music Player** – A clean, minimal, and modern **web-based music player** that plays audio across **Hindi, English, and regional languages** — capturing a wide spectrum of **moods and emotions**. Built for those who love music without distractions.

### 🌟 Features of Music Player

- 🎶 **Multi-language tracks** – Hindi, English, and more  
- 💫 **Emotion-based variety** – love, energy, calm, and more  
- 🎧 **No visuals, just sound** – low data usage  
- 🌓 **Dark mode only** – clean, night-friendly interface  
- ⏯️ **Core music controls** – Play, Pause, Next, Previous  
- 🔀 **Shuffle & 🔁 Repeat** – toggle with smart feedback  
- ⌨️ **Keyboard shortcuts** – control volume & seek without mouse  
- 🔊 **Volume memory** – remembers your sound preference  
- ⚡ **Lightweight** – fast, responsive, and clutter-free  

## 📂 Tech Stack

- **Frontend**: HTML5, CSS3 (Dark-themed), JavaScript
- **Hosting**: GitHub Pages
- **Domain**: [TheSoftmax.com](https://thesoftmax.com) via Hostinger
- **Deployment**: Manual deployment using Git and GitHub Pages

## 🚀 Getting Started

If you want to run this website locally:

```bash
git clone https://github.com/yourusername/thesoftmax.git
cd thesoftmax
# Open index.html in your browser
```

Or, just open the `index.html` file directly in your browser.

## 🧠 Features

- Clean and responsive layout for all devices.
- Like counter on each post using local storage (no backend).
- Structured format for educational blog posts.
- Resume formatted in a professional and stylized way.
- Fully static—easy to host and manage.

## 🌍 Custom Domain Setup with Hostinger

To connect your GitHub Pages website with a custom domain purchased from Hostinger, follow these steps:

### Step 1: Configure DNS in Hostinger

1. Go to your Hostinger account and open the **DNS Zone Editor** for your domain.
2. Add or edit the following DNS records:

| Type | Name     | Value                         |
|------|----------|-------------------------------|
| A    | @        | `185.199.108.153`             |
| A    | @        | `185.199.109.153`             |
| A    | @        | `185.199.110.153`             |
| A    | @        | `185.199.111.153`             |
| CNAME | www    | `yourusername.github.io`       |

> Replace `yourusername.github.io` with your GitHub Pages username URL.

### Step 2: Add a CNAME File to GitHub

1. Inside your GitHub repository root, create a file named `CNAME`.
2. Add only your domain name (without `https://`) inside the file, for example:

```
thesoftmax.com
```

3. Commit and push this to your GitHub repo:

```bash
git add CNAME
git commit -m "Added custom domain"
git push
```

### Step 3: Enable GitHub Pages

1. Go to your GitHub repository > **Settings** > **Pages**.
2. Under "Custom domain", enter `thesoftmax.com`.
3. Check the "Enforce HTTPS" option once the domain connects properly.

Your domain should now point to your GitHub Pages website!

## 📸 Screenshots

*(Optional: Add screenshots of your website homepage, resume page, and a sample blog post.)*
![alt text](assets/images/readme/thesoftmax.png)
![alt text](assets/images/readme/post.png)
![alt text](assets/images/readme/Vivek-Kumar-html.png)

## 📫 Contact

Feel free to connect with me on [LinkedIn](https://www.linkedin.com/in/Vivek-Kumar7171/) or check out more on [TheSoftmax.com](https://thesoftmax.com).


# Comprehensive AI, Deep Learning & ML Model Deployment Platform

## Overview
- It offers two roles User & Admin.
- User Management (Ban/Approve users, search users)
- User Signup & Login via Google auth. Thus no user password is stored in the database.
- User dashoard that list all models and their uses. It also contain logout button. Donation via UPI QR code.
- Model page that implement the model prediction api call and show the result in nice format.
- Admin Signup & Login via username, Password, OTP on Email Link and 2FA OTP.
- Admin Dashboard to manage users, models, payments, logout. Admin can also test the model prediction. Password Reset for admin and otp via email
- API (model) access only with devicefingerprint confirm device id is same as login time.
- Real-Time Notifications in app notification, Email notification.
- Payment Gateway: Secure online transactions using Razorpay to get credits which is used to access the ML model prediction api and Confirmation via Email.
- Responsive Design: Optimized for both mobile and desktop.
- api return json (done earlier) while website render html pages (the pages communicate via api and send and receive json).
- CSRF (Cross-Site Request Forgery) prevents a malicious site from tricking a logged-in user into performing actions (like submitting a form or making a POST request) on another site without their consent. CSRF is needed only for routes that perform sensitive actions like modifing data(user registration, payments, profile updates, etc.). ML prediction endpoint is like a read-only inference API thus Safe to exempt from CSRF protection.
- user login is managed using cookies and Session. The real session data is stored on your server’s filesystem (using Flask-Session with 'filesystem' type inside flask_session/), Redis, DB, etc. When a user makes a request, Flask looks up this ID in the session folder and retrieves their stored data (user_id, name, etc.). That’s secure — as long as your SECRET_KEY is private and you’re using HTTPS.

## Further Improvement :
-   rewrite all the functions docstring and data type hint etc. and make it the more moduler the possible.
-   delete account option for user.
-   Feedback Analytics Dashboard (Trends, Average Star ratings, comments, Thums up and thums down feedback).
-   System Analytics (Revenue, model uses Reports).
-   AI Chatbot: NLP-integrated chatbot for instant attendee queries.
-   Export reports (Daily/Weekly/Post-Event/On-Demand) in Excel, PDF, CSV, or PDF with Graphs/Charts (PNG).
-   google ads integration for revenue.
-   Sign Language Avatars: AI-generated interpreters for hearing-impaired attendees.
-   Multi-language Support: Real-time translation for event descriptions and chats.
-   WCAG 2.2 Compliance: Enhanced accessibility for visually impaired users.
-   Cloud Hosting: Scalable backend deployment via AWS (EC2, S3)
-   Database Hosting: Managed database solutions via MongoDB Atlas, AWS RDS, PlanetScale.







# **PROJECT 1** : Youtube Comment Sentiment Analysis

## **Business Problem**:

1. **Identifying the Influencer Pain Point**:
    - Influencers, especially those with large followings, struggle with managing and interpreting the vast amount of feedback they receive via comments on their content.

2. **Big Influencers Face Issues with Comment Analysis**:
    - High-profile influencers receive thousands of comments on their videos, making manual analysis impractical.
    - Influencers often lack the time to sift through comments to extract meaningful insights.
    - Without efficient comment analysis, influencers miss opportunities to understand audience sentiment, address concerns, and tailor their content effectively.

3. **Find out biasness in videos for viewers**:
    - Some videos may have biased comments due to various reasons like paid promotions, fake accounts, etc. Influencers need to identify such biases to maintain authenticity.
    - Some video may be biased for certain group of people like political videos, product review videos etc. so viewers need to know the biasness in video.

## **Our Solution**: 

To directly address the significant pain point faced by big influencers—managing and interpreting vast amounts of comment data—we present the "Satya" webpage & Chrome plugin. This tool is designed to empower influencers by providing in-depth analysis of their YouTube video comments, helping them make data-driven decisions to enhance their content and engagement strategies.

## **Key Features**:

1. **Sentiment Analysis of Comments**:
- **Real-Time Sentiment Classification**:
    - The plugin performs real-time analysis of all comments on a YouTube video, classifying each as positive, neutral, or negative.
- **Sentiment Distribution Visualization**:
    - Displays the overall sentiment distribution with intuitive graphs or charts (e.g., pie charts or bar graphs showing percentages like 70% positive, 20% neutral, 10% negative). Mark positive comment as green and negative comment  as negative.
- **Detailed Sentiment Insights**:
    - Allows users to drill down into each sentiment category to read specific comments classified under it. Average comment length, Top liked comment
- **Trend Tracking**:
    - Monitors how sentiment changes over time, helping influencers identify how different content affects audience perception by plotting positive, negative and neutral comment on each day in time series.

2. **Summary of Comments**
- **Automated Comment Summarization**:
    - Utilizes natural language processing algorithms to generate concise summaries of the most discussed topics within the comments.
- **Highlight Key Themes**:
    - Identifies and summarizes common feedback, suggestions, or concerns raised by the audience.

3. **Additional Comment Analysis Features**
- **Word Cloud Visualization**:
    - Generates a word cloud showcasing the most frequently used words and phrases in the comments.
    - Helps quickly identify trending topics, keywords, or recurring themes.
- **Average Comment Length**:
    - Calculates and displays the average length of comments, indicating the depth of audience engagement.
- **Spam and Troll Detection**:
    - Filters out spam, bot-generated comments, or potentially harmful content to streamline the analysis.
- **Export Data Functionality**:
    - Enables users to export analysis reports, data and visualizations in various formats (e.g., PDF, Excel, CSV) for further use or sharing with team members.
- **Analysis for whole channel**: Time consuming and take high computation.
- **Summary of whole comments**: summary of all comments on the video using AI or LLM API call.
- **label**: Feedback, suggestions, spam or concerns label on each comment. Search by the label like user wants to select top feedbacks etc. and filter by sentiments, it will show the respective comments (top negative comments when clicked on negative comments).

### Steps to obtain a YouTube Data API Key:

- **Visit https**: //console.cloud.google.com/
- **Create a Project**: Select a Project dropdown > New Project > name the project ("TheSoftMax.com") > Create
- **Enable YouTube Data API v3**: In left sidebar > APIs & Services > Library > Search for YouTube Data API v3 > click on it > Enable
- **Generate an API Key**: APIs & Services > Credentials > Create Credentials > API Key > Copy the key
- **Important Links** :
    
    https://console.cloud.google.com/home/dashboard?invt=AbtPTg&project=the-softmax
    
    https://developers.google.com/people/api/rest/v1/people/get
    
    https://console.cloud.google.com/apis/credentials?project=the-softmax
    
    https://developer.chrome.com/docs/extensions/reference/api/identity#method-launchWebAuthFlow
    
    https://developers.google.com/identity/openid-connect/openid-connect#python
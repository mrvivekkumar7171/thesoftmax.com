# TheSoftmax.com

Welcome to **TheSoftmax.com**, the website contains a **Minimal Music Player** – A clean, minimal, and modern **web-based music player** that plays audio across **Hindi, English, and regional languages** — capturing a wide spectrum of **moods and emotions**. Built for those who love music without distractions.

## 🌟 Features of Music Player

- 🎶 **Multi-language tracks** – Hindi, English, and more  
- 💫 **Emotion-based variety** – love, energy, calm, and more  
- 🎧 **No visuals, just sound** – low data usage  
- 🌓 **Dark mode only** – clean, night-friendly interface  
- ⏯️ **Core music controls** – Play, Pause, Next, Previous  
- 🔀 **Shuffle & 🔁 Repeat** – toggle with smart feedback  
- ⌨️ **Keyboard shortcuts** – control volume & seek without mouse  
- 🔊 **Volume memory** – remembers your sound preference  
- ⚡ **Lightweight** – fast, responsive, and clutter-free  

## Further Improvement :
-   rewrite all the functions docstring and data type hint etc. and make it the more moduler the possible.
-   Feedback Analytics Dashboard (Trends, Average Star ratings, comments, Thums up and thums down feedback).
-   Export reports (Daily/Weekly/Post-Event/On-Demand) in Excel, PDF, CSV, or PDF with Graphs/Charts (PNG).
-   google ads integration for revenue.
-   WCAG 2.2 Compliance: Enhanced accessibility for visually impaired users.

---

## Custom Domain Setup with Hostinger
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

```text
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
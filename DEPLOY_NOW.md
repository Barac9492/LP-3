# 🚀 Deploy Your Dashboard in 5 Minutes

## Quick Deploy to Streamlit Cloud (FREE)

### Step 1: Go to Streamlit Cloud
👉 **https://share.streamlit.io/**

### Step 2: Sign Up / Log In
- Click **"Sign up"** or **"Log in"**
- Use your **GitHub account**

### Step 3: Create New App
1. Click **"New app"** button (top right)
2. Fill in the form:

   ```
   Repository: Barac9492/LP-3
   Branch: claude/lp-monitoring-system-015a9ntaNG2haZ5RopbzLKQB
   Main file path: dashboard.py
   ```

3. **(Optional)** Custom URL: `lp-investment-monitor`
4. Click **"Deploy!"**

### Step 4: Wait 2-3 Minutes
Watch the deployment progress:
- ⏳ Installing dependencies...
- ⏳ Building app...
- ✅ **Your app is live!**

### Step 5: Access Your Dashboard
Your dashboard will be live at:
```
https://[your-app-name].streamlit.app
```

**That's it! 🎉**

---

## 📸 Visual Guide

### 1. Streamlit Cloud Homepage
![Streamlit Cloud](https://docs.streamlit.io/images/streamlit-community-cloud/deploy-an-app-part-1.png)

### 2. Deploy Form
Fill in:
- **Repository:** `Barac9492/LP-3`
- **Branch:** `claude/lp-monitoring-system-015a9ntaNG2haZ5RopbzLKQB`
- **Main file:** `dashboard.py`

### 3. Deployment in Progress
Wait for the build to complete (usually 2-3 minutes)

### 4. Live Dashboard
Your dashboard is now accessible worldwide! 🌍

---

## 🔐 Optional: Add API Keys

If you want AI-powered analysis in production:

1. Click on your app in Streamlit Cloud
2. Go to **"Settings"** → **"Secrets"**
3. Paste this (with your real keys):

```toml
OPENAI_API_KEY = "sk-your-actual-key-here"
```

4. Click **"Save"**

The app will automatically restart with the new keys.

---

## ✅ What You Get

- ✅ **Free hosting** (no credit card needed)
- ✅ **HTTPS** included
- ✅ **Auto-deploy** on git push
- ✅ **Global access** (anyone with URL can view)
- ✅ **Always on** (24/7 availability)

---

## 🎯 Next Steps After Deployment

1. **Share the URL** with your team
2. **Populate with real data:**
   ```bash
   python main.py --mode instant --days 7 --no-ai
   ```
   (Run this locally, data syncs if using cloud database)

3. **Set up auto-collection** (optional):
   ```bash
   python scheduler.py
   ```

4. **Add password protection** (see DEPLOYMENT.md)

---

## 🆘 Troubleshooting

### "Repository not found"
- Make sure you've pushed your code to GitHub
- Check repository permissions

### "Build failed"
- Check the build logs for errors
- Usually missing dependencies or Python version issues

### "App won't load"
- Click "Reboot app" in Streamlit Cloud
- Check logs for runtime errors

### Need Help?
- See full guide: `DEPLOYMENT.md`
- Streamlit docs: https://docs.streamlit.io/streamlit-community-cloud

---

## 🎊 You're Done!

Your LP Investment Monitoring Dashboard is now:
- 🌐 **Live on the web**
- 📊 **Accessible from anywhere**
- 🔄 **Auto-updating with new commits**
- 💯 **100% FREE**

**Your Dashboard URL:**
```
https://[your-chosen-name].streamlit.app
```

Share it with your team and start monitoring LP investments! 🚀

---

**Need more advanced deployment?** See `DEPLOYMENT.md` for:
- Docker deployment
- Alternative platforms (Railway, Render)
- Custom domain setup
- Production scaling

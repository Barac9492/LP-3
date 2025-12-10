# LP Monitoring Dashboard Guide

## 🚀 Quick Start

### Launch the Dashboard

**Linux/Mac:**
```bash
./run_dashboard.sh
```

**Windows:**
```bash
run_dashboard.bat
```

**Or manually:**
```bash
streamlit run dashboard.py
```

The dashboard will open automatically in your browser at: **http://localhost:8501**

## 📊 Dashboard Pages

### 1. 🏠 Overview
The main landing page showing:
- **Key Metrics**
  - Total news count (last 7 days)
  - High relevance signals (score 4-5)
  - Number of active LPs
  - News categories

- **Visual Highlights**
  - High-relevance signals
  - LP activity overview

### 2. 📰 News Feed
Browse and filter all collected news:
- **Filters:**
  - Time period (1, 3, 7, 14, 30 days)
  - Minimum relevance score (1-5)
  - Filter by LP institution

- **For each news item:**
  - Title and LP name
  - Korea relevance score (⭐ stars)
  - Date and category
  - Summary
  - Key points (expandable)
  - Link to original article

### 3. 🔥 High Signals
Focused view of high-relevance news (score 4-5):
- Top Korean-related investment signals
- Investment amounts
- Target sectors
- Direct links to articles

**Perfect for daily priority check!**

### 4. 🏢 LP Activity
Comprehensive LP analytics:

**Charts:**
- Bar chart: News count by LP
- Pie chart: News distribution
- Color-coded by average relevance score

**Data Table:**
- Total news count per LP
- High-score signals (4-5)
- Average relevance score

### 5. 📂 Categories
News breakdown by category:
- 신규_출자_약정 (New Commitments)
- 전략_변화 (Strategy Changes)
- 인사_변동 (Personnel Changes)
- 성과_발표 (Performance Reports)
- 한국_관련 (Korea-related)
- 일반_소식 (General News)

**Interactive bar chart** showing distribution

### 6. 🏦 LP Profiles
Detailed information about each LP:
- Full name and country
- Assets Under Management (AUM)
- PE allocation percentage
- Focus regions
- Korea interest level
- Website
- Search keywords used

### 7. ⚡ Actions
Control panel for manual operations:

**🔍 Collect News Now**
- Triggers immediate news collection
- Collects last 3 days of news
- Uses fast mode (no AI analysis)
- Auto-refreshes dashboard on completion

**📄 Generate Weekly Report**
- Creates comprehensive weekly report
- Downloads as Markdown file
- Includes all analysis and insights

**📊 Generate Monthly Report**
- Creates detailed monthly analytics
- Trend analysis and LP rankings
- Downloads as Markdown file

## 🎨 Dashboard Features

### Real-time Data
- All data pulled from SQLite database
- Updates automatically after news collection
- Manual refresh: Click on sidebar navigation

### Interactive Charts
- Hover for detailed information
- Zoom and pan on charts
- Click legend to filter data

### Color Coding
- 🟨 Yellow background: High relevance (score 4-5)
- 🔵 Blue borders: Standard news items
- Color gradients: Based on relevance scores

### Responsive Design
- Works on desktop and tablet
- Auto-adjusts to screen size
- Mobile-friendly interface

## 📝 Usage Tips

### Daily Workflow
1. **Check Overview** - See today's stats
2. **Review High Signals** - Priority check (score 4-5)
3. **Browse News Feed** - Filter by your target LPs
4. **Generate Report** - Weekly summary for team

### Weekly Workflow
1. **LP Activity** - Which LPs are most active?
2. **Categories** - What types of news trending?
3. **Generate Weekly Report** - Download for sharing
4. **Actions** - Collect fresh news

### Research Workflow
1. **LP Profiles** - Study target institutions
2. **News Feed** - Filter by specific LP
3. **High Signals** - Focus on top opportunities

## 🔄 Data Management

### Collecting New News
1. Go to **⚡ Actions** page
2. Click **🔍 Collect News Now**
3. Wait 1-3 minutes for collection
4. Dashboard auto-refreshes

### Viewing Different Time Periods
- Most pages have time period selector
- Options: 1, 3, 7, 14, 30 days
- Adjust based on your needs

### Filtering by LP
- Use multi-select dropdown in News Feed
- Select "All" or specific LPs
- Combine with other filters

## 🎯 Best Practices

### For Daily Monitoring
- Set **High Signals** as your homepage
- Check score 5 items first
- Review Asia-focused news (score 4)

### For Reporting
- Use **Weekly Report** generation
- Export data from charts (right-click)
- Take screenshots of key charts

### For Research
- Start with **LP Profiles**
- Filter **News Feed** by target LP
- Look at 30-day trends in **LP Activity**

## 🛠️ Troubleshooting

### Dashboard Won't Start
```bash
# Install dependencies
pip install streamlit plotly

# Try manual launch
streamlit run dashboard.py
```

### No Data Showing
```bash
# Create demo data
python create_demo_data.py

# Or collect real news
python main.py --mode instant --days 7 --no-ai
```

### Port Already in Use
```bash
# Use different port
streamlit run dashboard.py --server.port 8502
```

### Browser Doesn't Open
- Manually navigate to: http://localhost:8501
- Check firewall settings
- Try different browser

## 📱 Access from Other Devices

### On Same Network
1. Find your computer's IP address
2. Use Network URL shown in terminal
3. Example: http://192.168.1.100:8501

### For Remote Access
- Consider using ngrok or similar
- Or deploy to Streamlit Cloud (free)
- See deployment guide in main README

## ⚙️ Customization

### Change Port
```bash
streamlit run dashboard.py --server.port 8080
```

### Disable Usage Stats
Create `.streamlit/config.toml`:
```toml
[browser]
gatherUsageStats = false
```

### Change Theme
```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

## 📊 Data Sources

All data comes from:
- `data/news_archive.db` - SQLite database
- Populated by `main.py` news collection
- Updated by scheduler (if running)

To populate with real data:
```bash
# Collect news for all tier 1 LPs
python main.py --mode instant --days 7

# Or specific LPs
python main.py --mode instant --days 7 --lps GIC Temasek NPS
```

## 🚀 Next Steps

1. **Populate Real Data**
   ```bash
   python main.py --mode instant --days 7 --no-ai
   ```

2. **Set Up Scheduler** (optional)
   ```bash
   python scheduler.py
   ```

3. **Customize LP List**
   - Edit `data/lp_entities.json`
   - Add more institutions

4. **Share Dashboard**
   - Deploy to Streamlit Cloud
   - Or use port forwarding

## 📞 Support

For issues or questions:
- Check logs: `logs/lp_monitor.log`
- Review main README.md
- See QUICKSTART.md for setup help

---

**Dashboard Version**: 1.0.0
**Last Updated**: 2024-12-10

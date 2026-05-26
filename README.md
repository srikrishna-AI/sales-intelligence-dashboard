# 📊 Sales Intelligence Dashboard

A production-ready **Streamlit** application that replicates and enhances the Power BI Sales Report — powered by AI (Gemini) for natural language analytics.

---

## 🏗️ Architecture

```
sales_dashboard/
├── app.py                        # Main entry point, routing, global filters
├── pages/
│   ├── home.py                   # Landing page + summary KPIs
│   ├── executive.py              # Executive Overview & Trends
│   ├── product.py                # Product & Channel Performance
│   ├── geo.py                    # Geographic & Customer Insights
│   └── ai_insights.py           # AI-powered analytics + Q&A chatbot
├── components/
│   └── charts.py                 # Reusable Plotly chart components
├── utils/
│   ├── data_loader.py            # Data loading, cleaning, KPI calculations (DAX → Python)
│   └── styles.py                 # Custom CSS injection
├── data/
│   └── sales_data.csv            # Source dataset (2014–2018 US Sales)
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run locally
```bash
cd sales_dashboard
streamlit run app.py
```

### 3. Enable AI features (optional)
```bash
export GEMINI_API_KEY=your-gemini-api-key
streamlit run app.py
```

Or enter the key in the **AI Insights** page at runtime.

---

## 📋 Dashboard Pages

| Page | Power BI Equivalent | Charts |
|---|---|---|
| **Home** | Home Page | KPI strip, navigation cards |
| **Executive Overview & Trends** | Executive Overview & Trends | 5 KPI cards, monthly line charts, YoY comparison, order value histogram, price/margin scatter |
| **Product & Channel Performance** | Product & Channel Performance | Horizontal bar charts (revenue/margin), donut charts (channel), bubble scatter, heatmap |
| **Geographic & Customer Insights** | Geographic & Customer Insights | US bubble map, choropleth, state rankings, top/bottom customer bars, region donuts |
| **AI Insights** | *(enhancement)* | Executive summary, auto-insights, anomaly detection, NL Q&A chatbot |

---

## 🧮 DAX → Python Conversions

| DAX Measure | Python Equivalent |
|---|---|
| `Total Revenue = SUM(sales[revenue])` | `df["revenue"].sum()` |
| `Total Profit = SUM(sales[profit])` | `df["profit"].sum()` |
| `Profit Margin % = DIVIDE(Total Profit, Total Revenue) * 100` | `profit / revenue * 100` |
| `Total Orders = DISTINCTCOUNT(sales[order_number])` | `df["order_number"].nunique()` |
| `Revenue per order = DIVIDE(Total Revenue, Total Orders)` | `revenue / orders` |
| `Avg Profit Margin % = AVERAGE(sales[profit_margin_pct])` | `df["profit_margin_pct"].mean()` |

---

## 🤖 AI Features

All AI features are powered by **Gemini** through the Google Gen AI SDK:

- **Executive Summary** — Auto-generated business narrative from filtered KPIs
- **Auto Insights** — Revenue trends, geographic analysis, product portfolio, customer segmentation, growth forecast
- **Anomaly Detection** — Statistical z-score detection with AI explanation
- **Q&A Chatbot** — Multi-turn natural language questions about your data

---

## 🌐 Deployment

### Streamlit Cloud
1. Push to GitHub
2. Connect at [share.streamlit.io](https://share.streamlit.io)
3. Add `GEMINI_API_KEY` in Secrets

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```
```bash
docker build -t sales-dashboard .
docker run -p 8501:8501 -e GEMINI_API_KEY=your-gemini-api-key sales-dashboard
```

### AWS / Azure / GCP
Any container service (ECS, App Service, Cloud Run) works with the Docker image above.

---

## 🔐 Environment Variables

| Variable | Description | Required |
|---|---|---|
| `GEMINI_API_KEY` | Gemini API key for AI features | Optional |

---

## 📈 Improvements Over Power BI

| Feature | Power BI | Streamlit App |
|---|---|---|
| AI-generated insights | ❌ | ✅ Gemini-powered |
| NL Q&A chatbot | ❌ | ✅ Multi-turn |
| Anomaly detection | ❌ | ✅ Statistical z-score |
| YoY comparison chart | ❌ | ✅ Multi-year overlay |
| Customer scatter plot | ❌ | ✅ Revenue vs Margin |
| Channel heatmap | ❌ | ✅ Product × Channel |
| Custom CSS theme | Limited | ✅ Full dark mode |
| Open source | ❌ | ✅ |
| Free to deploy | ❌ (Pro license) | ✅ Streamlit Cloud |

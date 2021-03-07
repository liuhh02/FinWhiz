# FinWhiz
## Inspiration
Financial education is severely lacking among youths. According to a study by FINRA Investor Education Foundation, there is a **clear trend of declining financial literacy** with four in five youths failing a financial literacy quiz. This lack of financial knowledge further extends into adulthood, with 53% of adults being financially anxious.

At the same time, **women possess significantly lower rates of financial literacy than men**. Women are three times as likely as men to say they can’t afford to save for retirement and are three times more likely than men to quit their jobs to care for a family member. Despite this, women are still responsible for the same living expenses men pay. And since they live longer, they face additional costs, including more long-term and overall health care expenses. 

All these numbers point towards a need to increase financial literacy. In order to **empower users to make their own informed investment decisions**, we developed FinWhiz, a **data-first** fintech tool that helps to cut through the noise and hype (the GameStop saga as a quintessential example) and educate users about finance.

By providing **fundamental data** about the company as well as **real-time news sentiment information** and **technical analysis**, **explaining financial jargon** and **collating together vast amounts of vital information into a clear and intuitive dashboard**, we hope to increase the financial literacy of every member in the community.

## What it does
FinWhiz consists of five major components:
1. An **individual stock tracker** that supplies real-time stock price data and fundamental analysis of the company (including metrics like the P/E ratio, market capitalization, etc with clear explanations of what the terms mean). To enable users to keep up to date with the latest information, users can also plot interactive charts to visualize candlestick charts, calculate moving averages and retrieve real-time news articles coupled with sentiment analysis to track market sentiment of the company over time.

<p float="left">
  <img src="/images/Track1.png" width="460" />
  <img src="/images/Track2.png" width="460" /> 
</p>
<p float="left">
  <img src="/images/Track3.png" width="460" />
  <img src="/images/Track4.png" width="460" /> 
</p>

2. A **company fundamentals comparison** that compares the S&P500 companies across various metrics (such as beta, stock price, etc.) and enables users to sort these companies based on these metrics and plot them on interactive charts to decide which companies they are interested to invest in.

<p align="center">
  <img width="460" src="/images/CompareCompanies.png">
</p>

3. A **personalized portfolio optimizer** that suggests stocks to invest in based on the user's individual risk tolerance and target returns. This is calculated by analyzing the stocks' historical data to calculate the average volatility and expected returns.

<p align="center">
  <img width="460" src="/images/OptimizePortfolio.png">
</p>

4. A **candlestick pattern detector** for individual stocks that analyses a company's real-time stock data to detect candlestick patterns that may suggest either a reversal or continuation of a bullish or bearish price trend.

<p align="center">
  <img width="460" src="/images/FindCandlestick.png">
</p>

5. A **candlestick pattern screener** that scans real-time stock data of the S&P500 companies and filters them according to the patterns exhibited.

<p align="center">
  <img width="460" src="/images/ScanCandlestick.png">
</p>

## How we built it
We used **CockroachCloud**, hosted with **Google Cloud**, to store each company's real-time stock prices,  fundamental financial data (including the market capitalization, dividend yield, shares outstanding and more), news articles regarding the company and the associated sentiment (whether it is negative or positive) calculated using the Natural Language Processing library **nltk**. 

<p align="center">
  <img width="600" src="/images/dbSchema.png">
</p>

When a user queries the database, we retrieve the information from CockroachCloud using **psycopg2** and **SQLAlchemy** and display it on the front-end in a visually-appealing and easy-to-understand manner with **Streamlit**. We use **Plotly** to plot interactive charts and effectively summarize the data and provide immediate actionable insights to users.

<p align="center">
  <img width="600" src="/images/TechStack.png">
</p>
<p align="center">
  <img width="600" src="/images/CockroachCloud.png">
</p>

import yfinance as yf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def generate_heatmap(tickers):
    data = {ticker: yf.Ticker(ticker).info['regularMarketChangePercent'] for ticker in tickers}
    df = pd.DataFrame.from_dict(data, orient='index', columns=["% Change"])

    sns.set(font_scale=1.2)
    heatmap = sns.heatmap(df, annot=True, cmap="RdYlGn", center=0)
    plt.title("NASDAQ Heatmap")
    plt.savefig("heatmap.png")
    plt.clf()

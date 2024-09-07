#from summarizer import summarize_stories
from openai import OpenAI
import openai
import yfinance as yf


openai_api_key = ''


client = OpenAI(api_key=openai_api_key) # in prod app we should keep API keys as env variables
openai.api_key = openai_api_key

def get_comapny_logo_url(symbol):
     stock = yf.Ticker(symbol)
     if 'logo_url' in stock.info:
        return stock.info['logo_url']
     return None


def get_stock_data(symbol):
    stock = yf.Ticker(symbol)
    hist = stock.history(period="1y")
    
    financial_data = {}

    if not stock.info or hist.empty:
        raise ValueError(f"Stock data not found for symbol: {symbol}")
    
    # Check if each piece of financial data exists before adding it to the dictionary
    if 'currentPrice' in stock.info:
        financial_data['current_price'] = stock.info['currentPrice']
    
    if 'marketCap' in stock.info:
        financial_data['market_cap'] = stock.info['marketCap']
    
    if 'trailingPE' in stock.info:
        financial_data['pe_ratio'] = stock.info['trailingPE']
    
    if 'dividendYield' in stock.info:
        financial_data['dividend_yield'] = stock.info['dividendYield']
    
    # Calculate 1-year return if historical data is available
    if not hist.empty:
        financial_data['return_1y'] = (hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]
    
    return financial_data, hist

def analyze_stock(stock_symbol,financial_data=None,news=None):
    prompt = f"Analyze the stock {stock_symbol} based on the following financial data and news information:\n\n"
        
    # Add the financial data if it exists
    prompt += "Financial Data:\n"
        
    if 'current_price' in financial_data:
            prompt += f"- Current Price: {financial_data['current_price']}\n"
        
    if 'market_cap' in financial_data:
            prompt += f"- Market Cap: {financial_data['market_cap']}\n"
        
    if 'pe_ratio' in financial_data:
            prompt += f"- P/E Ratio: {financial_data['pe_ratio']}\n"
        
    if 'dividend_yield' in financial_data:
            prompt += f"- Dividend Yield: {financial_data['dividend_yield']}\n"
        
    if 'return_1y' in financial_data:
            prompt += f"- 1-Year Return: {financial_data['return_1y']:.2%}\n"
        
    # Add space between sections
    prompt += "\nRecent News:\n"
    # Adding news headlines and summaries
    for headline, summary in news.items():
        prompt += f"- {headline}: {summary}\n"
    
    prompt += f"\nBased on this data, provide a comprehensive analysis of the stock's current situation, potential risks, and opportunities. Keep in mind that some of this news may not be relevent to {stock_symbol}. What would be your recommendation for investors considering this stock?"

    response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a financial analyst. Your job is to analyze given stocks using financial data and market news and give investment advice. Never mention articles by name"},
                {"role": "user", "content": prompt}
            ]
        )

    return response.choices[0].message.content


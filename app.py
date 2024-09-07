# improve UI (appearance) add company logos with search 
# add error handling: financial data that isn't included from API, summary returns error (key error: 0) -> user input error handling
# improve speed of summary pipeline -> maybe cap the number of news stories we read?
# Add 'trending stocks' feature ? 
# ensure all font is a visible colour, currently the headings are very faint and quite invisible
# clean up appearance of text (Remove "###")
# add outlook forecasting, Brownian Motion?
# fix 'analyze stock' button so it shows text when not hovering
# The reason we see articles which we're unable to retrieve through web scraping is because we only look at HTML <article> tag with beautiful soup,
#  we can try and parse different tags and this might lead to more articles being retrieved
# Create an OpenAI assitant

import streamlit as st
from summarizer import run_summarize_stories #, summarize_stories
from LLM import get_stock_data, analyze_stock, get_comapny_logo_url
from plot_stock import plot_stock_chart
import asyncio


# Custom CSS for the UI
st.markdown("""
   <style>
    body {
        background-color: #000;
    }
    .main {
        background-color: #000;
        color: #FFF;
        font-family: Arial, sans-serif;
    }
    .header {
        text-align: center;
        margin-top: 5vh; /* Adjusted to 5% of viewport height */
    }
    .title-box {
        text-align: center;
        margin-top: 2vh; /* Adjusted to 2% of viewport height */
        margin-bottom: 3vh; /* Adjusted to 3% of viewport height */
        font-size: 5vw; /* Adjusted to 4% of viewport width */
        color: #FFD700;
        font-weight: bold;
        white-space: nowrap;
    
    }
    .input-box {
        margin: 2vh auto; /* Adjusted to 2% of viewport height */
        width: 30vw; /* Adjusted to 30% of viewport width */
        text-align: center;
    }
    .input-label {
        color: #999;
        font-size: 2vw; /* Adjusted to 2% of viewport width */
    }
    .output-box {
        background-color: #000;
        border: 0.3vw solid #FFD700; /* Adjusted to 0.3% of viewport width */
        border-radius: 1vw; /* Adjusted to 1% of viewport width */
        padding: 2vw; /* Adjusted to 2% of viewport width */
        color: #FFD700;
        font-size: 1.5vw; /* Adjusted to 1.5% of viewport width */
        margin-top: 2vh; /* Adjusted to 2% of viewport height */
        max-height: 60vh;  /* Adjusted to 50% of viewport height */
        overflow-y: auto;  /* Enable vertical scrolling */
        width: 70vw; /* Adjusted to 60% of viewport width */
        position: relative;
        left: -14vw; /* Adjusted to move the box 5% of the viewport width to the left */
    }
    .logo-img {
        position: absolute;
        top: 10px;
        right: 10px;
        width: 80px; /* Adjust the size of the logo */
        height: auto;
    }
    .image-container {
        display: flex;
        justify-content: center;
    }
    div.stButton > button {
            background-color: gold;
            color: black;
    }
    div.stButton > button:hover {
            color: white
    }
    </style>
    """, unsafe_allow_html=True)


# Header with Custom Icon
st.markdown('<div class="title-box">Stock Genie</div>', unsafe_allow_html=True)
left, center, right = st.columns(3)
with center:
    st.image('icons/Untitled design (1).png', width=200)


# Input box for ticker symbol
st.markdown('<div class="input-box">', unsafe_allow_html=True)
#st.markdown('<div class="input-label">Enter the stock ticker</div>', unsafe_allow_html=True)
ticker = st.text_input("", value="", max_chars=5,placeholder="Enter the stock ticker (ex. 'AAPL')")
st.markdown('</div>', unsafe_allow_html=True)

# Add a button to fetch news and analyze sentiment
if st.button("Analyze Stock"):
    ticker = ticker.upper()
    if not ticker:
        st.error("Please enter a valid stock ticker symbol. ")
    else:
        with st.spinner('Fetching data and analyzing, this may take a moment...'):
            try:
                financial_data, hist = get_stock_data(ticker)
                #news = summarize_stories(ticker)
                news = asyncio.run(run_summarize_stories(ticker))
                analysis = analyze_stock(ticker, financial_data, news)
                logo_url = get_comapny_logo_url(ticker)
                st.plotly_chart(plot_stock_chart(hist))
                if logo_url:
                    st.markdown(f"""
                        <div class="output-box">
                            <img src="{logo_url}" class="logo-img" alt="Company Logo">
                            <strong>Analysis for {ticker}: </strong><br>
                            {analysis}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                            <div class="output-box">
                                <strong>Analysis for {ticker}: </strong><br>
                                {analysis}
                            </div>
                            """, unsafe_allow_html=True)
            
            except Exception as e:
                st.error(f"An error occured: {str(e)}")
                    

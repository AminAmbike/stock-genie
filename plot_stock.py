import plotly.graph_objs as go

def plot_stock_chart(hist):
    fig = go.Figure()

    # Add trace for the closing price
    fig.add_trace(go.Scatter(
        x=hist.index,
        y=hist['Close'],
        mode='lines',
        name='Close Price',
        line=dict(color='#FFD700')  # Gold color for the line
    ))

    # Update layout to match the black and gold theme
    fig.update_layout(
        title="Stock Price Over the Last Year",
        title_font=dict(color='#FFD700'),
        xaxis_title="Date",
        yaxis_title="Close Price (USD)",
        xaxis=dict(
            color='#FFD700',
            showgrid=False  # No grid lines
        ),
        yaxis=dict(
            color='#FFD700',
            showgrid=False  # No grid lines
        ),
        plot_bgcolor='black',  # Background color of the plot area
        paper_bgcolor='black',  # Background color around the plot
        font=dict(color='#FFD700'),  # Color of all text
        hovermode="x"
    )

    return fig
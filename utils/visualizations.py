import plotly.graph_objects as go
import plotly.express as px

def create_equity_chart(df):
    """
    Create an interactive equity exposure chart
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['equity_exposure'].cumsum(),
        mode='lines',
        name='Equity Exposure',
        line=dict(color='#0066cc', width=2)
    ))
    
    fig.update_layout(
        title='Cumulative Equity Exposure Over Time',
        xaxis_title='Date',
        yaxis_title='Exposure Amount',
        template='plotly_white',
        hovermode='x unified'
    )
    
    return fig

def create_metrics_chart(df):
    """
    Create an interactive metrics visualization
    """
    metrics = df.groupby('Category')['Amount'].sum().reset_index()
    
    fig = px.pie(
        metrics,
        values='Amount',
        names='Category',
        title='Portfolio Composition',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        showlegend=False,
        template='plotly_white'
    )
    
    return fig

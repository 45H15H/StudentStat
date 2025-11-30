# Import packages
from dash import Dash, html, dash_table, dcc, Input, Output
import pandas as pd
import plotly.express as px
# import numpy as np

# Initialize the app
app = Dash(__name__, title="Student Performance Dashboard")

server = app.server

theme = {
    'dark': True,
    'detail': '#FF752D',
    'primary': '#E04f28',
    'secondary': '#FF752D',
}

# Load and prepare data
df = pd.read_excel(r"Consolidated_SGPA_CGPA_Report.xlsx", sheet_name="Clean")
df.columns = df.columns.str.replace(":", "")
df.columns = df.columns.str.lower()
df = df.sort_values(by='reg.no')

# Create SGPA and CGPA dataframes
sgpa = df[["reg.no", "student name", "sgpa_1", "sgpa_2", "sgpa_3", "sgpa_4", "sgpa_5", "sgpa_6", "sgpa_7", "sgpa_8"]]
cgpa = df[["reg.no", "student name", "cgpa_1", "cgpa_2", "cgpa_3", "cgpa_4", "cgpa_5", "cgpa_6", "cgpa_7", "cgpa_8"]]

# Prepare transposed SGPA data for line chart
transposed_sgpa = sgpa.transpose()
transposed_sgpa.reset_index(drop=False, inplace=True)
transposed_sgpa.iloc[1, 0] = "semester"
transposed_sgpa = transposed_sgpa.iloc[1:]
transposed_sgpa.columns = transposed_sgpa.iloc[0]
transposed_sgpa = transposed_sgpa.iloc[1:]
transposed_sgpa = transposed_sgpa.reset_index(drop=True)

# Prepare transposed CGPA data for line chart
transposed_cgpa = cgpa.transpose()
transposed_cgpa.reset_index(drop=False, inplace=True)
transposed_cgpa.iloc[1, 0] = "semester"
transposed_cgpa = transposed_cgpa.iloc[1:]
transposed_cgpa.columns = transposed_cgpa.iloc[0]
transposed_cgpa = transposed_cgpa.iloc[1:]
transposed_cgpa = transposed_cgpa.reset_index(drop=True)

# Calculate average SGPA for each semester
sgpa_columns = [col for col in sgpa.columns if col.startswith('sgpa_')]
avg_sgpa = {}

for col in sgpa_columns:
    # Extract semester number from column name (e.g., 'sgpa_1' -> '1')
    semester = col.split('_')[1]
    # Calculate average SGPA for this semester
    avg_sgpa[semester] = sgpa[col].mean()

# Convert to DataFrame for plotting
avg_sgpa_df = pd.DataFrame({
    'semester': list(avg_sgpa.keys()),
    'average_sgpa': list(avg_sgpa.values())
})

# Sort by semester number
avg_sgpa_df['semester'] = avg_sgpa_df['semester'].astype(int)
avg_sgpa_df = avg_sgpa_df.sort_values('semester')

# SGPA distribution data is now created dynamically in the callback function

# Create figures
# 1. Line chart for a specific student showing both SGPA and CGPA
def create_student_line_chart(student_name):
    import plotly.graph_objects as go

    # Create a figure with two traces
    fig = go.Figure()

    # Get the semester values for x-axis (use the same for both traces)
    semester_values = transposed_sgpa["semester"].tolist()
    semesters = ['Semester I', 'Semester II', 'Semester III', 'Semester IV', 'Semester V', 'Semester VI', 'Semester VII', 'Semester VIII']
    ticktext = [f"Semester {sem}" for sem in semester_values]

    # Add SGPA trace
    fig.add_trace(go.Scatter(
        x=semester_values,
        y=transposed_sgpa[student_name],
        mode='lines+markers',
        name='SGPA',
        line=dict(color=theme['primary'], width=2),
        marker=dict(size=10, color=theme['primary'])
    ))

    # Add CGPA trace
    fig.add_trace(go.Scatter(
        x=semester_values,
        y=transposed_cgpa[student_name],
        mode='lines+markers',
        name='CGPA',
        line=dict(color='#3498db', width=2),
        marker=dict(size=10, color='#3498db')
    ))

    # Update layout
    fig.update_layout(
        title=f'Performance Chart for {student_name}',
        xaxis_title='Semester',
        yaxis_title='Grade Point Average',
        yaxis=dict(range=[0, 10.5]),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        # Dark theme settings
        paper_bgcolor='#2c3e50',
        plot_bgcolor='#2c3e50',
        font=dict(color='white'),
        margin=dict(l=40, r=40, t=50, b=40)
    )

    # Update x-axis with custom tick labels
    fig.update_xaxes(
        tickmode='array',
        tickvals=semester_values,
        ticktext=semesters,
        gridcolor='rgba(255, 255, 255, 0.1)',
        zerolinecolor='rgba(255, 255, 255, 0.1)'
    )

    # Update y-axis styling
    fig.update_yaxes(
        gridcolor='rgba(255, 255, 255, 0.1)',
        zerolinecolor='rgba(255, 255, 255, 0.1)'
    )

    return fig

# 2. Bar chart for CGPA with semester selection
# Note: The actual bar chart is now created dynamically by the callback function

# 3. Box plot for SGPA (dynamic based on semester selection)

# 4. Line chart for average SGPA
avg_line_fig = px.line(avg_sgpa_df, x='semester', y='average_sgpa',
                      title='Average SGPA Across Semesters',
                      markers=True,
                      labels={
                          'semester': 'Semester',
                          'average_sgpa': 'Average SGPA'
                      },
                      color_discrete_sequence=[theme['primary']])

# Update layout for dark theme
avg_line_fig.update_layout(
    paper_bgcolor='#2c3e50',
    plot_bgcolor='#2c3e50',
    font=dict(color='white'),
    margin=dict(l=40, r=40, t=50, b=40)
)

avg_line_fig.update_yaxes(
    range=[0, 10],
    gridcolor='rgba(255, 255, 255, 0.1)',
    zerolinecolor='rgba(255, 255, 255, 0.1)'
)

avg_line_fig.update_xaxes(
    tickmode='linear',
    gridcolor='rgba(255, 255, 255, 0.1)',
    zerolinecolor='rgba(255, 255, 255, 0.1)'
)

# 5. Pie chart for SGPA distribution is now created dynamically in the callback function

# Get list of student names for dropdown
student_names = sgpa["student name"].tolist()

# App layout
app.layout = html.Div([
    html.H1("Student Performance Dashboard", style={'textAlign': 'center', 'marginBottom': '30px', 'color': theme['primary']}),

    # Responsive container for the main content
    html.Div([
        # First column (becomes full width on mobile)
        html.Div([
            html.Div([
                html.H3("Individual Student Performance Tracker", style={'textAlign': 'center', 'color': theme['primary']}),
                html.Label("Select Student:", style={'fontWeight': 'bold', 'marginBottom': '10px', 'color': '#ffffff'}),
                dcc.Dropdown(
                    id='student-dropdown',
                    options=[{'label': name, 'value': name} for name in student_names],
                    value=student_names[0] if student_names else None,
                    style={'marginBottom': '15px', 'color': '#333333'}
                ),
                dcc.Graph(id='student-line-chart')
            ], style={'padding': '20px', 'backgroundColor': '#2c3e50', 'borderRadius': '10px', 'marginBottom': '20px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.3)'}),

            html.Div([
                html.H3("Average SGPA Trend", style={'textAlign': 'center', 'color': theme['primary']}),
                dcc.Graph(figure=avg_line_fig)
            ], style={'padding': '20px', 'backgroundColor': '#2c3e50', 'borderRadius': '10px', 'marginBottom': '20px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.3)'}),
        ], className='column-left'),

        # Second column (becomes full width on mobile)
        html.Div([
            html.Div([
                html.H3("SGPA Distribution by Range", style={'textAlign': 'center', 'color': theme['primary']}),
                html.Label("Select Semester:", style={'fontWeight': 'bold', 'marginBottom': '10px', 'color': '#ffffff'}),
                dcc.Dropdown(
                    id='pie-semester-dropdown',
                    options=[
                        {'label': 'Semester 1', 'value': '1'},
                        {'label': 'Semester 2', 'value': '2'},
                        {'label': 'Semester 3', 'value': '3'},
                        {'label': 'Semester 4', 'value': '4'},
                        {'label': 'Semester 5', 'value': '5'},
                        {'label': 'Semester 6', 'value': '6'},
                        {'label': 'Semester 7', 'value': '7'},
                        {'label': 'Semester 8', 'value': '8'}
                    ],
                    value='8',  # Default to semester 8
                    style={'marginBottom': '15px', 'color': '#333333'}
                ),
                dcc.Graph(id='sgpa-pie-chart')
            ], style={'padding': '20px', 'backgroundColor': '#2c3e50', 'borderRadius': '10px', 'marginBottom': '20px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.3)'}),

            html.Div([
                html.H3("SGPA Distribution by Semester", style={'textAlign': 'center', 'color': theme['primary']}),
                html.Label("Select Semester:", style={'fontWeight': 'bold', 'marginBottom': '10px', 'color': '#ffffff'}),
                dcc.Dropdown(
                    id='box-semester-dropdown',
                    options=[
                        {'label': 'Semester 1', 'value': '1'},
                        {'label': 'Semester 2', 'value': '2'},
                        {'label': 'Semester 3', 'value': '3'},
                        {'label': 'Semester 4', 'value': '4'},
                        {'label': 'Semester 5', 'value': '5'},
                        {'label': 'Semester 6', 'value': '6'},
                        {'label': 'Semester 7', 'value': '7'},
                        {'label': 'Semester 8', 'value': '8'}
                    ],
                    value='4',  # Default to semester 4
                    style={'marginBottom': '15px', 'color': '#333333'}
                ),
                dcc.Graph(id='sgpa-box-plot')
            ], style={'padding': '20px', 'backgroundColor': '#2c3e50', 'borderRadius': '10px', 'marginBottom': '20px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.3)'}),
        ], className='column-right'),
    ], className='row'),

    # Full width section at the bottom
    html.Div([
        html.H3("CGPA Comparison by Semester", style={'textAlign': 'center', 'color': theme['primary']}),
        html.Label("Select Semester:", style={'fontWeight': 'bold', 'marginBottom': '10px', 'color': '#ffffff'}),
        dcc.Dropdown(
            id='semester-dropdown',
            options=[
                {'label': 'Semester 1', 'value': '1'},
                {'label': 'Semester 2', 'value': '2'},
                {'label': 'Semester 3', 'value': '3'},
                {'label': 'Semester 4', 'value': '4'},
                {'label': 'Semester 5', 'value': '5'},
                {'label': 'Semester 6', 'value': '6'},
                {'label': 'Semester 7', 'value': '7'},
                {'label': 'Semester 8', 'value': '8'}
            ],
            value='8',  # Default to semester 8
            style={'marginBottom': '15px', 'color': '#333333'}
        ),
        dcc.Graph(id='cgpa-bar-chart')
    ], style={'padding': '20px', 'backgroundColor': '#2c3e50', 'borderRadius': '10px', 'marginTop': '20px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.3)'}),
], style={
    'fontFamily': 'Arial, sans-serif', 
    'padding': '20px', 
    'maxWidth': '1200px', 
    'margin': '0 auto',
    'backgroundColor': '#1e272e',
    'color': '#ffffff',
    'minHeight': '100vh'
})

# Callback for student dropdown
@app.callback(
    Output('student-line-chart', 'figure'),
    Input('student-dropdown', 'value')
)
def update_student_chart(selected_student):
    if selected_student:
        return create_student_line_chart(selected_student)
    return {}

# Callback for semester dropdown to update CGPA bar chart
@app.callback(
    Output('cgpa-bar-chart', 'figure'),
    Input('semester-dropdown', 'value')
)
def update_cgpa_chart(selected_semester):
    if selected_semester:
        # Create bar chart for the selected semester
        column_name = f'cgpa_{selected_semester}'
        fig = px.bar(
            cgpa, 
            x='student name',
            y=column_name,
            title=f'CGPA Chart for Semester {selected_semester}',
            color_discrete_sequence=[theme['primary']]
        )
        fig.update_layout(
            xaxis={'categoryorder':'total descending', 'tickangle': 90, 'title': 'Student Name'},
            yaxis={'title': 'CGPA'},
            height=600,
            # Dark theme settings
            paper_bgcolor='#2c3e50',
            plot_bgcolor='#2c3e50',
            font=dict(color='white'),
            margin=dict(l=40, r=40, t=50, b=40)
        )

        # Update axes styling for dark theme
        fig.update_xaxes(
            gridcolor='rgba(255, 255, 255, 0.1)',
            zerolinecolor='rgba(255, 255, 255, 0.1)'
        )
        fig.update_yaxes(
            gridcolor='rgba(255, 255, 255, 0.1)',
            zerolinecolor='rgba(255, 255, 255, 0.1)'
        )

        return fig
    return {}

# Callback for pie chart semester dropdown
@app.callback(
    Output('sgpa-pie-chart', 'figure'),
    Input('pie-semester-dropdown', 'value')
)
def update_sgpa_pie_chart(selected_semester):
    if selected_semester:
        # Create SGPA distribution data for the selected semester
        sgpa_copy = sgpa.copy()
        column_name = f'sgpa_{selected_semester}'

        # Create SGPA range distribution for the selected semester
        sgpa_copy['sgpa_range'] = pd.cut(
            sgpa_copy[column_name], 
            bins=[0, 5, 6, 7, 8, 9, 10], 
            labels=['Below 5', '5-6', '6-7', '7-8', '8-9', '9-10'],
            include_lowest=True
        )

        # Count students in each SGPA range
        sgpa_distribution = sgpa_copy['sgpa_range'].value_counts().reset_index()
        sgpa_distribution.columns = ['SGPA Range', 'Number of Students']

        # Create pie chart with custom colors that work well on dark theme
        custom_colors = ['#ff5252', '#ff793f', '#ffb142', '#7bed9f', '#2ed573', '#00EA64']

        fig = px.pie(
            sgpa_distribution, 
            values='Number of Students', 
            names='SGPA Range',
            title=f'Distribution of Students by SGPA Range (Semester {selected_semester})',
            color_discrete_sequence=custom_colors,
            hole=0.3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            legend_title="SGPA Range",
            font=dict(size=12, color='white'),
            # Dark theme settings
            paper_bgcolor='#2c3e50',
            plot_bgcolor='#2c3e50',
            margin=dict(l=20, r=20, t=50, b=20)
        )
        return fig
    return {}

# Callback for box plot semester dropdown
@app.callback(
    Output('sgpa-box-plot', 'figure'),
    Input('box-semester-dropdown', 'value')
)
def update_sgpa_box_plot(selected_semester):
    if selected_semester:
        # Create box plot for the selected semester
        column_name = f'sgpa_{selected_semester}'
        fig = px.box(
            sgpa, 
            y=column_name,
            title=f'SGPA Distribution for Semester {selected_semester}',
            color_discrete_sequence=[theme['primary']]
        )
        fig.update_layout(
            yaxis={'title': 'SGPA'},
            height=400,
            # Dark theme settings
            paper_bgcolor='#2c3e50',
            plot_bgcolor='#2c3e50',
            font=dict(color='white'),
            margin=dict(l=40, r=40, t=50, b=40)
        )

        # Update axes styling for dark theme
        fig.update_xaxes(
            gridcolor='rgba(255, 255, 255, 0.1)',
            zerolinecolor='rgba(255, 255, 255, 0.1)'
        )
        fig.update_yaxes(
            gridcolor='rgba(255, 255, 255, 0.1)',
            zerolinecolor='rgba(255, 255, 255, 0.1)'
        )

        return fig
    return {}

# Run the app
if __name__ == '__main__':
    app.run(debug=True)

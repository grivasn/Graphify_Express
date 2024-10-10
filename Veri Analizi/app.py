from flask import Flask, render_template, request
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import os
import random

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def read_data_from_excel(file_path):
    try:
        return pd.read_excel(file_path, engine='openpyxl')
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None


def random_color():
    return f'rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 0.8)'


def auto_create_chart(df):
    columns = df.columns
    charts = []

    for i, col in enumerate(columns[1:]):
        x_column = columns[0]
        y_column = col
        title = f"{x_column} Bazlı {y_column}"

        
        if pd.api.types.is_numeric_dtype(df[y_column]):
            chart_type = 'line' if i % 2 == 0 else 'bar'
            color = random_color() if chart_type == 'line' else random_color()
            charts.append(create_chart(df[x_column], df[y_column], chart_type=chart_type, title=title, line_color=color))
   
        elif pd.api.types.is_object_dtype(df[y_column]):
            
            frequency = df[y_column].value_counts()
            
            colors = [random_color() for _ in range(len(frequency))]
            charts.append(create_chart(frequency.index, frequency.values, chart_type='bar', title=title, marker_colors=colors))
        else:
            charts.append(f"{y_column} sayısal veya kategorik veri değil, grafik oluşturulmadı.")
    return charts


def create_chart(x_values, y_values, chart_type='line', title='', line_color='blue', marker_colors=None):
    chart = go.Figure()

    if chart_type == 'line':
        chart.add_trace(go.Scatter(x=x_values, y=y_values, mode='lines+markers+text', 
                                   line=dict(color=line_color, shape='spline'),
                                   marker=dict(size=8, color=marker_colors), 
                                   text=y_values, textposition='top center'))
    elif chart_type == 'bar':
  
        chart.add_trace(go.Bar(x=x_values, y=y_values, name=title, marker=dict(color=marker_colors)))

    chart.update_layout(title=title, plot_bgcolor='white', paper_bgcolor='white', font=dict(color='black'))
    return pio.to_html(chart, full_html=False)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
      
        if 'file' not in request.files:
            return "Dosya yüklenmedi"
        file = request.files['file']

        if file.filename == '':
            return "Dosya seçilmedi"

        if file and file.filename.endswith('.xlsx'):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path) 

            df = read_data_from_excel(file_path)  
            if df is None:
                return "Veri okunamadı."

            charts = auto_create_chart(df)  
            return render_template('index.html', charts=charts)  
        else:
            return "Lütfen bir Excel dosyası (.xlsx) yükleyin."
    return render_template('index.html', charts=None)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)

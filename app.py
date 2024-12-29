import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os
import zipfile
from flask import Flask, request, render_template
from transformers import pipeline
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend

# Initialize Flask app
app = Flask(__name__)
UPLOAD_FOLDER = './uploads'
OUTPUT_FOLDER = './static/output'

# Ensure upload and output directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize Hugging Face pipeline for text generation
generator = pipeline("text-generation", model="distilgpt2")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Load dataset
        try:
            dataset = pd.read_csv(filepath)
        except Exception as e:
            return f"Error reading CSV file: {str(e)}"

        # Validate required columns
        required_columns = ['START_DATE', 'END_DATE', 'CATEGORY']
        missing_columns = [col for col in required_columns if col not in dataset.columns]
        if missing_columns:
            return f"Missing required columns: {', '.join(missing_columns)}"

        # Data Preprocessing
        dataset['START_DATE'] = pd.to_datetime(dataset['START_DATE'], errors='coerce')
        dataset['END_DATE'] = pd.to_datetime(dataset['END_DATE'], errors='coerce')
        dataset['Trip_Duration'] = (dataset['END_DATE'] - dataset['START_DATE']).dt.total_seconds() / 60  # Duration in minutes

        # Drop rows with invalid dates
        dataset = dataset.dropna(subset=['START_DATE', 'END_DATE'])

        # Feature Engineering
        dataset['day_of_week'] = dataset['START_DATE'].dt.day_name()
        dataset['month'] = dataset['START_DATE'].dt.month_name()
        dataset['hour_of_day'] = dataset['START_DATE'].dt.hour
        dataset['time_category'] = pd.cut(
            dataset['hour_of_day'],
            bins=[0, 6, 12, 18, 24],
            labels=['Late Night', 'Morning', 'Afternoon', 'Evening'],
            right=False
        )

        # Matplotlib styling
        plt.style.use('default')
        colors = plt.cm.Pastel1(np.linspace(0, 1, 10))

        # 1. Category Distribution
        plt.figure(figsize=(12, 6))
        category_counts = dataset['CATEGORY'].value_counts()
        category_counts.plot(kind='bar', color=colors)
        plt.title('Uber Trip Categories')
        plt.xlabel('Category')
        plt.ylabel('Number of Trips')
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_FOLDER, 'category_distribution.png'))
        plt.close()

        # 2. Trip Duration Distribution
        plt.figure(figsize=(12, 6))
        sns.boxplot(data=dataset, x='CATEGORY', y='Trip_Duration', palette='Set3')
        plt.title('Trip Duration by Category')
        plt.xlabel('Category')
        plt.ylabel('Duration (Minutes)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_FOLDER, 'trip_duration_boxplot.png'))
        plt.close()

        # 3. Trips by Time of Day
        plt.figure(figsize=(12, 6))
        time_category_counts = dataset['time_category'].value_counts()
        time_category_counts.plot(kind='pie', autopct='%1.1f%%', colors=colors, startangle=140)
        plt.title('Trips by Time of Day')
        plt.ylabel('')
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_FOLDER, 'time_of_day_pie.png'))
        plt.close()

        # 4. Day of Week Analysis
        plt.figure(figsize=(12, 6))
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_counts = dataset['day_of_week'].value_counts().reindex(day_order)
        plt.bar(day_counts.index, day_counts.values, color=colors)
        plt.title('Trips by Day of Week')
        plt.xlabel('Day')
        plt.ylabel('Number of Trips')
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_FOLDER, 'day_of_week_bar.png'))
        plt.close()

        # Statistical Summary
        summary_stats = {
            'Total_Trips': len(dataset),
            'Average_Trip_Duration': round(dataset['Trip_Duration'].mean(), 2),
            'Median_Trip_Duration': round(dataset['Trip_Duration'].median(), 2),
            'Most_Common_Category': dataset['CATEGORY'].mode().values[0],
            'Peak_Time_Category': dataset['time_category'].mode().values[0],
            'Most_Active_Day': dataset['day_of_week'].mode().values[0]
        }

        # Generate Insights Using Hugging Face
        try:
            insights_prompt = f"""
            Analyze this Uber trip dataset:
            - Total Trips: {summary_stats['Total_Trips']}
            - Average Trip Duration: {summary_stats['Average_Trip_Duration']} minutes
            - Median Trip Duration: {summary_stats['Median_Trip_Duration']} minutes
            - Most Common Category: {summary_stats['Most_Common_Category']}
            - Peak Time: {summary_stats['Peak_Time_Category']}
            - Most Active Day: {summary_stats['Most_Active_Day']}

            Provide a detailed analysis with patterns, optimization strategies, and trends.
            """
            result = generator(insights_prompt, max_length=300, num_return_sequences=1)
            insights = result[0]['generated_text']
        except Exception as e:
            insights = f"Error generating insights: {str(e)}"

        # Zip visualizations
        zip_path = './static/uber_analysis_results.zip'
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for filename in os.listdir(OUTPUT_FOLDER):
                zipf.write(os.path.join(OUTPUT_FOLDER, filename), filename)

        return render_template(
            'analysis.html',
            summary_stats=summary_stats,
            insights=insights,
            download_link=zip_path
        )

    return "File upload failed."


if __name__ == '__main__':
    app.run(debug=True)

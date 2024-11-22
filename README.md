
# eCommerce Fraud Detection with Apache Spark

This repository contains a project developed as part of the FIT5202 - Data Processing for Big Data unit at Monash University. The goal is to design and implement a robust eCommerce fraud detection system using Apache Spark's powerful capabilities, focusing on machine learning and real-time analytics.

## Project Overview

The project addresses the challenges of detecting and mitigating fraudulent transactions in an eCommerce setting. The rise of Card-Not-Present (CNP) fraud highlights the necessity of advanced, real-time detection systems. The system leverages historical data, browsing behaviors, and customer information to predict and prevent fraud while ensuring scalability and accuracy.

### Objectives:
1. Build a machine learning model using PySpark MLlib to detect fraudulent transactions.
2. Utilize Spark Streaming to predict fraudulent activity in real time.
3. Provide actionable insights through clustering analysis.
4. Explore data ethics, privacy, and security in the context of big data.

## Architecture

![Architecture Diagram](path/to/your/image.png)  
*Figure: Overall architecture of the fraud detection system.*

The architecture involves:
1. **Data Preprocessing**: Loading and transforming datasets into feature-rich formats.
2. **Machine Learning**: Training and evaluating models to classify transactions as fraudulent or legitimate.
3. **Streaming**: Processing real-time transaction data for immediate fraud detection.
4. **Visualization**: Providing real-time dashboards for monitoring system operations.

## Datasets

The datasets used include:
- **category.csv**: Product category information.
- **customer.csv**: Customer details.
- **product.csv**: Product descriptions.
- **transaction.csv**: Sales transactions.
- **browsing_behaviour.csv**: Customer browsing data.
- **customer_session.csv**: Mapping between browsing sessions and customers.
- **fraud_transaction.csv**: Known fraudulent transactions.

## Installation and Setup

### Requirements:
- Python 3.8+
- Apache Spark 3.5.0+
- Jupyter Notebook
- Required libraries: PySpark, Matplotlib, Seaborn, etc.

### Steps:
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/ecommerce-fraud-detection.git
   ```
2. Set up a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Launch Jupyter Notebook:
   ```bash
   jupyter notebook
   ```

## Features and Tasks

1. **Data Loading and Transformation**:
   - Load and process datasets with PySpark DataFrames.
   - Engineer features like browsing action counts, session times, and customer details.

2. **Exploratory Data Analysis (EDA)**:
   - Compute statistical summaries.
   - Visualize data patterns and identify fraud trends.

3. **Machine Learning**:
   - Build classification models using Random Forest and Gradient Boosted Trees.
   - Evaluate models based on precision, recall, AUC, and accuracy.
   - Save the best-performing model.

4. **Clustering Analysis**:
   - Apply K-means clustering to identify behavioral patterns among fraudsters.

5. **Data Ethics and Privacy**:
   - Explore ethical implications of big data processing.

## Results

- **Fraud Detection**: Achieved [X]% accuracy using Gradient Boosted Trees.
- **Insights**: Identified key behaviors of fraudsters such as high cart modification rates and unusual browsing times.

## Contribution

Contributions are welcome! Feel free to fork the repository and submit a pull request.

## License

This project is for academic purposes. Please contact Monash University for permissions or concerns regarding data usage.

# This repository stores my course work related to Data Science and Machine Learning.
Majority of work is related to machine learning projects done in UCSD Machine Learnig Bootcamp (in progress).
The following is a summary of current projects here:

--DataVisualizationFinalProject-1：
A Data Visualization project done during data science cource for data science certificate. It uses python to analyze the data from yahoo finance on four industries and try to check if they are influenced by US-China trade war. It saves the data in MySQL and display the results in Tableau Dashboard.

--mec-3.4.1-api-mini-project：
In this mini-project, I use API requests to grab data from NASDAQ and analyze data based on requirements using Jupyter Notebook.

--iris
A practice for plotting using matplotlib, also tried to show legends without using seaborn

--mec-5.3.10-data-wranging-with-pandas-mini-project：
A practice for data wrangling using pandas and plot charts

--mec-5.4.4-json-data-wrangling-mini-project：
A practice for data wrangling import json and use json_normalize to unwind nested structure of json file

--mec-5.5.4-webscraping-project：
A practice based on tutorial <https://docs.scrapy.org/en/latest/intro/tutorial.html>. The following is done:
   1) a class based on scrapy css method
   2) a class based on scrapy xpath method
   3) a python file which writes the json file to sqlite

--mec-5.6.6-sql-with-spark-mini-project：
This project is using spark sql in Databricks. 
The following link is a published view, but will expire in 6 month:
https://databricks-prod-cloudfront.cloud.databricks.com/public/4027ec902e239c93eaaa8714f173bcfc/4306574174881512/1987665294358223/113266931557391/latest.html

--mec-6.4.1.data-wrangling-at-scale-with-spark:
This project is a practice based on NASA log. It does EDA and ETL.
The project is done in Databrick. The following link is a published view, which will expire in 6 months:
https://databricks-prod-cloudfront.cloud.databricks.com/public/4027ec902e239c93eaaa8714f173bcfc/4306574174881512/3281807393584500/113266931557391/latest.html

--SampleDataForCapstone:
This is a EDA process for capstone process with some sample dataset for commercial energy, residential energy and weather data.

--mec-11.4.1-linear-regression-mini-project:
This is an exercise focus on linear regression model using both sklearn and statsmodel.
It investigate the boston dataset and evaluate the model in the following parameters:
    - outlier and leverage
    - R-squared value
    - F-statistic
    - F-test

--mec-12.4.2-logistic-regression-mini-project
This is an exercise on classification using logistic regression method.
It runs GridSerachCV and discusses the math behind the algorithm.

--mec-13.5.1-tree-based-algorithms-mini-project
This is a decision tree practice project. It also has some investigation on the xgboost, catboost and lightgbm.

--mec-18.5.1-time-series-analysis-mini-project
This is a mini project which builds a ARIMA model and a LSTM model for predicting IBM price.

--mec-16.2.6-clustering-mini-project
This is a mini project working with clustering algorithms from sklearn. It focuses on K-means, and explores visualization using PCA.
Additionally, it explores the alogorithms like Spectral Clustering, DBSCAN, Affinity propagation and Agglomerative clustering.

-- Capstone-Visualization
This is the visualization step for capstone project. It explores the plot of building energy in a year
It also investigated the relationship among humidity, temperature and energy.

--mec-16.4.1-anomaly-detection-mini-project
Anomaly detection practice. Tried with 3-sigma outlier detection, and then with isolation forest in sklearn.
Then with pyod lib, tried CBLOF, isolation forest and autoencoder on multivariate anomaly detection.

--mec-17.4.1-recommendation-systems-mini-project
This is a practice on recommendation system, it explores the recommendation system based on content and user.
For content, it uses TFIDF to compare the similarity and developed a model using tensorflow.

--mec-23.2.8-scalable-ml-with-spark-ml-mini-project
This is a project focusing on practicing spark machine learning libraries, including linear regression classifier, GBT classifier and Random Forest Classifier. The project is done in Databrick. The following link is a published view, which will expire in 6 months:
https://databricks-prod-cloudfront.cloud.databricks.com/public/4027ec902e239c93eaaa8714f173bcfc/4306574174881512/1397366416372765/113266931557391/latest.html

-- Capstone- API:
This includes a flask API built for initiate a mongodb and forecast data based on imported data. It uses the model developed in Capstone- Prototype. It also includes a front-end using streamlit to host a web that calls api developed in flask API.
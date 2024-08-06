# Owner Name Scrubber


This tool refines a dataset containing owner names (e.g., from real estate records) by:

1. Classifying names as "Human Name" or "Not Human Name" using a pre-trained machine learning model.
2. Filtering out potential company/non-human names based on the classification and a list of common business keywords.

## Prerequisites

- **Python:** Install Python (3.6 or later) if you don't have it. Download from [https://www.python.org/downloads/](https://www.python.org/downloads/).
- **Dependencies:** Install the required Python packages:
  ```bash
  pip install pandas scikit-learn pickle
  ```

## Usage Instructions

1. **Data Preparation:**
   - Place your input Excel file (e.g., "MI 2 Rows of Couties North of IN-OH.xlsx") in the same directory as this Python script. 
   - The file must have the following columns:
     - `MAIL_ADDR`
     - `MAIL_CITY`
     - `MAIL_STATE`
     - `MAIL_ZIP`
     - `OWNER_NAME_1`

2. **Model and Vectorizer:**
   - Ensure these files are also in the same directory as the script:
     - `logreg_classifier.pickle`: The trained logistic regression model.
     - `logreg_vectorizer.pickle`: The TF-IDF vectorizer used for text preprocessing.

3. **Run the Script:**
   - Execute the Python script. It will perform the following:
     - Load and clean the data (remove missing values, duplicates).
     - Load the trained model and vectorizer.
     - Predict whether each `OWNER_NAME_1` is a "Human Name" or not.
     - Save an intermediate file (`MI 2 Rows of Couties North of IN-OH.xlsx Classified.xlsx`) with the predictions.
     - Filter out names classified as "Not Human Name" using both:
       - A list of previously identified human names from a separate dataset.
       - A keyword-based filter to remove common business terms (`company_keywords`).
     - Save the final cleaned data to `MI 2 Rows of Couties North of IN-OH.xlsx SCRUBBED.xlsx`.



## How It Works

1. **Data Loading and Cleaning:** The script reads the Excel file, removes rows with missing data in key columns, and eliminates duplicates based on the mailing address.
2. **Model and Vectorizer Loading:** The trained model and the vectorizer used during training are loaded from the `pickle` files.
3. **Prediction:** The model predicts the category ("Human Name" or "Not Human Name") for each `OWNER_NAME_1` entry.
4. **Filtering:** The script applies two filters to remove potential non-human names:
   - **Human Name List Filtering:** It compares the names against a list of known human names. If a name is not in the list, it's considered a potential company name.
   - **Keyword-Based Filtering:**  It checks if a name contains any words from the `company_keywords` list. If it does, the name is treated as a company name.

## Customization

- **Keywords:** You can tailor the `company_keywords` list to better suit your specific domain and the types of company names you want to remove.
- **Filtered Names:** If you have another dataset with reliable "Human Name" classifications, you can use it for more effective filtering.
- **Model:** The script currently uses logistic regression. If needed, you can retrain the model with different algorithms or features for potentially better performance.


## Troubleshooting

- **Missing Files:** Ensure all required files (Excel data, model, vectorizer) are in the same directory as the script or provide the correct file paths.
- **Column Names:** Double-check that your Excel file has the exact column names specified (`MAIL_ADDR`, `MAIL_CITY`, `MAIL_STATE`, `MAIL_ZIP`, `OWNER_NAME_1`).
- **Model/Vectorizer Errors:** If errors occur while loading the model or vectorizer, verify that they were saved correctly during training.

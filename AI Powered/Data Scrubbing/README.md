# Name Scrubbing Tool

This tool uses a trained machine learning model to clean owner names from real estate datasets. It distinguishes between human names and potential company names.

## Prerequisites

- **Python:** Install Python (3.6 or later) if you haven't already. You can download it from [https://www.python.org/downloads/](https://www.python.org/downloads/).
- **Dependencies:** Install the required Python packages:

   ```bash
   pip install pandas scikit-learn pickle
   ```

## Usage Instructions

1. **Prepare Your Data:**
   - Place your input Excel file (e.g., "MI 2 Rows of Couties North of IN-OH.xlsx") in the "Data" folder relative to your notebook's location. The file should contain the columns:
     - `MAIL_ADDR`
     - `MAIL_CITY`
     - `MAIL_STATE`
     - `MAIL_ZIP`
     - `OWNER_NAME_1`

2. **Trained Model and Vectorizer:**
   - Ensure you have the following files in the same directory as your notebook:
     - `logreg_classifier.pickle`: The trained logistic regression model.
     - `logreg_vectorizer.pickle`: The TF-IDF vectorizer used to transform the names.
     - `AR Top 10 Zips July 31 2024 - 3-9.99 ac Tested.xlsx`: A list of previously predicted human names used for additional filtering

3. **Modify Configuration (Optional):**
   - **`EXCEL_FILE_PATH`:** If your data is in a different location, update this variable in the notebook accordingly.
   - **`Suspected_Words`:** If you want to customize the list of words used to identify company names, modify this list.

4. **Run the Notebook:**
   - Execute the Python notebook. It will:
     - Load the data.
     - Remove rows with missing values and duplicates based on address.
     - Load the trained model and vectorizer.
     - Make predictions on the `OWNER_NAME_1` column.
     - Filter out potential company names based on the `Suspected_Words` list and additional human names filtering.
     - Save the cleaned results to a new Excel file with the suffix " SCRUBBED" in the same directory as your input data.

## Important Notes

- **Model Accuracy:** The accuracy of the model might vary depending on the nature of your dataset. If the model's performance isn't satisfactory, you might need to retrain it on a more representative dataset.
- **Customizable:** Feel free to modify the `Suspected_Words` list or add more sophisticated filtering rules to better suit your specific requirements.



## Troubleshooting

- **File Not Found:** Make sure your Excel file is in the correct location and the file path in the `EXCEL_FILE_PATH` variable is accurate.
- **Missing Columns:** Ensure your Excel file has the necessary columns (`MAIL_ADDR`, `MAIL_CITY`, `MAIL_STATE`, `MAIL_ZIP`, `OWNER_NAME_1`).
- **Model/Vectorizer Issues:** If you encounter problems loading the model or vectorizer, ensure they are in the correct format and were saved correctly during the training process.

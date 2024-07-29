import pandas as pd
import spacy
from spacy.training.example import Example
from spacy.util import minibatch, compounding
from sklearn.model_selection import train_test_split
import random
import os

def load_training_data(file_path):
    """
    Load training data from an Excel file and prepare it for training.

    Args:
        file_path (str): Path to the Excel file.
        sheet_name (str): Sheet name in the Excel file containing the training data.

    Returns:
        list: A list of training examples formatted for spaCy.
    """
    df = pd.read_excel(file_path)
    # Remove commas and strip whitespace
    df['Full Name'] = df['Full Name'].str.replace(',', '').str.strip()
    train_data = []
    for _, row in df.iterrows():
        text = row['Full Name']
        label = row['Name Type']
        if label == "Human Name":
            entities = [(0, len(text), "PERSON")]
        elif label == "Company Name":
            entities = [(0, len(text), "ORG")]
        train_data.append((text, {"entities": entities}))
    return train_data

def train_model(nlp, train_data, val_data, n_iter=10, dropout=0.5):
    """
    Train the NER model.

    Args:
        nlp (Language): The spaCy language model.
        train_data (list): List of training data.
        val_data (list): List of validation data.
        n_iter (int): Number of training iterations.
        dropout (float): Dropout rate.

    """
    pipe_exceptions = ["ner"]
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]
    
    with nlp.disable_pipes(*other_pipes):  # only train NER
        optimizer = nlp.resume_training()
        for itn in range(n_iter):
            random.shuffle(train_data)
            losses = {}
            batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.001))
            for batch in batches:
                examples = []
                for text, annotations in batch:
                    doc = nlp.make_doc(text)
                    example = Example.from_dict(doc, annotations)
                    examples.append(example)
                nlp.update(examples, drop=dropout, losses=losses)
            print(f"Iteration {itn + 1}/{n_iter}, Losses: {losses}")
            evaluate_model(nlp, val_data)

def evaluate_model(nlp, val_data):
    """
    Evaluate the NER model on validation data.

    Args:
        nlp (Language): The spaCy language model.
        val_data (list): List of validation data.
    """
    correct = 0
    total = 0
    for text, annotations in val_data:
        doc = nlp(text)
        ents = [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]
        true_ents = annotations['entities']
        if ents == true_ents:
            correct += 1
        total += 1
    accuracy = correct / total
    print(f"Validation Accuracy: {accuracy * 100:.2f}%")

# Main script
if __name__ == "__main__":
    # Load and prepare training data
    train_data = load_training_data('Training Data Scrubbing Names.xlsx')
    
    train_data, val_data = train_test_split(train_data, test_size=0.2, random_state=42)

    # Load pre-trained spaCy model
    nlp = spacy.load("en_core_web_sm")

    # Add NER pipe if not present
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner")
    else:
        ner = nlp.get_pipe("ner")

    # Add new labels
    ner.add_label("PERSON")
    ner.add_label("ORG")

    # Train the model
    train_model(nlp, train_data, val_data, n_iter=20)

    # Save the fine-tuned model
    model_directory = "custom_ner_model"
    os.makedirs(model_directory, exist_ok=True)
    nlp.to_disk(model_directory)

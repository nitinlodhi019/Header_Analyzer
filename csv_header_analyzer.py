import csv
import sys
from transformers import GPT2LMHeadModel, GPT2Tokenizer
def load_model_and_tokenizer(model_name='gpt2'):
    print(f"Loading model: {model_name}...")
    try:
        tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        tokenizer.pad_token = tokenizer.eos_token
        model = GPT2LMHeadModel.from_pretrained(model_name)
        print("Model and tokenizer loaded successfully.")
        return model, tokenizer
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Please ensure you have an internet connection for the first run to download the model.")
        print("Also, make sure 'transformers' and 'torch' are installed ('pip install transformers torch').")
        return None, None
def read_csv_headers(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            return [header.strip() for header in headers]
    except FileNotFoundError:
        print(f"Error: Input file not found at '{filepath}'")
        return None
    except StopIteration:
        print(f"Error: CSV file at '{filepath}' appears to be empty.")
        return []
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")
        return None

def generate_description(header, model, tokenizer):
    prompt = f"In a data file, the column header '{header.replace('_', ' ')}' means"
    inputs = tokenizer.encode(prompt, return_tensors='pt')
    outputs = model.generate(
        inputs,
        max_length=40,
        num_return_sequences=1,
        pad_token_id=tokenizer.eos_token_id,
        no_repeat_ngram_size=2,
        early_stopping=True
    )
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    description = generated_text[len(prompt):].strip()
    if '.' in description:
        description = description.split('.')[0]
    if '\n' in description:
        description = description.split('\n')[0]

    if not description:
        return "no specific description could be generated."
    return description[0].lower() + description[1:]
def main():
    if len(sys.argv) < 2:
        print("Usage: python csv_header_analyzer.py <path_to_input.csv>")
        sys.exit(1)

    input_filepath = sys.argv[1]
    output_filepath = "output.txt"
    headers = read_csv_headers(input_filepath)
    if headers is None:
        sys.exit(1)
    if not headers:
        print("No headers found. Exiting.")
        return

    model, tokenizer = load_model_and_tokenizer()
    if model is None:
        sys.exit(1)

    results = {}
    print("\n--- Generating Descriptions ---")
    for header in headers:
        print(f"Processing '{header}'...")
        description = generate_description(header, model, tokenizer)
        results[header] = description

    print("\n--- Results ---")
    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            for header, desc in results.items():
                line = f"{header} → {desc}"
                print(line)
                f.write(line + '\n')
        print(f"\nResults have been successfully written to {output_filepath}")
    except IOError as e:
        print(f"Error writing to output file: {e}")

if __name__ == "__main__":
    main()

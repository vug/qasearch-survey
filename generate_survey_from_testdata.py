"""
Script to prepare the QA-search test dataset for human testing by creating a
JSON file for each question to be used by a web-based survey.
"""
import os
import json

UNIGRAM_DATASET_FILE = r'C:\Users\veliu\Downloads\test_no_candidates_unigram_question.txt'
NGRAM_DATASET_FILE = r'C:\Users\veliu\Downloads\test_no_candidates_ngram_question.txt'
UNIGRAM_OUTPUT_FOLDER = r'C:\Users\veliu\Documents\GitRepos\qasearch-survey\static\unigram-questions'
NGRAM_OUTPUT_FOLDER = r'C:\Users\veliu\Documents\GitRepos\qasearch-survey\static\ngram-questions'


def main():
    print('processing unigrams...')
    generate_json_files_from_txt(UNIGRAM_DATASET_FILE, UNIGRAM_OUTPUT_FOLDER)
    print('processing ngrams...')
    generate_json_files_from_txt(NGRAM_DATASET_FILE, NGRAM_OUTPUT_FOLDER)


def generate_json_files_from_txt(dataset_file, output_folder):
    print('Starting...')
    with open(dataset_file, 'rt') as f:
        lines = f.readlines()
    print('{} lines read from dataset file.'.format(len(lines)))

    chunks = split_list_into_chunks(lines)
    print('{} chunks separted via empty lines.'.format(len(chunks)))

    for out_no, chunk in enumerate(chunks):
        output_file = '{n}.json'.format(n=out_no)
        qa = convert_chunk_to_qa(chunk)
        output_path = os.path.join(output_folder, output_file)
        with open(output_path, 'wt') as out:
            json.dump(qa, out, indent=1)
    print('Chunks have been converted to JSON files.')


def split_list_into_chunks(lines):
    """Group lines of unigram dataset into individual qa parts.

    Read lines of the dataset file into a list. Split list between lines that
    are empty."""
    qas = []
    qa = []
    for line in lines:
        if line == '\n':
            qas.append(qa)
            qa = []
            continue
        qa.append(line[:-1])  # remove '\n' at the end of each line
    return qas


def convert_chunk_to_qa(chunk):
    """Parse a chunk's list into a dictionary."""
    snippet_lines = chunk[:-1]
    question_answer_line = chunk[-1]
    snippets = [line.split(' ', 1)[1] for line in snippet_lines]  # rest after the first space
    question_answer_line = question_answer_line.split(' ', 1)[1]  # rest after the first space
    splitted = question_answer_line.split('\t')
    question = splitted[0]
    answer = splitted[1]
    d = {
        'snippets': snippets,
        'question': question,
        'answer': answer
    }
    return d


if __name__ == '__main__':
    main()

import jsonlines
import sys
from scorer import fever_score
from metrics.claim import Claim

claims = []
train_file = []
train_relevant_file = []
train_concatenate_file = []
train_predictions_file = []

if len(sys.argv) - 1 == 1:
    type_file = sys.argv[1]
    if type_file == 'train':
        train_file = "/content/DeFactoNLP/data/subsample_train.jsonl"
        train_relevant_file = "/content/DeFactoNLP/data/subsample_train_relevant_docs.jsonl"
        train_concatenate_file = "/content/DeFactoNLP/data/subsample_train_concatenation.jsonl"
        train_predictions_file = "/content/DeFactoNLP/predictions/predictions_train.jsonl"
    else:  # type_file == 'dev':
        train_file = "/content/DeFactoNLP/data/dev.jsonl"
        train_relevant_file = "/content/DeFactoNLP/data/dev_relevant_docs.jsonl"
        train_concatenate_file = "/content/DeFactoNLP/data/dev_sentence_selection.jsonl"
        train_predictions_file = "/content/DeFactoNLP/predictions/new_dev_bert_test.jsonl"
else:
    print("Needs to have one argument. Choose:")
    print("train")
    print("dev")
    print("test")
    exit(0)

train_file = jsonlines.open(train_file)
train_relevant_file = jsonlines.open(train_relevant_file)
train_concatenate_file = jsonlines.open(train_concatenate_file)
train_predictions_file = jsonlines.open(train_predictions_file)

train_set = []
train_relevant = []
train_concatenate = []
train_prediction = []

for lines in train_file:
    lines['claim'] = lines['claim'].replace("-LRB-", " ( ")
    lines['claim'] = lines['claim'].replace("-RRB-", " ) ")
    train_set.append(lines)

for lines in train_relevant_file:
    lines['claim'] = lines['claim'].replace("-LRB-", " ( ")
    lines['claim'] = lines['claim'].replace("-RRB-", " ) ")
    train_relevant.append(lines)

for lines in train_concatenate_file:
    lines['claim'] = lines['claim'].replace("-LRB-", " ( ")
    lines['claim'] = lines['claim'].replace("-RRB-", " ) ")
    train_concatenate.append(lines)

for lines in train_predictions_file:
    train_prediction.append(lines)

for claim in train_set:
    _claim = Claim(claim['id'], claim['claim'], claim['verifiable'])
    _claim.add_gold_evidences(claim['evidence'])
    _claim.add_gold_line(claim)
    _claim.label = claim['label']
    claims.append(_claim)
    # print(_claim.get_gold_documents())
    # print(len(_claim.gold_evidence))

for claim in train_relevant:
    _id = claim['id']
    _claim = Claim.find_by_id(_id)[0]
    # no search is needed... no information on gold about retrieval
    if not _claim.verifiable:
        continue

    _claim.add_predicted_docs(claim['predicted_pages'])
    _claim.add_predicted_sentences(claim['predicted_sentences'])
    #_claim.add_predicted_sentences_bert(claim['predicted_sentences'])


for claim in train_concatenate:
    _id = claim['id']
    _claim = Claim.find_by_id(_id)[0]

    if not _claim.verifiable:
        continue

    if "predicted_pages_ner" in claim:
        _claim.add_predicted_docs_ner(claim['predicted_pages_ner'])
    if "predicted_sentences_ner" in claim:
        print("")
        _claim.add_predicted_sentences_ner(claim['predicted_sentences_ner'])

    if "predicted_sentences_bert" in claim:
        _claim.add_predicted_sentences_bert(claim['predicted_sentences_bert'])
    else:
        if "predicted_sentences_triple" in claim:
            _claim.add_predicted_sentences_bert(claim['predicted_sentences_triple'])
        else:
            _claim.add_predicted_sentences_bert(claim['predicted_sentences'])
    # _claim.add_predicted_docs_ner(claim['predicted_pages_ner'])
    # _claim.add_predicted_sentences_ner(claim['predicted_sentences_ner'])
    if "predicted_pages_oie" in claim:
        _claim.add_predicted_docs_oie(claim['predicted_pages_oie'])
    # if not _claim.check_evidence_found_doc(_type="all"):
    #     print(str(_claim.get_gold_documents()) + " -- " + str(_claim.get_predicted_documents(_type="all")))


results = Claim.document_retrieval_stats(claims, _type="tfidf")

print("\n########################")
print("# Documents Only TFIDF #")
print("########################")
print("Precision (Document Retrieved): \t" + str(results[0]))
print("Recall (Relevant Documents): \t\t" + str(results[1]))
print("At least one Doc Found: \t\t" + str(results[2]))

results = Claim.document_retrieval_stats(claims, _type="ner")

print("\n######################")
print("# Documents Only NER #")
print("########################")
print("Precision (Document Retrieved): \t" + str(results[0]))
print("Recall (Relevant Documents): \t\t" + str(results[1]))
print("At least one Doc Found: \t\t" + str(results[2]))

results = Claim.document_retrieval_stats(claims, _type="oie")

print("\n######################")
print("# Documents Only OIE #")
print("########################")
print("Precision (Document Retrieved): \t" + str(results[0]))
print("Recall (Relevant Documents): \t\t" + str(results[1]))
print("At least one Doc Found: \t\t" + str(results[2]))

results = Claim.document_retrieval_stats(claims, _type="all")

print("\n######################")
print("# Documents for All #")
print("######################")
print("Precision (Document Retrieved): \t" + str(results[0]))
print("Recall (Relevant Documents): \t\t" + str(results[1]))
print("At least one Doc Found: \t\t" + str(results[2]))

results = Claim.evidence_extraction_stats(claims, _type="tfidf")

print("\n#################################")
print("# Possible Sentences Only TFIDF #")
print("#################################")
print("Precision (Sentences Retrieved): \t" + str(results[0]))
print("Recall (Relevant Sentences): \t\t" + str(results[1]))
print("\nIF DOCUMENT WAS FOUND CORRECTLY:")
print("Precision (Sentences Retrieved): \t" + str(results[2]))
print("Recall (Relevant Sentences): \t\t" + str(results[3]))

results = Claim.evidence_extraction_stats(claims, _type="ner")

print("\n###############################")
print("# Possible Sentences Only NER #")
print("###############################")
print("Precision (Sentences Retrieved): \t" + str(results[0]))
print("Recall (Relevant Sentences): \t\t" + str(results[1]))
print("\nIF DOCUMENT WAS FOUND CORRECTLY:")
print("Precision (Sentences Retrieved): \t" + str(results[2]))
print("Recall (Relevant Sentences): \t\t" + str(results[3]))

results = Claim.evidence_extraction_stats(claims, _type="bert")

print("\n################################")
print("# Possible Sentences Only BERT #")
print("################################")
print("Precision (Sentences Retrieved): \t" + str(results[0]))
print("Recall (Relevant Sentences): \t\t" + str(results[1]))
print("\nIF DOCUMENT WAS FOUND CORRECTLY:")
print("Precision (Sentences Retrieved): \t" + str(results[2]))
print("Recall (Relevant Sentences): \t\t" + str(results[3]))

results = Claim.evidence_extraction_stats(claims, _type="all")

print("\n###############################")
print("# Possible Sentences For BOTH #")
print("###############################")
print("Precision (Sentences Retrieved): \t" + str(results[0]))
print("Recall (Relevant Sentences): \t\t" + str(results[1]))
print("\nIF DOCUMENT WAS FOUND CORRECTLY:")
print("Precision (Sentences Retrieved): \t" + str(results[2]))
print("Recall (Relevant Sentences): \t\t" + str(results[3]))

# scores from fever
new_train_set = []
for claim in train_prediction:
    _id = claim['id']
    _claim = Claim.find_by_id(_id)[0]
    new_train_set.append(_claim.line)

print(len(new_train_set))
results = fever_score(train_prediction, actual=new_train_set)

print("\n#########")
print("# FEVER #")
print("#########")
print("Strict_score: \t\t\t" + str(results[0]))
print("Acc_score: \t\t\t" + str(results[1]))
print("Precision: \t\t\t" + str(results[2]))
print("Recall: \t\t\t" + str(results[3]))
print("F1-Score: \t\t\t" + str(results[4]))

predictions_if_doc_found = []
claims_if_doc_found = []

for claim in train_prediction:
    _id = claim['id']
    _claim = Claim.find_by_id(_id)[0]

    if _claim.check_evidence_found_doc(_type="all"):
        claims_if_doc_found.append(_claim.line)
        predictions_if_doc_found.append(claim)

# scores from fever
results = fever_score(predictions_if_doc_found, actual=claims_if_doc_found)

print("\n#######################")
print("# FEVER If Doc Found! #")
print("#######################")
print("Strict_score: \t\t\t" + str(results[0]))
print("Acc_score: \t\t\t" + str(results[1]))
print("Precision: \t\t\t" + str(results[2]))
print("Recall: \t\t\t" + str(results[3]))
print("F1-Score: \t\t\t" + str(results[4]))

predictions_if_evidence_found = []
claims_if_evidence_found = []

for claim in train_prediction:
    _id = claim['id']
    _claim = Claim.find_by_id(_id)[0]

    if _claim.check_evidence_was_found(_type="bert"):
        claims_if_evidence_found.append(_claim.line)
        predictions_if_evidence_found.append(claim)

# scores from fever
results = fever_score(predictions_if_evidence_found, actual=claims_if_evidence_found)

print("\n############################")
print("# FEVER If Sentence Found! #")
print("############################")
print("Strict_score: \t\t\t" + str(results[0]))
print("Acc_score: \t\t\t" + str(results[1]))
print("Precision: \t\t\t" + str(results[2]))
print("Recall: \t\t\t" + str(results[3]))
print("F1-Score: \t\t\t" + str(results[4]))

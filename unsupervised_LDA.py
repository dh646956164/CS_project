import json
from sklearn.feature_extraction.text import CountVectorizer
from gensim.corpora import Dictionary
from gensim.models import LdaModel
from gensim.matutils import Sparse2Corpus

# Load the comments
with open("availability_comment_classification.json", "r") as file:
    data = json.load(file)

# Preprocess the comments
comments = [item['Comment Body'] for item in data]
vectorizer = CountVectorizer(stop_words='english')
X = vectorizer.fit_transform(comments)

# Convert the sparse matrix to a gensim corpus
corpus = Sparse2Corpus(X, documents_columns=False)

# Create a dictionary mapping id -> word
id2word = {id: word for word, id in vectorizer.vocabulary_.items()}

# Train the LDA model
lda_model = LdaModel(corpus, num_topics=38, id2word=id2word, passes=20, update_every=1, chunksize=10000, alpha='auto', eta='auto')

# Define a mapping from topic IDs to classification names
# You will need to adjust this mapping based on your understanding of the data and your business needs
topic_to_classification = {
    0: "Naming Conventions: Comments that suggest changing the name of a variable, method etc. Or indicate some other problem with the naming of a code element",
    1: "Code Style & Formatting: Comments that indicate Inconsistent Indentation, incorrect use of spacing, blank lines, unneeded long lines, bracket usage, improving readability, maintaining consistency or anything else related to the style and formatting of the code",
    2: "Code Complexity: Comments that indicate code is excessively complex. Suggesting things like simplifying logic, reducing sub-routine length",
    3: "Duplication: Comments that suggest removing duplication or semantic duplication",
    4: "Using standard methods: Comments that suggest using standard methods or pre-existing solutions",
    5: "Moving Functionality: Comments that suggest moving a function, part of a function, a module, or a class to a different part of the code, grouping related code, moving statements",
    6: "Removing Dead Code: Comments that suggest removing dead code, or semantic dead code i.e., unused code",
    7: "Visibility: Code element has the wrong scope, i.e., public element should be private",
    8: "Depreciated Functions: Comments that indicate the use of old or depreciated functions.",
    9: "Inline Comments: Comments that suggest that inline comments are missing or incorrect.",
    10: "Documentation: Comments that suggest issues in documentation, such as incorrect information, wording and grammar issues, or incorrect licensing details",
    11: "Logging: Comments that indicate that logging is needed.",
    12: "Feature Completeness: Comments that suggest that a feature is not entirely implemented, does not meet stakeholder requirements",
    13: "Wrong Location: Comments that indicate that an operation has been executed at the wrong place in the code, i.e., should have been performed earlier or later",
    14: "Variable Initialisation: Comments that indicate that a variable has not been instantiated before use.",
    15: "Logic Error: Comments that indicate an error in the logic of the code.",
    16: "Comparison Statements: Comments that indicate a error in a comparison statement.",
    17: "Function Parameters: Comments that indicate missing or incorrect function parameters, like incorrect use of void parameters.",
    18: "Function Calls: Comments that indicate missing or incorrect function calls",
    19: "Unvalidated Element: Comments that indicate that a variable or function return value isn’t checked before usage",
    20: "Element Type: Comments that indicate that a code element is of the wrong type",
    21: "Issues with Outside Code: Comments that indicate that there are issues caused by code that is not in the review",
    22: "Unhandled Errors/Exceptions: Comments that indicate unhandled errors or exceptions",
    23: "Input Validation: Comments that suggest that input validation is needed.",
    24: "Compatibility Issues: Other Compatibility Issues, Mobile device compatibility, Browser Compatibility, Software version compatibility, API Compatibility",
    25: "Security Concerns: Input Sanitisation, Data Encryption, Input sanitization, Authorization, Authentication, Other Security Issues",
    26: "Algorithmic Efficiency/Performance: Comments that mention the efficiency or performance of an algorithm.",
    27: "Data & Resource Management: Closing buffers/thread management, memory usage, caching",
    28: "Execution Time: Comments that indicate problems with the execution time of the code.",
    29: "Network Usage: Comments that indicate problems with network usage.",
    30: "Test Coverage: Comments that indicate issues with test coverage.",
    31: "Test Cases: Comments that indicate that incorrect test cases",
    32: "Test Results: Comments that question the results of a test.",
    33: "Other Test related: Any other test related comments.",
    34: "Social Communication: Comments that are not talking about code but are just social communication.",
    35: "Knowledge Transfer: Comments that explain concepts or link to additional resources to help to transfer knowledge.",
    36: "Understanding: Comments that ask questions about the code to further their understanding.",
    37: "Misc: Comments talking about things like Git Workflow, Project Management, or anything else not stated in other categories",

}

# Predict the topic for each comment and add the topic information to the JSON data
for i, item in enumerate(data):
    # Get the topic ID and weight
    topic_info = [(int(topic_id), float(weight)) for topic_id, weight in lda_model[corpus[i]]]

    # Replace the topic ID with the topic name using the topic_to_classification dictionary
    topic_info = [(topic_to_classification[topic_id], weight) for topic_id, weight in topic_info]

    # Sort the topic info by weight in descending order
    topic_info = sorted(topic_info, key=lambda x: x[1], reverse=True)

    item['Comment Classification'] = topic_info

# Save the JSON data with the added topic information
with open("availability_comment_classification_with_topics.json", "w") as file:
    json.dump(data, file, indent=4)


# -*- coding: utf-8 -*-
"""Tiffany_wTuning(1).ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/18xDsMhl-4v4GW0zOvp3veUlanIT3ONDd

[Working File
](https://colab.research.google.com/drive/1xoZe3dusVXtQPE7kCXMm1q8K-K1CAoo2?usp=sharing) | Combine code from Ziva and Silvia | Rename Columns | Include Testing Algorithms
"""

#imports

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import sklearn
import streamlit as st
import tpot
from tpot import TPOTClassifier
import pkg_resources


from sklearn.preprocessing import OrdinalEncoder
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_selection import chi2
from scipy.stats import pointbiserialr
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.model_selection import train_test_split
from tabulate import tabulate
from matplotlib.patches import Patch


labelEncode = LabelEncoder()



raw = pd.read_csv('dataset.csv')

"""# 
# Display an overview of the dataset

Task: Select and combine columns -> feat_select

Columns we have chosen
*   INSTN_CLGS_W116
*   INSTN_K12_W116
*   EMPLSIT_W116
*   WHADVANT_W116
*   ISSUECONG_ECON_W116
*   ISSUECONG_IMM_W116
*   F_VOTED2020
"""

feat_select = pd.DataFrame(raw, columns=[                    #select features and save copy
    'ISSUECONG_ECON_W116',
    'ISSUECONG_IMM_W116',
    'EMPLSIT_W116',
    'INSTN_CLGS_W116',
    'INSTN_K12_W116',
    'WHADVANT_W116',
    'F_VOTED2020'
]).copy()

print("Selected Features:")
for column in feat_select.columns:
    print(column)

feat_select

"""
# Cleaned Data
"""

# Clean EMPLSIT_W116
feat_select['EMPLSIT_W116'] = feat_select['EMPLSIT_W116'].astype(str).replace("No Answer", "99").astype(int)
feat_select['EMPLSIT_W116'] = feat_select['EMPLSIT_W116'].replace(99, 3)  # Replace placeholder values with a valid option (e.g., mode)
feat_select['EMPLSIT_W116'] = 6 - feat_select['EMPLSIT_W116']  # Reverse the scale

#Clean ISSUECONG_ECON_W116 and ISSUECONG_IMM_W116
feat_select['ISSUECONG_ECON_W116'] = feat_select['ISSUECONG_ECON_W116'].fillna(3).replace(['99', ' '], '3')
feat_select['ISSUECONG_IMM_W116'] = feat_select['ISSUECONG_IMM_W116'].fillna(3).replace(['99', ' '], '3')

#Clean WHADVANT_W116 and INSTN_CLGS_W116/INSTN_K12_W116
feat_select['INSTN_CLGS_W116'] = feat_select['INSTN_CLGS_W116'].replace(99, "No Answer")
feat_select['INSTN_K12_W116'] = feat_select['INSTN_K12_W116'].replace(99, "No Answer")
feat_select['WHADVANT_W116'] = feat_select['WHADVANT_W116'].replace(99, 1)
feat_select['WHADVANT_W116'] = 5 - feat_select['WHADVANT_W116']  # Reverse scale

feat_select.info()

# Step 1: Drop rows where F_VOTED2020 is an empty space (' ')
feat_select = feat_select[feat_select['F_VOTED2020'] != ' '].copy()  # Create a new copy to avoid warnings
print("After dropping empty spaces:", feat_select['F_VOTED2020'].unique())

# Step 2: Create a new column F_VOTED2020_encoded and replace '99' with '2'
feat_select.loc[:, 'F_VOTED2020_encoded'] = feat_select['F_VOTED2020'].replace('99', '2')
print("After replacing '99' with '2':", feat_select['F_VOTED2020_encoded'].unique())

# Step 4: Combine categories 1 and 2 as 0 (did not vote), and keep 3 as 1 (voted)
feat_select.loc[:, 'F_VOTED2020_encoded'] = feat_select['F_VOTED2020_encoded'].replace({1: 0, 2: 0, 3: 1})
print("After combining categories:", feat_select['F_VOTED2020_encoded'].unique())

feat_select.loc[:, 'F_VOTED2020_encoded'] = pd.to_numeric(feat_select['F_VOTED2020_encoded'], errors='coerce')


# Step 3: Convert F_VOTED2020_encoded to integer type
feat_select.loc[:, 'F_VOTED2020_encoded'] = feat_select['F_VOTED2020_encoded'].astype(int)
print("After converting to integer:", feat_select['F_VOTED2020_encoded'].unique())


# Verify the cleaned column
print(feat_select['F_VOTED2020_encoded'].value_counts())
# Display the cleaned dataset
feat_select
# Replace dtype object to int or float

# Replace "No Answer" with a placeholder numeric value
feat_select['INSTN_CLGS_W116'] = feat_select['INSTN_CLGS_W116'].astype(str).replace("No Answer", "99").astype(int)
feat_select['INSTN_K12_W116'] = feat_select['INSTN_K12_W116'].astype(str).replace("No Answer", "99").astype(int)

# Replace object dType due to non-numerical characters (' ', "99", etc)
feat_select['EMPLSIT_W116'] = feat_select['EMPLSIT_W116'].astype(int)

"""
# Map and Encode Features
"""


# Map and encode features
whadvant_mapping = {
    1: "A great deal",
    2: "A fair amount",
    3: "Not too much",
    4: "Not at all",
    99: "No Answer"
}
emplsit_mapping = {
    1: "Work full time for pay",
    2: "Work part time for pay",
    3: "Not currently working for pay",
    4: "Unable to work due to a disability",
    5: "Retire"
}
instn_mapping = {
    1: "Positive Effect",
    2: "Negative Effect",
    99: "No Answer"
}
f_voted2020_mapping = {
    0: "Did not vote",
    1: "Voted"
}

# Apply mappings (dynamic)
mapped_whadvant = feat_select['WHADVANT_W116'].map(whadvant_mapping)
mapped_emplsit = feat_select['EMPLSIT_W116'].map(emplsit_mapping)
mapped_instn_clgs = feat_select['INSTN_CLGS_W116'].map(instn_mapping)
mapped_instn_k12 = feat_select['INSTN_K12_W116'].map(instn_mapping)
mapped_f_voted2020 = feat_select['F_VOTED2020'].map(f_voted2020_mapping)

from sklearn.preprocessing import OneHotEncoder
hotEncoder = OneHotEncoder(sparse_output=False)

# One-hot encoding for INSTN_CLGS_W116
INSTN_CLGS_W116_encoded = hotEncoder.fit_transform(feat_select[['INSTN_CLGS_W116']])
INSTN_CLGS_W116_encoded = pd.DataFrame(
    INSTN_CLGS_W116_encoded,
    columns=hotEncoder.get_feature_names_out(['INSTN_CLGS_W116'])
)
# One-hot encoding for INSTN_K12_W116
INSTN_K12_W116_encoded = hotEncoder.fit_transform(feat_select[['INSTN_K12_W116']])
INSTN_K12_W116_encoded = pd.DataFrame(
    INSTN_K12_W116_encoded,
    columns=hotEncoder.get_feature_names_out(['INSTN_K12_W116'])
)

# One-Hot Encoding for EMPLSIT_W116
EMPLSIT_W116_encoded = hotEncoder.fit_transform(feat_select[['EMPLSIT_W116']])
EMPLSIT_W116_encoded = pd.DataFrame(
    EMPLSIT_W116_encoded,
    columns=hotEncoder.get_feature_names_out(['EMPLSIT_W116'])
)

# One-Hot Encoding for WHADVANT_W116
WHADVANT_W116_encoded = hotEncoder.fit_transform(feat_select[['WHADVANT_W116']])
WHADVANT_W116_encoded = pd.DataFrame(
    WHADVANT_W116_encoded,
    columns=hotEncoder.get_feature_names_out(['WHADVANT_W116'])
)

#Convert remaining object features to numerical
feat_select['ISSUECONG_ECON_W116'] = pd.to_numeric(feat_select['ISSUECONG_ECON_W116'], errors='coerce')
feat_select['ISSUECONG_IMM_W116'] = pd.to_numeric(feat_select['ISSUECONG_IMM_W116'], errors='coerce')
feat_select['F_VOTED2020'] = pd.to_numeric(feat_select['F_VOTED2020'], errors='coerce')
feat_select = feat_select.dropna(subset=['F_VOTED2020']).copy()
feat_select['F_VOTED2020'] = feat_select['F_VOTED2020'].astype(int)

feat_select['F_VOTED2020_encoded'] = feat_select['F_VOTED2020_encoded'].replace({' ': None, '99': '2'})

feat_select.info()

# Add all one-hot encoded features into the dataset
feat_select = pd.concat([
    feat_select,
    INSTN_CLGS_W116_encoded,
    INSTN_K12_W116_encoded,
    EMPLSIT_W116_encoded,
    WHADVANT_W116_encoded,
], axis=1)

feat_select.info()
feat_select

"""
# F_Voted2020 Analysis
"""


plt.figure(figsize=(8, 5))  #new figure for each plot
feat_select['F_VOTED2020_encoded'].value_counts().sort_index().plot(
        kind='bar')

"""

*   Importance of Economy
*   Importance of Immigration
*   White Advantage
*   Employment Status
"""

feat_select.info()

#Removes the warning from output regarding future changes to Seaborn
#Add legend

def plot_encoded_distribution(data, title, x_label, y_label, palette, legend_labels=None):
    """
    Plot the distribution of encoded feature categories with individual colors for each bar.

    Parameters:
    - data: A pandas DataFrame containing 'Category' and 'Sum' columns.
    - title: Title of the plot.
    - x_label: Label for the x-axis.
    - y_label: Label for the y-axis.
    - palette: List of colors for individual bars.
    - legend_labels: List of labels for the legend (default is None).
    """
    # Create the bar plot with individual colors for each bar
    plt.figure(figsize=(8, 5))
    sns.barplot(
        data=data,
        x='Category',
        y='Sum',
        hue='Category',
        palette=palette  # Assign colors directly from the palette
    )
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    # Add custom legend if provided
    if legend_labels:
        handles = [Patch(facecolor=palette[i], label=legend_labels[i]) for i in range(len(legend_labels))]
        plt.legend(handles=handles, loc='best', title="Legend")

    plt.show()

# Aggregated distribution for INSTN_CLGS_W116
encoded_instn_clgs = feat_select[['INSTN_CLGS_W116_1', 'INSTN_CLGS_W116_2', 'INSTN_CLGS_W116_99']]
encoded_instn_clgs_sum = encoded_instn_clgs.sum().reset_index()
encoded_instn_clgs_sum.columns = ['Category', 'Sum']

# Get pastel colors for the number of bars
pastel_palette = sns.color_palette("pastel", len(encoded_instn_clgs_sum))

plot_encoded_distribution(
    data=encoded_instn_clgs_sum,
    title="INSTN_CLGS_W116 Features",
    x_label="Feature Answers",
    y_label="# of Answers",
    palette=pastel_palette,  # Use pastel colors
    legend_labels=["Positive Effect", "Negative Effect", "No Answer"]  # Close parentheses here
)

# Aggregated distribution for INSTN_K12_W116
encoded_instn_k12 = feat_select[['INSTN_K12_W116_1', 'INSTN_K12_W116_2', 'INSTN_K12_W116_99']]
encoded_instn_k12_sum = encoded_instn_k12.sum().reset_index()
encoded_instn_k12_sum.columns = ['Category', 'Sum']

# Get pastel colors for the number of bars
pastel_palette = sns.color_palette("pastel", len(encoded_instn_k12_sum))

plot_encoded_distribution(
    data=encoded_instn_k12_sum,
    title="INSTN_K12_W116 Features",
    x_label="Feature Answers",
    y_label="# of Answers",
    palette=pastel_palette,  # Use pastel colors
    legend_labels=["Positive Effect", "Negative Effect", "No Answer"]
)

# Aggregated distribution for EMPLSIT_W116
encoded_emplsit = feat_select[['EMPLSIT_W116_1', 'EMPLSIT_W116_2', 'EMPLSIT_W116_3', 'EMPLSIT_W116_4', 'EMPLSIT_W116_5']]
encoded_emplsit_sum = encoded_emplsit.sum().reset_index()
encoded_emplsit_sum.columns = ['Category', 'Sum']

# Get pastel colors for the number of bars
pastel_palette = sns.color_palette("pastel", len(encoded_emplsit_sum))

plot_encoded_distribution(
    data=encoded_emplsit_sum,
    title="EMPLSIT_W116 Features",
    x_label="Feature Answers",
    y_label="# of Answers",
    palette=sns.color_palette("pastel", len(encoded_emplsit_sum)),  # Adjust colors dynamically
    legend_labels=[
        "Retire",
        "Unable to work due to a disability",
        "Not currently working for pay",
        "Work part time for pay",
        "Work full time for pay"
    ]
)

# Aggregated distribution for WHADVANT_W116
encoded_whadvant = feat_select[['WHADVANT_W116_1', 'WHADVANT_W116_2', 'WHADVANT_W116_3', 'WHADVANT_W116_4']]
encoded_whadvant_sum = encoded_whadvant.sum().reset_index()
encoded_whadvant_sum.columns = ['Category', 'Sum']

# Get pastel colors for the number of bars
pastel_palette = sns.color_palette("pastel", len(encoded_whadvant_sum))

plot_encoded_distribution(
    data=encoded_whadvant_sum,
    title="WHADVANT_W116 Features",
    x_label="Feature Answers",
    y_label="# of Answers",
    palette=pastel_palette,  # Use pastel colors
    legend_labels=[
        "Not at all",
        "Not too much",
        "A fair amount",
        "A great deal"
    ]
)
# st.dataframe(pastel_palette)

"""
# Rename Columns For Improved Readability
Consists of the encoded features only | Original columns will retain their name"""

feat_select.info()

# Rename columns for readability (including both F_VOTED2020 versions)
feat_select = feat_select.rename(columns={
    # Original Features
    'ISSUECONG_ECON_W116': 'Importance of Economy',
    'ISSUECONG_IMM_W116': 'Importance of Immigration',
    'EMPLSIT_W116': 'Employment Status',
    'INSTN_CLGS_W116': 'College Effect',
    'INSTN_K12_W116': 'K12 Effect',
    'WHADVANT_W116': 'White Advantage',
    'F_VOTED2020': 'Original Voted in 2020',
    'F_VOTED2020_encoded': 'Voted in 2020',

    # Encoded Features
    'INSTN_CLGS_W116_1': 'College Positive Effect',
    'INSTN_CLGS_W116_2': 'College Negative Effect',
    'INSTN_CLGS_W116_99': 'College No Answer',
    'INSTN_K12_W116_1': 'K12 Positive Effect',
    'INSTN_K12_W116_2': 'K12 Negative Effect',
    'INSTN_K12_W116_99': 'K12 No Answer',
    'EMPLSIT_W116_1': 'Employment: Retired',
    'EMPLSIT_W116_2': 'Employment: Unable to Work',
    'EMPLSIT_W116_3': 'Employment: Not Working',
    'EMPLSIT_W116_4': 'Employment: Part-Time',
    'EMPLSIT_W116_5': 'Employment: Full-Time',
    'WHADVANT_W116_1': 'White Advantage: Not at All',
    'WHADVANT_W116_2': 'White Advantage: Not Too Much',
    'WHADVANT_W116_3': 'White Advantage: Fair Amount',
    'WHADVANT_W116_4': 'White Advantage: Great Deal'
}, inplace=False)

# Verify the renamed columns
print(feat_select.info())

#Make new feat_select_encoded to omit 5 original features from correlation findings
# List of readable feature names to drop
features_to_drop = [
    'K12 Effect',
    'College Effect',
    'Employment Status',
    'White Advantage',
    'Original Voted in 2020'
]

# Create a new DataFrame excluding the original features
feat_select_encoded = feat_select.drop(columns=features_to_drop)

feat_select_encoded.info()

"""# Startifying Label
Strat F_VOTED2020 to ensure the model distributes this evenly

-Training Set (78% voters, 14% non-voters, etc.):
    The model will see training data that reflects the actual class distribution, helping it learn patterns that apply to the full dataset.

-Test Set (similar distribution):
    The test set will also represent the real-world distribution, so when you evaluate your model, you’ll get realistic performance metrics.

"""

# Step 1: Drop rows where 'Voted in 2020' contains NaN values
feat_select = feat_select.dropna(subset=['Voted in 2020']).copy()

# Step 2: Reset the index of the DataFrame
feat_select.reset_index(drop=True, inplace=True)

# Step 3: Use the encoded DataFrame and ensure correct column names
split = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)

# Step 4: Stratify based on 'Voted in 2020'
for train_index, test_index in split.split(feat_select, feat_select["Voted in 2020"]):
    strat_train_set = feat_select.loc[train_index]
    strat_test_set = feat_select.loc[test_index]

print("Training Set Distribution:")
print(strat_train_set["Voted in 2020"].value_counts(normalize=True))

print("Test Set Distribution:")
print(strat_test_set["Voted in 2020"].value_counts(normalize=True))

# Define the proportion function
def voted_cat_proportions(data):
    # Use the correct, renamed column: 'Voted in 2020'
    return data["Voted in 2020"].value_counts() / len(data)

# Perform a stratified split
split = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)

# Create stratified train and test sets, use 'Voted in 2020' and the original dataframe (feat_select)
for train_idx, test_idx in split.split(feat_select, feat_select["Voted in 2020"]):
    # Select only the encoded features for the training and test sets
    strat_train_set = feat_select_encoded.loc[train_idx]
    strat_test_set = feat_select_encoded.loc[test_idx]

# Perform a random split for comparison
train_set, test_set = train_test_split(feat_select_encoded, test_size=0.2, random_state=42)

# Create a comparison DataFrame
compare_props = pd.DataFrame({
    "Overall": voted_cat_proportions(feat_select),  # Use original dataframe to calculate overall proportions
    "Stratified": voted_cat_proportions(strat_test_set),  # Proportions from the stratified split
    "Random": voted_cat_proportions(test_set)  # Proportions from the random split
}).sort_index()

# Calculate percentage errors
compare_props["Random %error"] = 100 * (compare_props["Random"] / compare_props["Overall"] - 1)
compare_props["Stratified %error"] = 100 * (compare_props["Stratified"] / compare_props["Overall"] - 1)

compare_props

"""Why Stratified is Ideal:

    -Stratified sampling ensures that every class in F_VOTED2020 is proportionally represented in both training and test sets, even for rare -classes like 99.
    This leads to a more representative test set and fair evaluation of the model.

"""

one_hot_groups = {
    "College Effect": ['College Positive Effect', 'College Negative Effect', 'College No Answer'],
    "K12 Effect": ['K12 Positive Effect', 'K12 Negative Effect', 'K12 No Answer'],
    "Employment Status": ['Employment: Retired', 'Employment: Unable to Work', 'Employment: Not Working', 'Employment: Part-Time', 'Employment: Full-Time'],
    "White Advantage": ['White Advantage: Not at All', 'White Advantage: Not Too Much', 'White Advantage: Fair Amount', 'White Advantage: Great Deal']
}

mask = pd.DataFrame(0, index=feat_select_encoded.columns, columns=feat_select_encoded.columns, dtype=bool)

for group in one_hot_groups.values():
    for col1 in group:
        for col2 in group:
            if col1 != col2:
                mask.at[col1, col2] = True
                mask.at[col2, col1] = True  # Symmetric masking

# Select only numeric columns
numeric_columns = feat_select_encoded.select_dtypes(include=[np.number])
corr_matrix = numeric_columns.corr()

print("Columns included in correlation calculation:")
print(numeric_columns.columns.tolist())

"""
# Correlation | List of Top Correlations 
"""

import pandas as pd
import numpy as np
from tabulate import tabulate

# Assuming feat_select_encoded contains all the features including one-hot encoded features
# Compute the correlation matrix for all features
corr_matrix = feat_select_encoded.corr()

# Create a DataFrame from the correlation matrix
corr_pairs = []

for i in range(len(corr_matrix.columns)):
    for j in range(i + 1, len(corr_matrix.columns)):
        feature_1 = corr_matrix.columns[i]
        feature_2 = corr_matrix.columns[j]
        correlation = corr_matrix.iloc[i, j]
        corr_pairs.append((feature_1, feature_2, correlation))

# Create a DataFrame of correlation pairs
sorted_corr_values = pd.DataFrame(corr_pairs, columns=["Feature1", "Feature2", "Correlation"])

# Sort by absolute correlation in descending order
sorted_corr_values = sorted_corr_values.sort_values(by="Correlation", key=abs, ascending=False)

# Define groups of one-hot encoded features to avoid comparing within groups
groups = {
    "College": ["College Positive Effect", "College Negative Effect", "College No Answer"],
    "K12": ["K12 Positive Effect", "K12 Negative Effect", "K12 No Answer"],
    "Employment": [
        "Employment: Retired",
        "Employment: Unable to Work",
        "Employment: Not Working",
        "Employment: Part-Time",
        "Employment: Full-Time",
    ],
    "White Advantage": [
        "White Advantage: Not at All",
        "White Advantage: Not Too Much",
        "White Advantage: Fair Amount",
        "White Advantage: Great Deal",
    ],
}

# Create a set of invalid pairs (comparisons within the same group)
invalid_pairs = set()
for group, features in groups.items():
    for i in range(len(features)):
        for j in range(i + 1, len(features)):
            invalid_pairs.add((features[i], features[j]))
            invalid_pairs.add((features[j], features[i]))  # Add reverse pair for symmetry

# Remove invalid pairs from the sorted correlation values
filtered_corr_values = sorted_corr_values[
    ~sorted_corr_values[["Feature1", "Feature2"]].apply(tuple, axis=1).isin(invalid_pairs)
]

# Filter to show only positive correlations
filtered_corr_values_positive = filtered_corr_values[filtered_corr_values["Correlation"] > 0]

# Sort values by correlation in descending order
filtered_corr_values_positive = filtered_corr_values_positive.sort_values(by="Correlation", ascending=False)

# Display all positive correlations
print("All Positive Correlations (after filtering within groups):")

print(tabulate(filtered_corr_values_positive, headers="keys", tablefmt="fancy_grid"))
st.subheader("All Positive Correlations (after filtering within groups):")
st.dataframe(filtered_corr_values_positive)

st.header("Heat Map to Visualize Correlations")

# Step 1: Calculate the correlation matrix for the dataset
corr = feat_select_encoded.corr()

# Step 2: Create a mask for the upper triangle to avoid duplicate correlations
mask = np.triu(np.ones_like(corr, dtype=bool))

# Step 3: Define groups of one-hot encoded features
groups = {
    "College": ["College Positive Effect", "College Negative Effect", "College No Answer"],
    "K12": ["K12 Positive Effect", "K12 Negative Effect", "K12 No Answer"],
    "Employment": [
        "Employment: Retired",
        "Employment: Unable to Work",
        "Employment: Not Working",
        "Employment: Part-Time",
        "Employment: Full-Time",
    ],
    "White Advantage": [
        "White Advantage: Not at All",
        "White Advantage: Not Too Much",
        "White Advantage: Fair Amount",
        "White Advantage: Great Deal",
    ],
}

# Step 4: Create a set of invalid pairs (comparisons within the same group)
invalid_pairs = set()
for group, features in groups.items():
    for i in range(len(features)):
        for j in range(i + 1, len(features)):
            invalid_pairs.add((features[i], features[j]))
            invalid_pairs.add((features[j], features[i]))  # Add reverse pair for symmetry

# Step 5: Create a mask for the invalid pairs
mask_invalid = np.zeros_like(corr, dtype=bool)

# Get feature names from the correlation matrix
features = list(corr.columns)

for (feature1, feature2) in invalid_pairs:
    if feature1 in features and feature2 in features:
        idx1, idx2 = features.index(feature1), features.index(feature2)
        mask_invalid[idx1, idx2] = True
        mask_invalid[idx2, idx1] = True

# Step 6: Combine upper triangle mask with the invalid mask
combined_mask = mask | mask_invalid

# Step 7: Create the heatmap
f, ax = plt.subplots(figsize=(11, 9))  # Adjust figure size for better readability
cmap = sns.diverging_palette(230, 20, as_cmap=True)

sns.heatmap(
    corr,
    mask=combined_mask,  # Apply the combined mask
    cmap=cmap,
    vmax=0.3,  # Limit maximum value of the color bar
    center=0,
    square=True,
    linewidths=0.5,
    annot=True,
    fmt=".2f",
    cbar_kws={"shrink": 0.5}
)

plt.title("Heatmap of Correlations (Excluding One-Hot Encoded Comparisons)")
plt.xticks(rotation=45, ha='right')  # Rotate labels for better readability
plt.tight_layout()  # Adjust layout to fit everything well
plt.show()
st.pyplot(f)


st.header("Models")
st.subheader("Linear Regression")


feat_select_encoded = feat_select_encoded.dropna().copy()
st.dataframe(feat_select_encoded)

st.subheader("Logistic Regression")

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# Step 1: Prepare the data
X = feat_select_encoded.drop(columns=["Voted in 2020"])  # Features
y = feat_select_encoded["Voted in 2020"]  # Target variable

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 2: Train a logistic regression model with class weighting
log_reg = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
log_reg.fit(X_train, y_train)

# Step 3: Make predictions
y_pred = log_reg.predict(X_test)

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
print("\nConfusion Matrix:")
print(tabulate(cm, headers=["Predicted 0", "Predicted 1"], tablefmt="fancy_grid"))
st.subheader("Confusion Matrix")
st.dataframe(cm)

# Classification Report
print("\nClassification Report:")
print(classification_report(y_test, y_pred, digits=2))
st.subheader("Classification Report")
target_names = ["class 0", "class 1"]
st.dataframe(
    classification_report(y_test, y_pred, target_names=target_names, output_dict=True)
)

# Accuracy Score
accuracy = accuracy_score(y_test, y_pred)
print(f"\nAccuracy Score: {accuracy:.2%}")
st.subheader("Accuracy Score")
st.write(f"{accuracy:.2%}")


st.subheader("Random Forest")

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# Train a Random Forest model
rf_model = RandomForestClassifier(random_state=42, class_weight='balanced', n_estimators=100)
rf_model.fit(X_train, y_train)

# Make predictions
y_pred_rf = rf_model.predict(X_test)

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred_rf)
print("\nConfusion Matrix:")
print(tabulate(cm, headers=["Predicted 0", "Predicted 1"], tablefmt="fancy_grid"))
st.subheader("Confusion Matrix")
st.dataframe(cm)

# Classification Report
print("\nClassification Report:")
print(classification_report(y_test, y_pred_rf, digits=2))
st.subheader("Classification Report")
target_names = ["class 0", "class 1"]
st.dataframe(
    classification_report(y_test, y_pred_rf, target_names=target_names, output_dict=True)
)

# Accuracy Score
accuracy = accuracy_score(y_test, y_pred_rf)
print(f"\nAccuracy Score: {accuracy:.2%}")
st.subheader("Accuracy Score")
st.write(f"{accuracy:.2%}")

st.subheader("Tuning Random Forest Algorithm")

from sklearn.model_selection import GridSearchCV

param_grid = {
    'n_estimators': [50,100,200],
    'max_depth' : [None, 10, 20, 30],
    'min_samples_split' : [2, 5, 10],
    'min_samples_leaf' : [1, 2, 4],
    'max_features' :['sqrt','log2']
}

grid_search = GridSearchCV(
    estimator = RandomForestClassifier(random_state=42),
    param_grid = param_grid,
    scoring = 'roc_auc',
    cv=5,
    n_jobs = -1
)

grid_search.fit(X_train, y_train)

print("Best Parameters: ",grid_search.best_params_)
st.subheader("Best Parameters")
st.write(grid_search.best_params_)
best_rf_model = grid_search.best_estimator_

best_rf_model = grid_search.best_params_

tuned_rf_model = RandomForestClassifier(
    n_estimators=best_rf_model['n_estimators'],
    max_depth=best_rf_model['max_depth'],
    min_samples_split=best_rf_model['min_samples_split'],
    min_samples_leaf=best_rf_model['min_samples_leaf'],
    max_features=best_rf_model['max_features'],
    random_state=42
)

# Train the new model
tuned_rf_model.fit(X_train, y_train)

# Make predictions
y_pred_tuned = tuned_rf_model.predict(X_test)

cm = confusion_matrix(y_test, y_pred_tuned)
print("\nConfusion Matrix:")
print(tabulate(cm, headers=["Predicted 0", "Predicted 1"], tablefmt="fancy_grid"))
st.subheader("Confusion Matrix")
st.dataframe(cm)

# Classification Report
print("\nClassification Report:")
print(classification_report(y_test, y_pred_tuned, digits=2))
st.subheader("Classification Report")
target_names = ["class 0", "class 1"]
st.dataframe(
    classification_report(y_test, y_pred_tuned, target_names=target_names, output_dict=True)
)

# Accuracy Score
accuracy = accuracy_score(y_test, y_pred_tuned)
print(f"\nAccuracy Score: {accuracy:.2%}")
st.subheader("Accuracy Score")
st.write(f"{accuracy:.2%}")

st.subheader("Support Vector Machine (SVM)")

from sklearn.svm import SVC

# Train an SVM model
svm_model = SVC(kernel='linear', class_weight='balanced', random_state=42)
svm_model.fit(X_train, y_train)

# Make predictions
y_pred_svm = svm_model.predict(X_test)

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred_svm)
print("\nConfusion Matrix:")
print(tabulate(cm, headers=["Predicted 0", "Predicted 1"], tablefmt="fancy_grid"))
st.subheader("Confusion Matrix")
st.dataframe(cm)

# Classification Report
print("\nClassification Report:")
print(classification_report(y_test, y_pred_svm, digits=2))
st.subheader("Classification Report")
target_names = ["class 1", "class 2"]
st.dataframe(
    classification_report(y_test, y_pred_svm, target_names=target_names, output_dict=True)
)

# Accuracy Score
accuracy = accuracy_score(y_test, y_pred_svm)
print(f"\nAccuracy Score: {accuracy:.2%}")
st.subheader("Accuracy Score")
st.write(f"{accuracy:.2%}")

st.subheader("Fine Tune the Model")
# Define parameter grid for SVM tuning
param_grid = {
    'C': [0.1, 1, 10, 100],  # Regularization parameter
    'kernel': ['linear', 'rbf', 'poly'],  # Kernel types
    'gamma': ['scale', 'auto'],  # Kernel coefficient for 'rbf', 'poly', and 'sigmoid'
    'class_weight': ['balanced', None],  # Class weight options
    'max_iter': [1000, 2000]  # Max number of iterations
}

# Create a GridSearchCV object
grid_search = GridSearchCV(estimator=SVC(random_state=42), param_grid=param_grid,
                           cv=5, scoring='accuracy', n_jobs=-1, verbose=1)

# Fit the model
grid_search.fit(X_train, y_train)

# Get the best parameters from GridSearchCV
print("Best Parameters found: ", grid_search.best_params_)
st.subheader("Best Parameters")
st.write(grid_search.best_params_)

# Get the best model from the grid search
best_svm_model = grid_search.best_estimator_

# Make predictions using the best model
y_pred_best_svm = best_svm_model.predict(X_test)

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred_best_svm)
print("\nConfusion Matrix:")
print(tabulate(cm, headers=["Predicted 0", "Predicted 1"], tablefmt="fancy_grid"))
st.subheader("Confusion Matrix")
st.dataframe(cm)

# Classification Report
print("\nClassification Report:")
print(classification_report(y_test, y_pred_best_svm, digits=2))
st.subheader("Classification Report")
target_names = ["class 0", "class 1"]
st.dataframe(
    classification_report(y_test, y_pred_best_svm, target_names=target_names, output_dict=True)
)

# Accuracy Score
accuracy = accuracy_score(y_test, y_pred_best_svm)
print(f"\nAccuracy Score: {accuracy:.2%}")
st.subheader("Accuracy Score")
st.write(f"{accuracy:.2%}")

st.subheader("Gradient Boosting with XGBoost")
# !pip install xgboost

from xgboost import XGBClassifier

# Map the target variable
y_train = y_train.map({1: 0, 2: 1})
y_test = y_test.map({1: 0, 2: 1})

# Train an XGBoost model
xgb_model = XGBClassifier(scale_pos_weight=(len(y_train) - sum(y_train)) / sum(y_train), random_state=42, eval_metric='logloss')
xgb_model.fit(X_train, y_train)

# Make predictions
y_pred_xgb = xgb_model.predict(X_test)

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred_xgb)
print("\nConfusion Matrix:")
print(tabulate(cm, headers=["Predicted 0", "Predicted 1"], tablefmt="fancy_grid"))
st.subheader("Confusion Matrix")
st.dataframe(cm)

# Classification Report
print("\nClassification Report:")
print(classification_report(y_test, y_pred_xgb, digits=2))
st.subheader("Classification Report")
target_names = ["class 0", "class 1"]
st.dataframe(
    classification_report(y_test, y_pred_xgb, target_names=target_names, output_dict=True)
)

# Accuracy Score
accuracy = accuracy_score(y_test, y_pred_xgb)
print(f"\nAccuracy Score: {accuracy:.2%}")
st.subheader("Accuracy Score")
st.write(f"{accuracy:.2%}")

st.subheader("Gradient Boosting with LightGBM")

from lightgbm import LGBMClassifier

# !pip install lightgbm

# Clean feature names to make them LightGBM-compatible
X_train.columns = X_train.columns.str.replace(r'[^\w]', '_', regex=True)
X_test.columns = X_test.columns.str.replace(r'[^\w]', '_', regex=True)

# Train the LightGBM model
lgbm_model = LGBMClassifier(class_weight='balanced', random_state=42)
lgbm_model.fit(X_train, y_train)

# Make predictions
y_pred_lgbm = lgbm_model.predict(X_test)

# Evaluate the model
cm = confusion_matrix(y_test, y_pred_lgbm)
cm_table = [
    ["", "Predicted 0", "Predicted 1"],
    ["True 0 (TN)", cm[0, 0], cm[0, 1]],
    ["True 1 (FN)", cm[1, 0], cm[1, 1]]
]
print("\nConfusion Matrix with Labels:")
print(tabulate(cm_table, headers="firstrow", tablefmt="grid"))
st.subheader("Confusion Matrix")
st.dataframe(cm)

print("\nClassification Report:")
print(classification_report(y_test, y_pred_lgbm, digits=2))
st.subheader("Classification Report")
target_names = ["class 0", "class 1"]
st.dataframe(
    classification_report(y_test, y_pred_lgbm, target_names=target_names, output_dict=True)
)
accuracy = accuracy_score(y_test, y_pred_lgbm) * 100
print(f"\nAccuracy Score: {accuracy:.2f}%")
st.subheader("Accuracy Score")
st.write(f"{accuracy:.2f}%")


#attempt to run auto ml

# pip install arcgis

# !pip install tpot
#Assuming feat_select_encoded is your dataset
# import time
# X = feat_select_encoded.drop(columns=["Voted in 2020"])
# y = feat_select_encoded["Voted in 2020"]

# # Split the data into training and test sets
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# with st.spinner(text="In progress..."):
#     while True:
#         time.sleep(5)
#         st.text("Still working...")
#     tpot = TPOTClassifier(generations=5, population_size=50, verbosity=2, random_state=42)
#     tpot.fit(X_train, y_train)
#     # Evaluate the model
#     score = tpot.score(X_test, y_test)
# st.success("Done!")

# print(f"TPOT Model Accuracy: {score:.2%}")
# st.subheader("TPOT Model Accuracy")
# st.write(f"{score:.2%}")

# # Export the best model pipeline found
# tpot.export('best_pipeline.py')

# st.subheader("Best Pipeline")
# st.write(tpot.fitted_pipeline_)

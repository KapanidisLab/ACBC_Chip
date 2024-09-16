import pandas as pd
import numpy as np
from sklearn.metrics import ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import builtins  # To access the original built-in functions

# Define the message function and dictionaries
def message(binary_array):
    merfish_msg = ' '.join(map(str, binary_array))
    return merfish_dict.get(merfish_msg, 'Inconclusive')

species_dict = {
    1: 'E.Coli',
    3: 'S.Aureus',
    6: 'K.Pneumoniae',
    7: 'P.Aeruginosa',
    10: 'S.Agalactiae',
    11: 'E.Faecalis',
    12: 'S.Pneumoniae',
    0: 'Inconclusive'
}

# Reverse mapping from species names to indices
species_name_to_index = {v: k for k, v in species_dict.items()}

merfish_dict = {
    '1 0 0 0 1 0': 'E.Coli',
    '1 0 1 0 0 0': 'S.Aureus',
    '0 1 0 1 0 0': 'P.Aeruginosa',
    '1 0 0 0 0 1': 'K.Pneumoniae',
    '0 1 0 0 0 1': 'S.Agalactiae',
    '1 0 0 1 0 0': 'E.Faecalis',
    '0 1 1 0 0 0': 'S.Pneumoniae',
    '0 0 0 0 0 0': 'Inconclusive'
}

# Read the data
data = pd.read_csv('multiplexed_16S_database.csv')
data = data.dropna()

# Extract necessary columns
exp_ids = data['exp_id'].values
true_labels = data['species index'].astype(int).values
probe_columns = ['p1', 'p2', 'p3', 'p4', 'p5', 'p6']
probe_data = data[probe_columns].values

# Normalize and binarize the data
row_min = probe_data.min(axis=1, keepdims=True)
row_max = probe_data.max(axis=1, keepdims=True)
value_range = row_max

normalized_probe_data = probe_data / value_range

binarized_data = np.zeros_like(normalized_probe_data, dtype=int)
num_rows = normalized_probe_data.shape[0]
for i in builtins.range(num_rows):
    row = normalized_probe_data[i]
    top_two_indices = np.argpartition(row, -2)[-2:]
    binarized_data[i, top_two_indices] = 1

# Use the message function to get species assignments
predicted_species = [message(binary_array) for binary_array in binarized_data]
predicted_labels = [species_name_to_index.get(species, -1) for species in predicted_species]

# Get strain numbers from 'exp_id'
strains = [''.join(filter(str.isdigit, exp_id)) for exp_id in exp_ids]

# Create DataFrame with results
results_df = pd.DataFrame({
    'exp_id': exp_ids,
    'True_Label': true_labels,
    'Strain': strains,
    'Predicted_Label': predicted_labels
})

# Calculate per-strain classification rates
def calculate_classification_rate(group):
    correct = (group['True_Label'] == group['Predicted_Label']).sum()
    total = len(group)
    return correct / total

strain_classification_rates = results_df.groupby(['True_Label', 'Strain']).apply(
    calculate_classification_rate
).reset_index(name='Classification_Rate')

# Average classification rates per species
species_classification_rates = strain_classification_rates.groupby('True_Label')['Classification_Rate'].mean().reset_index()
species_classification_rates['Species_Name'] = species_classification_rates['True_Label'].map(species_dict)

print("\nAverage Classification Rates for Each Species:")
print(species_classification_rates[['Species_Name', 'Classification_Rate']])

# Create confusion matrix in the specified order
desired_species_order = [
    'E.Coli', 'K.Pneumoniae', 'P.Aeruginosa', 'E.Faecalis',
    'S.Pneumoniae', 'S.Agalactiae', 'S.Aureus', 'Inconclusive'
]

# Map species names to indices
species_indices_ordered = [species_name_to_index.get(name, -1) for name in desired_species_order]
species_indices_ordered = [idx for idx in species_indices_ordered if idx != -1]
species_index_to_position = {label: idx for idx, label in enumerate(species_indices_ordered)}
num_species = len(species_indices_ordered)

# Initialize the confusion matrix
confusion_mat = np.zeros((num_species, num_species))

# Collect confusion matrix rows per strain of species
species_confusion_rows = {label: [] for label in species_indices_ordered}

for (true_label, strain), group in results_df.groupby(['True_Label', 'Strain']):
    if true_label in species_index_to_position:
        total = len(group)
        if total > 0:
            predicted_counts = group['Predicted_Label'].value_counts()
            # Initialize the confusion matrix row for this strain
            confusion_row = np.zeros(num_species)
            for pred_label, count in predicted_counts.items():
                if pred_label in species_index_to_position:
                    j = species_index_to_position[pred_label]
                    confusion_row[j] = count / total  # Normalize by total
            # Append this confusion row to the list for this species
            species_confusion_rows[true_label].append(confusion_row)

# Average confusion matrix rows per species
for true_label in species_indices_ordered:
    if species_confusion_rows[true_label]:
        rows = species_confusion_rows[true_label]
        avg_row = np.mean(rows, axis=0)
        i = species_index_to_position[true_label]
        confusion_mat[i, :] = avg_row

# Prepare labels for display
display_labels = desired_species_order[:num_species]

# Plot the confusion matrix
plt.figure(figsize=(12, 10))
disp = ConfusionMatrixDisplay(confusion_matrix=confusion_mat, display_labels=display_labels)
disp.plot(cmap=plt.cm.Greens, values_format='.2f', ax=plt.gca())
plt.title('Averaged Classification Rates Confusion Matrix')
plt.show()

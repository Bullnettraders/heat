import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def generate_top10_heatmap():
    changes_dict = get_price_changes()
    if not changes_dict:
        return None

    # Wir nehmen nur die Ticker, die wir auch erfolgreich abgerufen haben
    # Und füllen ggf. auf 10 auf, falls ein Ticker fehlt
    labels_list = list(changes_dict.keys())
    values_list = list(changes_dict.values())

    # Sicherstellen, dass wir genau 10 Elemente für eine 2x5 Matrix haben
    while len(values_list) < 10:
        values_list.append(0.0)
        labels_list.append("N/A")

    # Umwandeln in 2x5 Raster
    data_matrix = np.array(values_list).reshape(2, 5)
    
    # Text für die Kacheln (Ticker + Wert)
    annot_matrix = np.array([f"{t}\n{v}%" for t, v in zip(labels_list, values_list)]).reshape(2, 5)

    # Styling
    plt.figure(figsize=(12, 5))
    sns.heatmap(data_matrix, 
                annot=annot_matrix, 
                fmt="", 
                cmap="RdYlGn", 
                center=0, 
                linewidths=2,
                cbar_kws={'label': 'Änderung in %'})
    
    plt.title("Top 10 Tech Heatmap", fontsize=16)
    plt.axis('off')
    
    file_path = "top10_heatmap.png"
    plt.savefig(file_path, bbox_inches='tight', facecolor='#2c2f33') # Discord-Grau als Hintergrund
    plt.close()
    return file_path

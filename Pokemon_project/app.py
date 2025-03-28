import matplotlib
matplotlib.use('Agg')
from io import BytesIO
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import numpy as np
from flask import Flask, render_template, send_file, request

app = Flask(__name__)

def load_pokemon_data():
    file_path = "data/pokemon.csv"
    pokemon_data = pd.read_csv(file_path)
    print("Column Names:", pokemon_data.columns) 
    return pokemon_data

def encode_plot_to_base64(fig):
    img_io = BytesIO()
    fig.savefig(img_io, format='png')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
    img_io.close()
    return img_base64

def create_radar_chart(pokemon1, pokemon2):
    categories = ['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']
    
    stats1 = [pokemon1['HP'], pokemon1['Attack'], pokemon1['Defense'], pokemon1['Sp. Atk'], pokemon1['Sp. Def'], pokemon1['Speed']]
    stats2 = [pokemon2['HP'], pokemon2['Attack'], pokemon2['Defense'], pokemon2['Sp. Atk'], pokemon2['Sp. Def'], pokemon2['Speed']]

    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    stats1 += stats1[:1]
    stats2 += stats2[:1] 
    angles += angles[:1] 

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angles, stats1, color='blue', alpha=0.25)
    ax.fill(angles, stats2, color='red', alpha=0.25)
    ax.plot(angles, stats1, color='blue', linewidth=2, linestyle='solid')
    ax.plot(angles, stats2, color='red', linewidth=2, linestyle='solid')

    for i in range(len(categories)):
        ax.text(angles[i], stats1[i] + 5, f"{stats1[i]}", horizontalalignment='center', size=10, color='blue', weight='semibold')
        ax.text(angles[i], stats2[i] + 5, f"{stats2[i]}", horizontalalignment='center', size=10, color='red', weight='semibold')

    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)

    return encode_plot_to_base64(fig)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pokemon')
def pokemon_list():
    pokemon_data = load_pokemon_data()

    unique_types = sorted(set(pokemon_data['Type 1']).union(set(pokemon_data['Type 2'].dropna())))

    return render_template(
        'pokemon.html',
        pokemons=pokemon_data.to_dict(orient='records'),
        unique_types=unique_types
    )

@app.route('/stats')
def stats():
    pokemon_data = load_pokemon_data()

    avg_stats_by_type = pokemon_data.groupby('Type 1').mean(numeric_only=True)
    plt.figure(figsize=(8, 6))
    sns.barplot(x=avg_stats_by_type.index, y=avg_stats_by_type['HP'])
    plt.title('Average HP by Type')
    plot1 = encode_plot_to_base64(plt)
    plt.close()

    type_counts = pokemon_data['Type 1'].value_counts()
    plt.figure(figsize=(8, 6))
    sns.barplot(x=type_counts.index, y=type_counts.values)
    plt.title('Pokémon Type Distribution')
    plot2 = encode_plot_to_base64(plt)
    plt.close()

    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=pokemon_data, x='Attack', y='Defense', hue='Type 1')
    plt.title('Attack vs Defense by Type')
    plot3 = encode_plot_to_base64(plt)
    plt.close()

    pokemon_data['Total'] = pokemon_data[['HP', 'Attack', 'Defense', 'Speed']].sum(axis=1)
    plt.figure(figsize=(8, 6))
    sns.histplot(pokemon_data['Total'], kde=True)
    plt.title('Total Stats Distribution')
    plot4 = encode_plot_to_base64(plt)
    plt.close()

    return render_template('stats.html', plot1=plot1, plot2=plot2, plot3=plot3, plot4=plot4)

@app.route('/compare', methods=['GET', 'POST'])
def compare():
    pokemon_data = load_pokemon_data()
    
    pokemon1 = None
    pokemon2 = None
    comparison_plot = None

    if request.method == 'POST':
        pokemon1_id = request.form.get('pokemon1')
        pokemon2_id = request.form.get('pokemon2')

        if pokemon1_id and pokemon2_id:
            pokemon1 = pokemon_data[pokemon_data['#'] == int(pokemon1_id)].iloc[0]
            pokemon2 = pokemon_data[pokemon_data['#'] == int(pokemon2_id)].iloc[0]

            comparison_plot = create_radar_chart(pokemon1, pokemon2)

    return render_template('comparison.html', pokemon_list=pokemon_data.to_dict(orient='records'),
                           pokemon1=pokemon1, pokemon2=pokemon2, comparison_plot=comparison_plot)

@app.route('/download')
def download_file():
    file_path = os.path.join("data", "pokemon.csv")
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

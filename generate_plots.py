import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt

def plot_regression(x, y, regression, title, filename):
    """Plots the data points and the regression line."""
    plt.figure()
    plt.scatter(x, y, label='Data')

    x_fit = np.linspace(x.min(), x.max(), 100)
    y_fit = 0

    if regression['type'] == 'linear':
        y_fit = regression['params'][0] * x_fit + regression['params'][1]
    elif regression['type'] == 'quadratic':
        # params: [coef_x_squared, coef_x, intercept]
        y_fit = regression['params'][0] * (x_fit ** 2) + regression['params'][1] * x_fit + regression['params'][2]
    elif regression['type'] == 'log':
        y_fit = regression['params'][0] * np.log(x_fit) + regression['params'][1]

    plt.plot(x_fit, y_fit, color='red', label=f"{regression['type'].capitalize()} Fit")
    plt.title(title)
    plt.xlabel('Lichess Rating')
    plt.ylabel('Chess.com Rating')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'images/{filename}')
    plt.close()

# Load the datasets
lichess_data = pd.read_csv('lichess_to_chess_com_data.csv')
chess_com_data = pd.read_csv('chess_com_to_chess_com_data.csv')

with open('regressions.json', 'r') as f:
    regressions = json.load(f)

# --- Generate Plots ---

# Blitz
df_blitz = lichess_data[['lichess_blitz', 'chess_com_blitz']].dropna()
plot_regression(df_blitz['lichess_blitz'], df_blitz['chess_com_blitz'], regressions['BLITZ'], 'Lichess Blitz vs. Chess.com Blitz', 'blitz_regression.png')

# Bullet
l_b_vs_c_b = lichess_data[['lichess_bullet', 'chess_com_blitz']].dropna()
c_b_vs_c_b = chess_com_data[['chess_com_blitz', 'chess_com_bullet']].dropna()
interp_bullet_ratings = np.interp(l_b_vs_c_b['chess_com_blitz'], c_b_vs_c_b['chess_com_blitz'], c_b_vs_c_b['chess_com_bullet'])
plot_regression(l_b_vs_c_b['lichess_bullet'], interp_bullet_ratings, regressions['BULLET'], 'Lichess Bullet vs. Chess.com Bullet', 'bullet_regression.png')

# Rapid
l_r_vs_c_b = lichess_data[['lichess_rapid', 'chess_com_blitz']].dropna()
c_b_vs_c_r = chess_com_data[['chess_com_blitz', 'chess_com_rapid']].dropna()
interp_rapid_ratings = np.interp(l_r_vs_c_b['chess_com_blitz'], c_b_vs_c_r['chess_com_blitz'], c_b_vs_c_r['chess_com_rapid'])
plot_regression(l_r_vs_c_b['lichess_rapid'], interp_rapid_ratings, regressions['RAPID'], 'Lichess Rapid vs. Chess.com Rapid', 'rapid_regression.png')

# Classical
df_classical = lichess_data[['lichess_classical', 'chess_com_blitz']].dropna()
plot_regression(df_classical['lichess_classical'], df_classical['chess_com_blitz'], regressions['CLASSICAL'], 'Lichess Classical vs. Chess.com Blitz', 'classical_regression.png')

print("Successfully generated and saved regression plots.")

# --- Update README.md with new image paths ---
readme_path = 'README.md'
with open(readme_path, 'r') as f:
    readme_content = f.read()

# Define a mapping of old image URLs to new local paths
image_updates = {
    '![bullet_regression](https://user-images.githubusercontent.com/89805167/173907866-57c8af0d-5985-44ea-ae53-2a1ae08a8d57.png)': '![bullet_regression](images/bullet_regression.png)',
    '![blitz_regression](https://user-images.githubusercontent.com/89805167/173907893-be119ab6-45c0-4f42-bf8c-61a5b28e187b.png)': '![blitz_regression](images/blitz_regression.png)',
    '![rapid_regression](https://user-images.githubusercontent.com/89805167/173907914-f2d1f4c7-e64e-4ef1-a27e-cec18a6167ec.png)': '![rapid_regression](images/rapid_regression.png)',
    '![classical_regression](https://user-images.githubusercontent.com/89805167/173907947-b99af892-cb76-4d15-b6a5-7723f57d0558.png)': '![classical_regression](images/classical_regression.png)'
}

for old_url, new_path in image_updates.items():
    readme_content = readme_content.replace(old_url, new_path)

with open(readme_path, 'w') as f:
    f.write(readme_content)

print("README.md updated with new image paths.")
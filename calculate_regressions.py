import pandas as pd
import numpy as np
import json
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error

def calculate_aic(n, mse, k):
    """Calculates the Akaike Information Criterion."""
    if mse == 0:
        return -np.inf
    return n * np.log(mse) + 2 * k

def find_best_regression(x, y):
    """Finds the best regression model (linear, quadratic, or log) based on AIC."""
    models = {}
    x_reshaped = x.values.reshape(-1, 1)

    # Linear
    linear_model = LinearRegression()
    linear_model.fit(x_reshaped, y)
    linear_mse = mean_squared_error(y, linear_model.predict(x_reshaped))
    models['linear'] = {
        'model': linear_model,
        'aic': calculate_aic(len(x), linear_mse, 2),
        'params': linear_model.coef_.tolist() + [linear_model.intercept_]
    }

    # Quadratic
    poly = PolynomialFeatures(degree=2)
    x_poly = poly.fit_transform(x_reshaped)
    quad_model = LinearRegression()
    quad_model.fit(x_poly, y)
    quad_mse = mean_squared_error(y, quad_model.predict(x_poly))
    
    # Corrected order for quadratic parameters: [coef_x_squared, coef_x, intercept]
    # Based on observed quad_model.coef_ shape (3,) where coef_[0] is for constant, coef_[1] for x, coef_[2] for x^2
    models['quadratic'] = {
        'model': quad_model,
        'aic': calculate_aic(len(x), quad_mse, 3),
        'params': [quad_model.coef_[2], quad_model.coef_[1], quad_model.intercept_]
    }

    # Logarithmic
    x_log = np.log(x_reshaped)
    log_model = LinearRegression()
    log_model.fit(x_log, y)
    log_mse = mean_squared_error(y, log_model.predict(x_log))
    models['log'] = {
        'model': log_model,
        'aic': calculate_aic(len(x), log_mse, 2),
        'params': log_model.coef_.tolist() + [log_model.intercept_]
    }

    # Find best model
    best_model_name = min(models, key=lambda k: models[k]['aic'])
    return {
        'type': best_model_name,
        'params': models[best_model_name]['params']
    }

# Load the datasets
lichess_data = pd.read_csv('lichess_to_chess_com_data.csv')
chess_com_data = pd.read_csv('chess_com_to_chess_com_data.csv')

# --- Regressions ---
regressions = {}

# Blitz
df_blitz = lichess_data[['lichess_blitz', 'chess_com_blitz']].dropna()
regressions['BLITZ'] = find_best_regression(df_blitz['lichess_blitz'], df_blitz['chess_com_blitz'])

# Bullet
l_b_vs_c_b = lichess_data[['lichess_bullet', 'chess_com_blitz']].dropna()
c_b_vs_c_b = chess_com_data[['chess_com_blitz', 'chess_com_bullet']].dropna()
interp_bullet_ratings = np.interp(l_b_vs_c_b['chess_com_blitz'], c_b_vs_c_b['chess_com_blitz'], c_b_vs_c_b['chess_com_bullet'])
regressions['BULLET'] = find_best_regression(l_b_vs_c_b['lichess_bullet'], interp_bullet_ratings)

# Rapid
l_r_vs_c_b = lichess_data[['lichess_rapid', 'chess_com_blitz']].dropna()
c_b_vs_c_r = chess_com_data[['chess_com_blitz', 'chess_com_rapid']].dropna()
interp_rapid_ratings = np.interp(l_r_vs_c_b['chess_com_blitz'], c_b_vs_c_r['chess_com_blitz'], c_b_vs_c_r['chess_com_rapid'])
regressions['RAPID'] = find_best_regression(l_r_vs_c_b['lichess_rapid'], interp_rapid_ratings)

# Classical
df_classical = lichess_data[['lichess_classical', 'chess_com_blitz']].dropna()
regressions['CLASSICAL'] = find_best_regression(df_classical['lichess_classical'], df_classical['chess_com_blitz'])


with open('regressions.json', 'w') as f:
    json.dump(regressions, f, indent=2)

print("Successfully created regressions.json with the best-fit models.")
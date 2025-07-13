import unittest
import pandas as pd
import numpy as np
import json
import os
import sys

# Add the parent directory to the path to import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calculate_regressions import find_best_regression, calculate_aic


class TestRegressions(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Load test data once for all tests."""
        cls.test_dir = os.path.dirname(os.path.abspath(__file__))
        cls.lichess_data = pd.read_csv(os.path.join(cls.test_dir, 'example_lichess_to_chess_com_data.csv'))
        cls.chess_com_data = pd.read_csv(os.path.join(cls.test_dir, 'example_chess_com_to_chess_com_data.csv'))
        
    def calculate_regression_value(self, regression, lichess_rating):
        """Calculate regression value using the same logic as JavaScript extension."""
        params = regression['params']
        
        if regression['type'] == 'linear':
            # For linear: p1 * x + p2 (JavaScript: p1 * lichessRating + p2)
            p1, p2 = params
            result = round(p1 * lichess_rating + p2)
        elif regression['type'] == 'quadratic':
            # For quadratic: p1 * x^2 + p2 * x + p3 (JavaScript: p1 * (lichessRating ** 2) + p2 * lichessRating + p3)
            p1, p2, p3 = params
            result = round(p1 * (lichess_rating ** 2) + p2 * lichess_rating + p3)
        elif regression['type'] == 'log':
            # For log: p1 * log(x) + p2 (JavaScript: p1 * Math.log(lichessRating) + p2)
            p1, p2 = params
            result = round(p1 * np.log(lichess_rating) + p2)
        else:
            return None
        
        # Return 0 if the result is negative (can't have negative ratings)
        return max(0, result)

    def test_blitz_regression(self):
        """Test Blitz to Blitz regression."""
        df_blitz = self.lichess_data[['lichess_blitz', 'chess_com_blitz']].dropna()
        regression = find_best_regression(df_blitz['lichess_blitz'], df_blitz['chess_com_blitz'])
        
        # Test that regression is created
        self.assertIsNotNone(regression)
        self.assertIn('type', regression)
        self.assertIn('params', regression)
        self.assertIn(regression['type'], ['linear', 'quadratic', 'log'])
        
        # Test specific Lichess ratings and verify they produce reasonable Chess.com ratings
        test_cases = [
            (1030, 500),   # First row in test data
            (1420, 1000),  # Middle range
            (2100, 2000),  # Higher range
        ]
        
        for lichess_rating, expected_chess_com in test_cases:
            calculated = self.calculate_regression_value(regression, lichess_rating)
            self.assertIsNotNone(calculated)
            # Allow for some variance due to regression fitting
            self.assertGreater(calculated, 0, f"Calculated rating should be positive for Lichess {lichess_rating}")
            # Verify it's in a reasonable range (not too far from expected)
            self.assertLess(abs(calculated - expected_chess_com), 200, 
                          f"Blitz regression for {lichess_rating} produced {calculated}, expected around {expected_chess_com}")

    def test_bullet_regression(self):
        """Test Bullet regression (Lichess Bullet -> Chess.com Bullet via Blitz interpolation)."""
        l_b_vs_c_b = self.lichess_data[['lichess_bullet', 'chess_com_blitz']].dropna()
        c_b_vs_c_b = self.chess_com_data[['chess_com_blitz', 'chess_com_bullet']].dropna()
        interp_bullet_ratings = np.interp(l_b_vs_c_b['chess_com_blitz'], 
                                        c_b_vs_c_b['chess_com_blitz'], 
                                        c_b_vs_c_b['chess_com_bullet'])
        regression = find_best_regression(l_b_vs_c_b['lichess_bullet'], interp_bullet_ratings)
        
        self.assertIsNotNone(regression)
        self.assertIn('type', regression)
        self.assertIn('params', regression)
        
        # Test with sample Lichess bullet ratings
        test_cases = [
            (975, 445),    # Approximately from test data
            (1295, 920),   # Middle range
            (2195, 1930),  # Higher range
        ]
        
        for lichess_rating, expected_approx in test_cases:
            calculated = self.calculate_regression_value(regression, lichess_rating)
            self.assertIsNotNone(calculated)
            self.assertGreater(calculated, 0)
            # Bullet ratings tend to be lower than blitz
            self.assertLess(abs(calculated - expected_approx), 300,
                          f"Bullet regression for {lichess_rating} produced {calculated}, expected around {expected_approx}")

    def test_rapid_regression(self):
        """Test Rapid regression (Lichess Rapid -> Chess.com Rapid via Blitz interpolation)."""
        l_r_vs_c_b = self.lichess_data[['lichess_rapid', 'chess_com_blitz']].dropna()
        c_b_vs_c_r = self.chess_com_data[['chess_com_blitz', 'chess_com_rapid']].dropna()
        interp_rapid_ratings = np.interp(l_r_vs_c_b['chess_com_blitz'], 
                                       c_b_vs_c_r['chess_com_blitz'], 
                                       c_b_vs_c_r['chess_com_rapid'])
        regression = find_best_regression(l_r_vs_c_b['lichess_rapid'], interp_rapid_ratings)
        
        self.assertIsNotNone(regression)
        self.assertIn('type', regression)
        self.assertIn('params', regression)
        
        # Test with sample Lichess rapid ratings
        test_cases = [
            (1205, 735),   # From test data
            (1615, 1230),  # Middle range
            (2185, 2035),  # Higher range
        ]
        
        for lichess_rating, expected_approx in test_cases:
            calculated = self.calculate_regression_value(regression, lichess_rating)
            self.assertIsNotNone(calculated)
            self.assertGreater(calculated, 0)
            # Rapid ratings tend to be higher than blitz
            self.assertLess(abs(calculated - expected_approx), 300,
                          f"Rapid regression for {lichess_rating} produced {calculated}, expected around {expected_approx}")

    def test_classical_regression(self):
        """Test Classical regression (Lichess Classical -> Chess.com Blitz)."""
        df_classical = self.lichess_data[['lichess_classical', 'chess_com_blitz']].dropna()
        regression = find_best_regression(df_classical['lichess_classical'], df_classical['chess_com_blitz'])
        
        self.assertIsNotNone(regression)
        self.assertIn('type', regression)
        self.assertIn('params', regression)
        
        # Test with sample Lichess classical ratings
        test_cases = [
            (1405, 500),   # From test data
            (1715, 1000),  # Middle range
            (2100, 2000),  # Higher range
        ]
        
        for lichess_rating, expected_approx in test_cases:
            calculated = self.calculate_regression_value(regression, lichess_rating)
            self.assertIsNotNone(calculated)
            self.assertGreater(calculated, 0)
            # Classical tends to be higher, so conversion might have wider variance
            self.assertLess(abs(calculated - expected_approx), 400,
                          f"Classical regression for {lichess_rating} produced {calculated}, expected around {expected_approx}")

    def test_aic_calculation(self):
        """Test AIC calculation function."""
        # Test normal case
        aic = calculate_aic(100, 1.5, 3)
        self.assertIsInstance(aic, float)
        
        # Test zero MSE case
        aic_zero = calculate_aic(100, 0, 3)
        self.assertEqual(aic_zero, -np.inf)
        
        # Test that lower MSE gives better (lower) AIC
        aic1 = calculate_aic(100, 1.0, 3)
        aic2 = calculate_aic(100, 2.0, 3)
        self.assertLess(aic1, aic2)

    def test_regression_consistency(self):
        """Test that regressions are consistent and monotonic."""
        df_blitz = self.lichess_data[['lichess_blitz', 'chess_com_blitz']].dropna()
        regression = find_best_regression(df_blitz['lichess_blitz'], df_blitz['chess_com_blitz'])
        
        # Test monotonicity for a range of ratings
        ratings = [1000, 1200, 1400, 1600, 1800, 2000, 2200]
        calculated_ratings = [self.calculate_regression_value(regression, r) for r in ratings]
        
        # For most reasonable regressions, higher Lichess rating should give higher Chess.com rating
        for i in range(len(calculated_ratings) - 1):
            if calculated_ratings[i] is not None and calculated_ratings[i+1] is not None:
                # Allow for some small decreases due to regression fitting, but not major ones
                difference = calculated_ratings[i+1] - calculated_ratings[i]
                self.assertGreater(difference, -50, 
                                 f"Large decrease in ratings: {ratings[i]} -> {calculated_ratings[i]}, "
                                 f"{ratings[i+1]} -> {calculated_ratings[i+1]}")

    def test_parameter_format(self):
        """Test that regression parameters are in the correct format."""
        df_blitz = self.lichess_data[['lichess_blitz', 'chess_com_blitz']].dropna()
        regression = find_best_regression(df_blitz['lichess_blitz'], df_blitz['chess_com_blitz'])
        
        # Check parameter count based on regression type
        if regression['type'] == 'linear':
            self.assertEqual(len(regression['params']), 2, "Linear regression should have 2 parameters")
        elif regression['type'] == 'quadratic':
            self.assertEqual(len(regression['params']), 3, "Quadratic regression should have 3 parameters")
        elif regression['type'] == 'log':
            self.assertEqual(len(regression['params']), 2, "Log regression should have 2 parameters")
        
        # All parameters should be numeric
        for param in regression['params']:
            self.assertIsInstance(param, (int, float, np.number))

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        df_blitz = self.lichess_data[['lichess_blitz', 'chess_com_blitz']].dropna()
        regression = find_best_regression(df_blitz['lichess_blitz'], df_blitz['chess_com_blitz'])
        
        # Test very low rating
        low_rating = self.calculate_regression_value(regression, 800)
        self.assertIsNotNone(low_rating)
        self.assertGreater(low_rating, 0)
        
        # Test very high rating
        high_rating = self.calculate_regression_value(regression, 3000)
        self.assertIsNotNone(high_rating)
        self.assertGreater(high_rating, 0)
        
        # Test that high rating gives higher result than low rating (general trend)
        self.assertGreater(high_rating, low_rating)

    def test_full_integration(self):
        """Test full integration by recreating the regressions.json logic."""
        # This test recreates the full calculation process
        regressions = {}
        
        # Blitz
        df_blitz = self.lichess_data[['lichess_blitz', 'chess_com_blitz']].dropna()
        regressions['BLITZ'] = find_best_regression(df_blitz['lichess_blitz'], df_blitz['chess_com_blitz'])
        
        # Bullet
        l_b_vs_c_b = self.lichess_data[['lichess_bullet', 'chess_com_blitz']].dropna()
        c_b_vs_c_b = self.chess_com_data[['chess_com_blitz', 'chess_com_bullet']].dropna()
        interp_bullet_ratings = np.interp(l_b_vs_c_b['chess_com_blitz'], 
                                        c_b_vs_c_b['chess_com_blitz'], 
                                        c_b_vs_c_b['chess_com_bullet'])
        regressions['BULLET'] = find_best_regression(l_b_vs_c_b['lichess_bullet'], interp_bullet_ratings)
        
        # Rapid
        l_r_vs_c_b = self.lichess_data[['lichess_rapid', 'chess_com_blitz']].dropna()
        c_b_vs_c_r = self.chess_com_data[['chess_com_blitz', 'chess_com_rapid']].dropna()
        interp_rapid_ratings = np.interp(l_r_vs_c_b['chess_com_blitz'], 
                                       c_b_vs_c_r['chess_com_blitz'], 
                                       c_b_vs_c_r['chess_com_rapid'])
        regressions['RAPID'] = find_best_regression(l_r_vs_c_b['lichess_rapid'], interp_rapid_ratings)
        
        # Classical
        df_classical = self.lichess_data[['lichess_classical', 'chess_com_blitz']].dropna()
        regressions['CLASSICAL'] = find_best_regression(df_classical['lichess_classical'], df_classical['chess_com_blitz'])
        
        # Verify all regressions were created
        for game_type in ['BLITZ', 'BULLET', 'RAPID', 'CLASSICAL']:
            self.assertIn(game_type, regressions)
            self.assertIn('type', regressions[game_type])
            self.assertIn('params', regressions[game_type])
            
        # Test a few calculations with each regression type
        test_rating = 1500
        for game_type, regression in regressions.items():
            calculated = self.calculate_regression_value(regression, test_rating)
            self.assertIsNotNone(calculated, f"Failed to calculate {game_type} regression for rating {test_rating}")
            self.assertGreater(calculated, 0, f"{game_type} regression produced non-positive result")
            self.assertLess(calculated, 5000, f"{game_type} regression produced unreasonably high result")


    def test_linear_regression_directly(self):
        """Test linear regression with known data that should produce a linear fit."""
        # Create synthetic linear data: y = 2x + 100
        x_data = pd.Series([1000, 1200, 1400, 1600, 1800, 2000])
        y_data = pd.Series([2100, 2500, 2900, 3300, 3700, 4100])  # y = 2x + 100
        
        regression = find_best_regression(x_data, y_data)
        
        # Should choose linear as the best fit
        self.assertEqual(regression['type'], 'linear')
        self.assertEqual(len(regression['params']), 2)
        
        # Test calculation
        calculated = self.calculate_regression_value(regression, 1500)
        expected = 2 * 1500 + 100  # 3100
        self.assertAlmostEqual(calculated, expected, delta=5)

    def test_quadratic_regression_directly(self):
        """Test quadratic regression with known quadratic data."""
        # Create synthetic quadratic data: y = 0.001x² + x + 100
        x_data = pd.Series([1000, 1200, 1400, 1600, 1800, 2000])
        y_data = pd.Series([
            0.001 * (1000**2) + 1000 + 100,  # 2100
            0.001 * (1200**2) + 1200 + 100,  # 2740
            0.001 * (1400**2) + 1400 + 100,  # 3460
            0.001 * (1600**2) + 1600 + 100,  # 4260
            0.001 * (1800**2) + 1800 + 100,  # 5140
            0.001 * (2000**2) + 2000 + 100,  # 6100
        ])
        
        regression = find_best_regression(x_data, y_data)
        
        # Should choose quadratic as the best fit
        self.assertEqual(regression['type'], 'quadratic')
        self.assertEqual(len(regression['params']), 3)
        
        # Test calculation
        calculated = self.calculate_regression_value(regression, 1500)
        expected = 0.001 * (1500**2) + 1500 + 100  # 3850
        self.assertAlmostEqual(calculated, expected, delta=10)

    def test_logarithmic_regression_directly(self):
        """Test logarithmic regression with known logarithmic data."""
        # Create synthetic logarithmic data: y = 500 * ln(x) - 2000
        x_data = pd.Series([1000, 1200, 1400, 1600, 1800, 2000, 2200, 2400])
        y_data = pd.Series([
            500 * np.log(x) - 2000 for x in x_data
        ])
        
        regression = find_best_regression(x_data, y_data)
        
        # Should choose logarithmic as the best fit
        self.assertEqual(regression['type'], 'log')
        self.assertEqual(len(regression['params']), 2)
        
        # Test calculation
        calculated = self.calculate_regression_value(regression, 1500)
        expected = 500 * np.log(1500) - 2000
        self.assertAlmostEqual(calculated, expected, delta=10)

    def test_regression_type_selection(self):
        """Test that AIC correctly selects the best regression type."""
        # Test with actual data from the blitz regression
        df_blitz = self.lichess_data[['lichess_blitz', 'chess_com_blitz']].dropna()
        
        # Calculate AIC for each model type manually
        x = df_blitz['lichess_blitz']
        y = df_blitz['chess_com_blitz']
        
        from sklearn.linear_model import LinearRegression
        from sklearn.preprocessing import PolynomialFeatures
        from sklearn.metrics import mean_squared_error
        
        x_reshaped = x.values.reshape(-1, 1)
        
        # Linear
        linear_model = LinearRegression()
        linear_model.fit(x_reshaped, y)
        linear_mse = mean_squared_error(y, linear_model.predict(x_reshaped))
        linear_aic = calculate_aic(len(x), linear_mse, 2)
        
        # Quadratic
        poly = PolynomialFeatures(degree=2)
        x_poly = poly.fit_transform(x_reshaped)
        quad_model = LinearRegression()
        quad_model.fit(x_poly, y)
        quad_mse = mean_squared_error(y, quad_model.predict(x_poly))
        quad_aic = calculate_aic(len(x), quad_mse, 3)
        
        # Logarithmic
        x_log = np.log(x_reshaped)
        log_model = LinearRegression()
        log_model.fit(x_log, y)
        log_mse = mean_squared_error(y, log_model.predict(x_log))
        log_aic = calculate_aic(len(x), log_mse, 2)
        
        # Find the best regression
        regression = find_best_regression(x, y)
        
        aic_values = {'linear': linear_aic, 'quadratic': quad_aic, 'log': log_aic}
        best_type = min(aic_values, key=aic_values.get)
        
        self.assertEqual(regression['type'], best_type, 
                        f"Expected {best_type} based on AIC values: {aic_values}, but got {regression['type']}")

    def test_bullet_regression_explanation(self):
        """Test and document the bullet regression process to explain the logic."""
        # Step 1: Get Lichess Bullet → Chess.com Blitz relationship
        l_b_vs_c_b = self.lichess_data[['lichess_bullet', 'chess_com_blitz']].dropna()
        
        # Step 2: Get Chess.com Blitz → Chess.com Bullet relationship  
        c_b_vs_c_b = self.chess_com_data[['chess_com_blitz', 'chess_com_bullet']].dropna()
        
        # Step 3: For each Lichess bullet rating, find corresponding Chess.com blitz,
        # then interpolate to find the corresponding Chess.com bullet rating
        interp_bullet_ratings = np.interp(l_b_vs_c_b['chess_com_blitz'], 
                                        c_b_vs_c_b['chess_com_blitz'], 
                                        c_b_vs_c_b['chess_com_bullet'])
        
        # Step 4: Create regression from Lichess Bullet → Chess.com Bullet (interpolated)
        regression = find_best_regression(l_b_vs_c_b['lichess_bullet'], interp_bullet_ratings)
        
        # Verify the process works
        self.assertIsNotNone(regression)
        
        # Test with a known example
        # If someone has 1295 Lichess bullet, what's their estimated Chess.com bullet?
        test_lichess_bullet = 1295
        calculated_bullet = self.calculate_regression_value(regression, test_lichess_bullet)
        
        # Verify it's reasonable (should be lower than blitz typically)
        self.assertIsNotNone(calculated_bullet)
        self.assertGreater(calculated_bullet, 0)
        self.assertLess(calculated_bullet, 3000)  # Sanity check
        
        print(f"Lichess Bullet {test_lichess_bullet} → Chess.com Bullet {calculated_bullet}")

    def test_logarithmic_edge_cases(self):
        """Test logarithmic regression with edge cases that might cause issues."""
        # Test with very small values (log domain issues)
        x_small = pd.Series([1, 2, 3, 4, 5])  # Very small values
        y_small = pd.Series([100, 200, 300, 400, 500])
        
        # This should work but might not choose log due to small x values
        regression_small = find_best_regression(x_small, y_small)
        self.assertIsNotNone(regression_small)
        
        # Test calculation doesn't fail
        if regression_small['type'] == 'log':
            calculated = self.calculate_regression_value(regression_small, 3)
            self.assertIsNotNone(calculated)
        
        # Test with normal range values more suitable for log
        x_normal = pd.Series([100, 200, 500, 1000, 2000])
        y_log_pattern = pd.Series([np.log(x) * 100 + 500 for x in x_normal])
        
        regression_normal = find_best_regression(x_normal, y_log_pattern)
        self.assertIsNotNone(regression_normal)
        
        # Test calculation
        calculated = self.calculate_regression_value(regression_normal, 500)
        self.assertIsNotNone(calculated)
        self.assertGreater(calculated, 0)

    def test_all_regression_types_work(self):
        """Comprehensive test that all regression types can be calculated correctly."""
        # Test each game type's regression
        game_types = ['BLITZ', 'BULLET', 'RAPID', 'CLASSICAL']
        
        for game_type in game_types:
            with self.subTest(game_type=game_type):
                if game_type == 'BLITZ':
                    df = self.lichess_data[['lichess_blitz', 'chess_com_blitz']].dropna()
                    regression = find_best_regression(df['lichess_blitz'], df['chess_com_blitz'])
                
                elif game_type == 'BULLET':
                    l_b_vs_c_b = self.lichess_data[['lichess_bullet', 'chess_com_blitz']].dropna()
                    c_b_vs_c_b = self.chess_com_data[['chess_com_blitz', 'chess_com_bullet']].dropna()
                    interp_bullet_ratings = np.interp(l_b_vs_c_b['chess_com_blitz'], 
                                                    c_b_vs_c_b['chess_com_blitz'], 
                                                    c_b_vs_c_b['chess_com_bullet'])
                    regression = find_best_regression(l_b_vs_c_b['lichess_bullet'], interp_bullet_ratings)
                
                elif game_type == 'RAPID':
                    l_r_vs_c_b = self.lichess_data[['lichess_rapid', 'chess_com_blitz']].dropna()
                    c_b_vs_c_r = self.chess_com_data[['chess_com_blitz', 'chess_com_rapid']].dropna()
                    interp_rapid_ratings = np.interp(l_r_vs_c_b['chess_com_blitz'], 
                                                   c_b_vs_c_r['chess_com_blitz'], 
                                                   c_b_vs_c_r['chess_com_rapid'])
                    regression = find_best_regression(l_r_vs_c_b['lichess_rapid'], interp_rapid_ratings)
                
                else:  # CLASSICAL
                    df = self.lichess_data[['lichess_classical', 'chess_com_blitz']].dropna()
                    regression = find_best_regression(df['lichess_classical'], df['chess_com_blitz'])
                
                # Test that regression was created successfully
                self.assertIsNotNone(regression, f"{game_type} regression failed to create")
                self.assertIn('type', regression, f"{game_type} regression missing type")
                self.assertIn('params', regression, f"{game_type} regression missing params")
                self.assertIn(regression['type'], ['linear', 'quadratic', 'log'], 
                            f"{game_type} regression has invalid type: {regression['type']}")
                
                # Test calculation for each type
                test_ratings = [1200, 1500, 1800, 2100]
                for test_rating in test_ratings:
                    calculated = self.calculate_regression_value(regression, test_rating)
                    self.assertIsNotNone(calculated, 
                                       f"{game_type} calculation failed for rating {test_rating}")
                    self.assertGreaterEqual(calculated, 0, 
                                     f"{game_type} produced negative result for {test_rating}")
                    self.assertLess(calculated, 5000, 
                                   f"{game_type} produced unreasonably high result for {test_rating}")
                
                print(f"{game_type}: {regression['type']} regression with {len(regression['params'])} parameters")

    def test_classical_regression_investigation(self):
        """Investigate why classical regression produces negative results."""
        df_classical = self.lichess_data[['lichess_classical', 'chess_com_blitz']].dropna()
        
        print("\nClassical data analysis:")
        print(f"Data shape: {df_classical.shape}")
        print("First few rows:")
        print(df_classical.head())
        print("Last few rows:")
        print(df_classical.tail())
        
        # Check the range and relationship
        print(f"\nLichess Classical range: {df_classical['lichess_classical'].min()} - {df_classical['lichess_classical'].max()}")
        print(f"Chess.com Blitz range: {df_classical['chess_com_blitz'].min()} - {df_classical['chess_com_blitz'].max()}")
        
        regression = find_best_regression(df_classical['lichess_classical'], df_classical['chess_com_blitz'])
        print(f"\nRegression type: {regression['type']}")
        print(f"Regression params: {regression['params']}")
        
        # Test various ratings to see where it goes negative
        test_ratings = [1000, 1200, 1400, 1600, 1800, 2000, 2200]
        print("\nRating conversions:")
        for rating in test_ratings:
            calculated = self.calculate_regression_value(regression, rating)
            print(f"Lichess Classical {rating} → Chess.com Blitz {calculated}")
        
        # The issue might be that Classical ratings are typically much higher
        # than other time controls, so the regression might not work well
        # for lower classical ratings that aren't in the training data

    def test_negative_result_handling(self):
        """Test that negative regression results are handled by returning 0."""
        # Test with classical regression which can produce negative results for low ratings
        df_classical = self.lichess_data[['lichess_classical', 'chess_com_blitz']].dropna()
        regression = find_best_regression(df_classical['lichess_classical'], df_classical['chess_com_blitz'])
        
        # Test with a rating that would normally produce a negative result
        low_rating = 1200  # This should produce negative result with classical regression
        calculated = self.calculate_regression_value(regression, low_rating)
        
        # Should return 0 instead of negative value
        self.assertEqual(calculated, 0, 
                        f"Expected 0 for low classical rating {low_rating}, got {calculated}")
        
        # Test that higher ratings still work normally
        high_rating = 1500
        calculated_high = self.calculate_regression_value(regression, high_rating)
        self.assertGreater(calculated_high, 0, 
                          f"Higher rating {high_rating} should produce positive result")

if __name__ == '__main__':
    unittest.main()
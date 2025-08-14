from horseracepredictor import HorseRacePredictor

predictor = HorseRacePredictor()

# Load data
csv_file = "2019_Jan_Mar-4.csv"
predictor.load_data(csv_file)

# Train using original feature set and gradient descent
print("\nTraining model with original features using gradient descent...")
weights, biases = predictor.train_model()
print("Training completed.")
print("Weights:", weights.flatten())
print("Bias:", biases)

#  Summary of original feature model
print("\nSummary of predictions with feature set:")
predictor.summary(threshold=0.35, save_csv=True)

# Prepare expanded features
expanded_features = [
    'ncond', 'class', 'saddle', 'decimalPrice', 'isFav',
    'positionL', 'dist', 'headGear', 'runners', 'weight'
]
print(f"\nPreparing expanded feature: {expanded_features}")
predictor.prepare_features(expanded_features)

#  Train on expanded features with manual gradient descent
print("\nTraining model with expanded features using manual gradient descent...")
predictor.train_with_gradient_descent(iterations=26, learning_rate=0.02)

# Plot 3D visualization of two features vs predicted target
print("\nPlotting 3D features vs prediction...")
predictor.plot_3d_features_vs_prediction(feature_x='decimalPrice', feature_y='weight')

 # Plot predicted vs actual for expanded feature model (uncomment if needed)
print("\nPlotting predicted vs actual targets for expanded features...")
predictor.plot_predicted_vs_actual(threshold=0.35)




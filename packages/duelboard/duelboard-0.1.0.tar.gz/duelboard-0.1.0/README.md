# Duelboard

A high-performance Elo rating calculation library for tournaments and competitions, inspired by the Chatbot Arena rating system.

## Features

- **Multiple Calculation Methods**: Basic Elo, Bootstrap with confidence intervals, and Maximum Likelihood Estimation
- **High Performance**: Optimized for large datasets with thousands of battles
- **Type Safe**: Full type annotations and modern Python practices
- **Flexible Data Input**: Support for pandas DataFrames, CSV/JSON files, or Battle objects
- **Comprehensive Analysis**: Built-in tools for win rate prediction and pairwise analysis
- **Optional Visualization**: Beautiful plots with Plotly (optional dependency)

## Installation

```bash
# Basic installation
pip install duelboard

# With visualization support
pip install duelboard[visualization]

# Development installation
git clone https://github.com/jannchie/duelboard.git
cd duelboard
uv sync --extra visualization --group dev  # with visualization and dev tools
```

## Quick Start

```python
import pandas as pd
import duelboard as db

# Load your battle data
battles_df = pd.DataFrame([
    {"player_a": "gpt-4", "player_b": "claude-v1", "winner": "player_a"},
    {"player_a": "claude-v1", "player_b": "gpt-3.5-turbo", "winner": "player_a"},
    {"player_a": "gpt-4", "player_b": "gpt-3.5-turbo", "winner": "player_a"},
    # ... more battles
])

# Calculate Elo ratings
calculator = db.EloCalculator(k_factor=4)
ratings = calculator.calculate(battles_df)

# Get leaderboard
leaderboard = db.get_rating_summary(ratings)
print(leaderboard)
```

## Calculation Methods

### 1. Basic Elo Calculator

Standard online Elo rating updates:

```python
calculator = db.EloCalculator(
    k_factor=4,           # Lower = more stable ratings
    scale=400,            # Elo scale parameter
    initial_rating=1000   # Starting rating
)
ratings = calculator.calculate(battles_df)
```

### 2. Bootstrap Elo Calculator

Provides confidence intervals through bootstrap sampling:

```python
bootstrap_calc = db.BootstrapEloCalculator(
    k_factor=4,
    n_bootstrap=1000,     # Number of bootstrap samples
    confidence_level=0.95,
    random_seed=42
)
ratings = bootstrap_calc.calculate(battles_df)

# Access confidence intervals
for player, rating in ratings.items():
    print(f"{player}: {rating.rating:.0f} [{rating.confidence_interval[0]:.0f}, {rating.confidence_interval[1]:.0f}]")
```

### 3. Maximum Likelihood Estimation

Uses logistic regression for more stable ratings:

```python
mle_calc = db.MLEEloCalculator(random_state=42)
ratings = mle_calc.calculate(battles_df)

# With bootstrap confidence intervals
ratings = mle_calc.calculate_with_bootstrap(battles_df, n_bootstrap=500)
```

## Analysis Tools

### Win Rate Prediction

```python
predictor = db.WinRatePredictor()

# Predict win probability
prob = predictor.predict_win_probability(1200, 1000)  # ratings
print(f"Win probability: {prob:.3f}")

# Create win rate matrix
win_matrix = predictor.create_win_rate_matrix(ratings)
```

### Battle Statistics

```python
analyzer = db.PairwiseAnalyzer()

# Basic battle statistics
stats = analyzer.compute_battle_statistics(battles_df)

# Pairwise win fractions
win_fractions = analyzer.compute_pairwise_win_fraction(battles_df)

# Battle count matrix
battle_counts = analyzer.visualize_battle_count_matrix(battles_df)
```

## Visualization (Optional)

```python
# Install with: pip install duelboard[visualization]
import duelboard.visualization as viz

# Plot leaderboard with confidence intervals
fig = viz.plot_leaderboard(ratings, show_confidence_intervals=True)
fig.show()

# Plot win rate matrix
win_matrix = predictor.create_win_rate_matrix(ratings)
fig = viz.plot_win_rate_matrix(win_matrix)
fig.show()

# Plot battle count matrix
battle_counts = analyzer.visualize_battle_count_matrix(battles_df)
fig = viz.plot_battle_count_matrix(battle_counts)
fig.show()
```

## Data Formats

### DataFrame Format

```python
battles_df = pd.DataFrame({
    'player_a': ['player1', 'player2', 'player1'],
    'player_b': ['player2', 'player3', 'player3'], 
    'winner': ['player_a', 'player_b', 'tie']
})
```

### Battle Objects

```python
# Recommended: Use intuitive win/tie methods
battles = [
    db.Battle.win('player1', 'player2'),    # player1 beats player2
    db.Battle.win('player3', 'player2'),    # player3 beats player2
    db.Battle.tie('player1', 'player3'),    # tie between player1 and player3
]

# Traditional API with outcome enums (for advanced use cases)
battles = [
    db.Battle('player1', 'player2', db.BattleOutcome.WIN_A),
    db.Battle('player2', 'player3', db.BattleOutcome.WIN_B),
    db.Battle('player1', 'player3', db.BattleOutcome.TIE)
]
```

### Load from Files

```python
# From CSV
battles = db.load_battles_from_csv('battles.csv')

# From JSON  
battles = db.load_battles_from_json('battles.json')
```

## Advanced Usage

### Filter Anonymous Battles (Chatbot Arena Style)

```python
# Filter to only anonymous battles
anonymous_df = db.filter_anonymous_battles(df, anony_col='anony')

# Filter out ties
no_ties_df = db.filter_non_tie_battles(df)
```

### Even Sampling Across Model Pairs

```python
bootstrap_calc = db.BootstrapEloCalculator()
ratings = bootstrap_calc.calculate_even_sample(
    battles_df, 
    n_per_pair=50  # Sample 50 battles per model pair
)
```

### Export Results

```python
# Export to CSV
db.export_ratings_to_csv(ratings, 'ratings.csv')

# Get ranked player list
ranked_players = db.rank_players_by_rating(ratings)
```

## Performance Tips

- Use `k_factor=4` for stable ratings (as used in Chatbot Arena)
- For large datasets, consider filtering to anonymous battles only
- Use MLE calculator for most stable results
- Bootstrap calculations are slower but provide uncertainty estimates
- Reduce `n_bootstrap` for faster computation during development

## Development

```bash
# Install dependencies with visualization and dev tools
uv sync --extra visualization --group dev

# Run tests
pytest

# Run tests with coverage
pytest --cov=src/duelboard --cov-report=html

# Run examples
python examples/simple_example.py
python examples/basic_usage.py
python examples/visualization_example.py

# Format and lint code
ruff check --fix
```

## License

MIT License. See LICENSE file for details.

## Citation

Inspired by the Chatbot Arena Elo rating system. If you use this library in academic work, please cite:

```txt
Zheng, L., Chiang, W. L., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, Y., ... & Stoica, I. (2023). 
Judging LLM-as-a-judge with MT-Bench and Chatbot Arena. arXiv preprint arXiv:2306.05685.
```

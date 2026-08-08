from backend.data import load_transactions
from backend.model import train_model, score_transactions
from backend.graph import graph_scores

df, src = load_transactions()
print("Source:", src)
print("Total rows:", len(df))
print("isFraud counts:", df['isFraud'].value_counts().to_dict())

bundle = train_model(df)
scored = score_transactions(bundle, df)
scored, _ = graph_scores(scored)

scored['combined'] = 0.65 * scored['base_risk_score'] + 0.35 * scored['graph_collusion_score']
scored_sorted = scored.sort_values('combined', ascending=False).head(50)

# Check risk tier distribution in top 50
def tier(row):
    s = row['combined']
    if s >= 0.6: return 'high'
    elif s >= 0.35: return 'medium'
    return 'low'

scored_sorted['tier'] = scored_sorted.apply(tier, axis=1)
print("Tier distribution in top 50:", scored_sorted['tier'].value_counts().to_dict())
print("Score range:", scored_sorted['combined'].min(), "-", scored_sorted['combined'].max())

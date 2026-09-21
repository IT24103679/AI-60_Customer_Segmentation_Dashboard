import os
from flask import Flask, render_template, jsonify, request
import pandas as pd

app = Flask(__name__)

# Base directory for data files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def load_data():
    """Load and process all required CSV datasets."""
    data = {}
    
    # 1. Segmentation Results
    seg_path = os.path.join(DATA_DIR, 'segmentation_results.csv')
    if os.path.exists(seg_path):
        data['segmentation_results'] = pd.read_csv(seg_path)
    else:
        data['segmentation_results'] = pd.DataFrame()

    # 2. Segment Labels Mapping
    mapping_path = os.path.join(DATA_DIR, 'segment_labels_mapping.csv')
    if os.path.exists(mapping_path):
        data['labels_mapping'] = pd.read_csv(mapping_path)
    else:
        data['labels_mapping'] = pd.DataFrame()

    # 3. Association Rules Summary
    rules_sum_path = os.path.join(DATA_DIR, 'association_rules_summary.csv')
    if os.path.exists(rules_sum_path):
        data['rules_summary'] = pd.read_csv(rules_sum_path)
    else:
        data['rules_summary'] = pd.DataFrame()

    # 4. Bundle Recommendations
    bundles_path = os.path.join(DATA_DIR, 'bundle_recommendations.csv')
    if os.path.exists(bundles_path):
        data['bundles'] = pd.read_csv(bundles_path)
    else:
        data['bundles'] = pd.DataFrame()

    # 5. Segment Profiles
    profiles_path = os.path.join(DATA_DIR, 'segment_profiles.csv')
    if os.path.exists(profiles_path):
        # The CSV has a 2-row multi-index header:
        # ,Recency,Recency,Recency,Frequency,Frequency,Monetary,Monetary
        # ,mean,median,count,mean,median,mean,median
        # Final_Cluster,,,,,,,
        try:
            raw_profiles = pd.read_csv(profiles_path, header=[0, 1], index_col=0)
            profiles_list = []
            
            # Map known cluster labels
            cluster_labels = {
                0: {"name": "Regular Average Customers (Mid-Tier)", "badge": "Regular", "color": "#2563eb"},
                1: {"name": "At-Risk Customers", "badge": "At-Risk", "color": "#ef4444"},
                2: {"name": "New / Occasional Buyers", "badge": "New / Occasional", "color": "#f59e0b"},
                3: {"name": "High-Value Regular Customers", "badge": "High-Value", "color": "#10b981"}
            }

            for cluster_idx, row in raw_profiles.iterrows():
                cid = int(cluster_idx)
                cinfo = cluster_labels.get(cid, {"name": f"Cluster {cid}", "badge": "Active", "color": "#3b82f6"})
                profiles_list.append({
                    "cluster_id": cid,
                    "label": cinfo["name"],
                    "badge": cinfo["badge"],
                    "color": cinfo["color"],
                    "count": int(row.get(('Recency', 'count'), 0)),
                    "recency_mean": round(float(row.get(('Recency', 'mean'), 0)), 1),
                    "recency_median": round(float(row.get(('Recency', 'median'), 0)), 1),
                    "frequency_mean": round(float(row.get(('Frequency', 'mean'), 0)), 2),
                    "frequency_median": round(float(row.get(('Frequency', 'median'), 0)), 1),
                    "monetary_mean": round(float(row.get(('Monetary', 'mean'), 0)), 2),
                    "monetary_median": round(float(row.get(('Monetary', 'median'), 0)), 2)
                })
            data['profiles'] = profiles_list
        except Exception as e:
            print(f"Error parsing segment_profiles.csv: {e}")
            data['profiles'] = []
    else:
        data['profiles'] = []

    return data

# Preload data on startup
APP_DATA = load_data()


# Model comparison benchmark metrics
MODEL_COMPARISON_DATA = [
    {
        "model": "K-Means",
        "clusters": 4,
        "silhouette": 0.4082,
        "davies_bouldin": 0.9155,
        "calinski_harabasz": 3701.14,
        "status": "Champion Model",
        "badge_class": "badge-champion",
        "notes": "Optimal cluster balance, tight intra-cluster distance, best business applicability."
    },
    {
        "model": "Hierarchical (Agglomerative)",
        "clusters": 4,
        "silhouette": 0.3952,
        "davies_bouldin": 0.9995,
        "calinski_harabasz": 2816.05,
        "status": "Challenger Model",
        "badge_class": "badge-secondary",
        "notes": "Ward linkage preserves cluster hierarchies but computationally intensive for large scale."
    },
    {
        "model": "DBSCAN",
        "clusters": "Varying (1-34)",
        "silhouette": -0.0975,
        "davies_bouldin": "N/A",
        "calinski_harabasz": "N/A",
        "status": "Excluded",
        "badge_class": "badge-muted",
        "notes": "Struggles with variable density across RFM feature spaces; high proportion of noise points."
    }
]


@app.route('/')
def home():
    """Home Page: 4 metric cards + 2 info boxes."""
    summary_metrics = {
        "total_transactions": "541,909",
        "unique_customers": "4,372",
        "segmented_customers": "3,614",
        "num_segments": 4,
        "total_rules": 761,
        "top_bundles": len(APP_DATA.get('bundles', []))
    }
    return render_template('index.html', active_page='home', metrics=summary_metrics)


@app.route('/eda')
def eda():
    """EDA Page: Data quality issues + Business insights + Visual exhibits."""
    return render_template('eda.html', active_page='eda')


@app.route('/segments')
def segments():
    """Segments Page: Bar chart, Pie chart, Segment profiles table, Expandable details."""
    profiles = APP_DATA.get('profiles', [])
    
    # Segment narrative cards with business strategies
    segment_narratives = [
        {
            "id": 0,
            "title": "Cluster 0 & 3: Regular Average Customers",
            "subtitle": "Core Steady Spenders & Frequent Loyalists",
            "tag": "1,316 Customers (36.4%)",
            "icon": "fa-user-check",
            "color_theme": "blue",
            "recency_desc": "Active within past 33–42 days",
            "frequency_desc": "4.3 to 7.3 purchases per year",
            "monetary_desc": "$824.70 to $1,666.02 average expenditure",
            "behavior": "Consistent, trustworthy transaction history with balanced repeat purchasing patterns. Cluster 3 represents the top-spending echelon.",
            "strategies": [
                "Enroll in tiered loyalty and VIP early-access reward programs.",
                "Cross-sell multi-pack bundles (e.g. Poppy's Playhouse & Regency tea sets).",
                "Personalized product recommendation emails triggered after 30 days of inactivity."
            ]
        },
        {
            "id": 2,
            "title": "Cluster 2: New / Occasional Buyers",
            "subtitle": "Recent First-Time & Exploratory Shoppers",
            "tag": "1,421 Customers (39.3%)",
            "icon": "fa-user-plus",
            "color_theme": "amber",
            "recency_desc": "Active within past 51 days (median 45 days)",
            "frequency_desc": "1.7 purchases on average",
            "monetary_desc": "$293.07 average spending",
            "behavior": "New or sporadic purchasers who have interacted recently but have not yet developed routine purchasing habits.",
            "strategies": [
                "Implement automated 3-stage onboarding email sequence highlighting bestsellers.",
                "Provide a 10-15% discount voucher redeemable on their 2nd purchase within 21 days.",
                "Recommend beginner gift bundles (e.g. Birthday bunting and party sets)."
            ]
        },
        {
            "id": 1,
            "title": "Cluster 1: At-Risk Customers",
            "subtitle": "Lapsed High-Dormancy Accounts",
            "tag": "877 Customers (24.3%)",
            "icon": "fa-user-clock",
            "color_theme": "red",
            "recency_desc": "High inactivity (mean 233.8 days, median 234 days)",
            "frequency_desc": "1.6 purchases historically",
            "monetary_desc": "$261.57 average spending",
            "behavior": "Customers who haven't ordered in over 7 to 8 months. Risk of permanent churn is high without decisive intervention.",
            "strategies": [
                "Launch targeted 'We Miss You' win-back reactivation campaigns.",
                "Conduct short feedback surveys with an instant incentive to discover friction points.",
                "Promote clearance and seasonal clearance bundles with high discount lift."
            ]
        }
    ]

    return render_template('segments.html', 
                           active_page='segments', 
                           profiles=profiles, 
                           narratives=segment_narratives)


@app.route('/bundles')
def bundles():
    """Bundles Page: Segment dropdown filter, bundle recommendations table, and lift charts."""
    bundles_df = APP_DATA.get('bundles', pd.DataFrame())
    rules_sum_df = APP_DATA.get('rules_summary', pd.DataFrame())

    segments_list = ["All Segments"]
    if not bundles_df.empty and 'Segment' in bundles_df.columns:
        segments_list.extend(bundles_df['Segment'].unique().tolist())

    bundles_records = bundles_df.to_dict(orient='records') if not bundles_df.empty else []
    rules_summary_records = rules_sum_df.to_dict(orient='records') if not rules_sum_df.empty else []

    return render_template('bundles.html', 
                           active_page='bundles',
                           segments=segments_list,
                           bundles=bundles_records,
                           rules_summary=rules_summary_records)


@app.route('/models')
def models():
    """Models Page: Model comparison table, silhouette score chart, champion model info."""
    return render_template('models.html', 
                           active_page='models',
                           model_data=MODEL_COMPARISON_DATA)


# ==========================================
# JSON API ENDPOINTS FOR DYNAMIC CHART.JS
# ==========================================

@app.route('/api/segments-data')
def api_segments_data():
    """Return customer segment counts and percentages for charts."""
    profiles = APP_DATA.get('profiles', [])
    labels = [p['label'] for p in profiles]
    counts = [p['count'] for p in profiles]
    colors = [p['color'] for p in profiles]
    
    # Aggregated 3-label mapping
    # New/Occasional: 1421, Regular Average: 1316, At-Risk: 877
    aggregated = {
        "labels": ["New / Occasional Buyers", "Regular Average Customers", "At-Risk Customers"],
        "counts": [1421, 1316, 877],
        "colors": ["#f59e0b", "#2563eb", "#ef4444"]
    }

    return jsonify({
        "cluster_labels": labels,
        "cluster_counts": counts,
        "cluster_colors": colors,
        "aggregated": aggregated
    })


@app.route('/api/bundles-data')
def api_bundles_data():
    """Return filtered bundle recommendation records."""
    segment_query = request.args.get('segment', 'All Segments')
    bundles_df = APP_DATA.get('bundles', pd.DataFrame())

    if bundles_df.empty:
        return jsonify([])

    if segment_query != 'All Segments':
        filtered = bundles_df[bundles_df['Segment'] == segment_query]
    else:
        filtered = bundles_df

    # Sort by Lift descending
    if 'Lift' in filtered.columns:
        filtered = filtered.sort_values(by='Lift', ascending=False)

    return jsonify(filtered.to_dict(orient='records'))


@app.route('/api/models-data')
def api_models_data():
    """Return comparison data for the models comparison chart."""
    models = ["K-Means", "Hierarchical", "DBSCAN"]
    silhouettes = [0.4082, 0.3952, -0.0975]
    davies_bouldin = [0.9155, 0.9995, 0] # DBSCAN 0 for display
    return jsonify({
        "models": models,
        "silhouette_scores": silhouettes,
        "davies_bouldin_scores": davies_bouldin
    })


if __name__ == '__main__':
    # Run development server
    app.run(host='127.0.0.1', port=5000, debug=True)

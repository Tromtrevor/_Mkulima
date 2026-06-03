import json
from .groq_client import client



def generate_crop_insight(data):

    latest = data.get("latest", {})
    profit_analysis = data.get("profit_analysis", {})

    prompt = f"""
    County: {latest['county']}
    Farm Size: {latest['farm_size']} acres
    Crop: {profit_analysis['crop']}

    Soil pH: {latest['input_data']['pH']}
    Average Rainfall: {latest['input_data']['Precipitation']} mm/year
    Average Temperature (Min): {latest['input_data']['mean Tmin']} °C
    Average Temperature (Max): {latest['input_data']['mean Tmax']} °C    
    
    Predicted Yield: {profit_analysis['predicted_yield']} t/acre
    Market Price: KES {profit_analysis['market_price']} per bag
    Estimated Profit: KES {profit_analysis['profit']['total_profit']}
    Profit Margin: {profit_analysis['profit_margin']}%

    Provide analysis in valid JSON format with these exact keys:
    {{
        "insight": "1-2 sentence main takeaway about profitability and viability",
        "recommendations": ["recommendation 1", "recommendation 2", "recommendation 3", "recommendation 4"],
        "warnings": ["warning 1", "warning 2"],
        "market_trends": "Brief market outlook for this crop in this region",
        "best_practices": ["practice 1", "practice 2", "practice 3"],
        "roi_info": "Expected return on investment and timeline",
        "notes": "Any additional considerations or intercropping suggestions"
    }}

    Guidelines:
    - Keep all text SHORT and PRACTICAL for farmers
    - Recommendations should be actionable
    - Suggest intercropping if farm size allows (>{latest['farm_size']} acres)
    - Consider N-P-K levels for intercrop suggestions
    - Warnings should highlight risks
    - Best practices should be region-specific to {latest['county']}
    - Use local context and Kenyan agricultural practices
    - Response MUST be valid JSON only, no markdown or extra text
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert agronomist for Kenyan smallholder farmers. "
                    "Provide structured, actionable agricultural insights. "
                    "Always respond with valid JSON only."
                )
            },
            {"role": "user", "content": prompt},
        ],
    )

    # --- safe parsing: ensure we pass a str to json.loads ---
    raw_content = ""
    try:
        choices = getattr(response, "choices", [])
        if choices and getattr(choices[0], "message", None):
            raw_content = getattr(choices[0].message, "content", "") or ""
    except Exception as e:
        raw_content = ""
        # optionally log: logger.exception("Failed to extract content: %s", e)

    if raw_content:
        try:
            insight_data = json.loads(raw_content)
            return {"Insights": insight_data}
        except json.JSONDecodeError:
            # fallback: return raw text and empty structured fields
            # optionally log raw_content for debugging
            return {
                "insight": raw_content,
                "recommendations": [],
                "warnings": [],
                "market_trends": [],
                "best_practices": [],
                "roi_info": [],
            }
    else:
        # empty or missing content: return safe default
        return {
            "insight": "",
            "recommendations": [],
            "warnings": [],
            "market_trends": [],
            "best_practices": [],
            "roi_info": [],
        }
# ...existing code...
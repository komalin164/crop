"""Government scheme information for farmers (AP, TG, Central)."""
SCHEMES = [
    {
        "id": "pm-kisan",
        "name_en": "PM-KISAN",
        "name_te": "పీఎం-కిసాన్",
        "name_hi": "पीएम-किसान",
        "amount": "Rs 6,000/year in 3 installments",
        "eligibility": "Landholding farmers; 2 ha limit",
        "link": "https://pmkisan.gov.in",
        "state": "Central",
    },
    {
        "id": "rythu-bharosa",
        "name_en": "Rythu Bharosa",
        "name_te": "రైతు భరోసా",
        "name_hi": "रैथु भरोसा",
        "amount": "Rs 15,000/year (AP); Rs 10,000 (TG)",
        "eligibility": "Landholding farmers; tenant farmers",
        "link": "https://rythubharosa.ap.gov.in",
        "state": "AP/TG",
    },
    {
        "id": "pmfby",
        "name_en": "PM Fasal Bima Yojana",
        "name_te": "పీఎం ఫసల్ బీమా యోజన",
        "name_hi": "पीएम फसल बीमा योजना",
        "amount": "Crop insurance; premium subsidy",
        "eligibility": "All farmers; loanee/non-loanee",
        "link": "https://pmfby.gov.in",
        "state": "Central",
    },
    {
        "id": "kcc",
        "name_en": "Kisan Credit Card",
        "name_te": "కిసాన్ క్రెడిట్ కార్డ్",
        "name_hi": "किसान क्रेडिट कार्ड",
        "amount": "Credit up to Rs 3L at 4% interest",
        "eligibility": "Farmers, livestock, fisheries",
        "link": "https://www.pmfby.gov.in/kcc",
        "state": "Central",
    },
    {
        "id": "soil-health",
        "name_en": "Soil Health Card",
        "name_te": "సాయిల్ హెల్త్ కార్డ్",
        "name_hi": "मृदा स्वास्थ्य कार्ड",
        "amount": "Free soil testing every 2 years",
        "eligibility": "All farmers",
        "link": "https://soilhealth.dac.gov.in",
        "state": "Central",
    },
    {
        "id": "rythu-bima",
        "name_en": "Rythu Bima",
        "name_te": "రైతు బీమా",
        "name_hi": "रैथु बीमा",
        "amount": "Rs 5L life insurance",
        "eligibility": "Farmers 18-59 years",
        "link": "https://rythubima.telangana.gov.in",
        "state": "TG",
    },
]


def get_schemes(lang: str = "en") -> list:
    name_key = f"name_{lang}" if lang in ("te", "hi") else "name_en"
    return [
        {**s, "name": s.get(name_key, s["name_en"])}
        for s in SCHEMES
    ]

"""
Merchant Categorization Engine
"""

from typing import Dict, List

DEFAULT_CATEGORY_MAP: Dict[str, List[str]] = {
    "Food": [
        "swiggy", "zomato", "canteen", "tea", "restaurant",
        "instamart", "cafe", "coffee", "bakery", "dinner", "lunch"
    ],
    "Travel": [
        "ola", "uber", "rapido", "metro", "petrol", "fuel",
        "bpcl", "hpcl", "iocl", "ride", "auto", "flight", "taxi"
    ],
    "Shopping": [
        "dmart", "amazon", "flipkart", "myntra", "ajio",
        "supermarket", "fashion", "mall", "purchase", "order"
    ],
    "Bills": [
        "recharge", "electricity", "wifi", "ticket", "bill",
        "bescom", "airtel", "jio", "water", "broadband", "card"
    ],
    "Health": [
        "pharmacy", "gym", "medical", "hospital", "clinic",
        "doctor", "fitness", "medicine", "chemist"
    ],
    "Entertainment": [
        "netflix", "spotify", "youtube", "cinema", "movie",
        "prime", "hotstar", "gaming", "pvr"
    ],
}


class CategorizerService:
    def __init__(self, custom_rules: Dict[str, List[str]] = None):
        self.category_map: Dict[str, List[str]] = custom_rules or {
            k: list(v) for k, v in DEFAULT_CATEGORY_MAP.items()
        }

    def get_category(self, merchant_name: str) -> str:
        """Categorize a merchant based on keyword substring matching."""
        merchant_clean = merchant_name.lower().strip()

        for category, keywords in self.category_map.items():
            for kw in keywords:
                if kw in merchant_clean:
                    return category

        return "Other"

    def register_keyword(self, category: str, keyword: str) -> bool:
        """Dynamically learn or extend category keyword mappings."""
        kw_clean = keyword.lower().strip()
        if category not in self.category_map:
            self.category_map[category] = []
        if kw_clean not in self.category_map[category]:
            self.category_map[category].append(kw_clean)
            return True
        return False


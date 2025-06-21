# product_info.py
import wikipedia

PRODUCT_DB = {
    "bottle": {
        "manufacturer": "Bisleri Ltd",
        "year": "2023",
        "details": "Eco-friendly plastic water bottle"
    },
    "keyboard": {
        "manufacturer": "Logitech",
        "year": "2021",
        "details": "Wireless mechanical keyboard"
    }
}

def get_product_details(name):
    details = PRODUCT_DB.get(name, {
        "manufacturer": "Unknown",
        "year": "N/A",
        "details": "No extra data in local DB"
    })
    try:
        summary = wikipedia.summary(name, sentences=2)
    except:
        summary = "No summary available."
    return {
        **details,
        "description": summary
    }

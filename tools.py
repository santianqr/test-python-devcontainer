"""Tools for the WhatsApp AI Agent."""

from datetime import datetime, timedelta

from langchain.tools import tool


@tool
def check_property_availability(property_id: str, check_in: str, check_out: str) -> str:
    """Check availability for Airbnb property.

    Args:
        property_id: Property identifier (e.g., "miami_beach_01", "downtown_02")
        check_in: Check-in date in YYYY-MM-DD format
        check_out: Check-out date in YYYY-MM-DD format

    Returns:
        Availability status and pricing information
    """
    dummy_properties = {
        "miami_beach_01": {
            "name": "Ocean View Apartment - Miami Beach",
            "base_price": 150,
            "available_dates": ["2024-03-15", "2024-03-16", "2024-03-17", "2024-03-20", "2024-03-25"],
        },
        "downtown_02": {
            "name": "Downtown Miami Loft",
            "base_price": 120,
            "available_dates": ["2024-03-18", "2024-03-19", "2024-03-22", "2024-03-23", "2024-03-24"],
        },
        "brickell_03": {
            "name": "Brickell High-Rise Condo",
            "base_price": 200,
            "available_dates": ["2024-03-15", "2024-03-16", "2024-03-21", "2024-03-22", "2024-03-26"],
        },
    }

    if property_id not in dummy_properties:
        available_props = ", ".join(dummy_properties.keys())
        return f"Property {property_id} not found. Available properties: {available_props}"

    property_info = dummy_properties[property_id]

    try:
        check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
        check_out_date = datetime.strptime(check_out, "%Y-%m-%d")

        if check_in_date >= check_out_date:
            return "Check-in date must be before check-out date."

        nights = (check_out_date - check_in_date).days
        current_date = check_in_date
        available_nights = []

        while current_date < check_out_date:
            date_str = current_date.strftime("%Y-%m-%d")
            available_dates: list[str] = property_info["available_dates"]
            if date_str in available_dates:
                available_nights.append(date_str)
            current_date += timedelta(days=1)

        if len(available_nights) == nights:
            base_price: int = property_info["base_price"]
            total_price = nights * base_price
            return f"""✅ AVAILABLE: {property_info['name']}
📅 Dates: {check_in} to {check_out} ({nights} nights)
💰 Price: ${property_info['base_price']}/night × {nights} nights = ${total_price}
📍 All requested dates are available!"""
        else:
            unavailable_nights = nights - len(available_nights)
            return f"""❌ PARTIALLY AVAILABLE: {property_info['name']}
📅 Requested: {check_in} to {check_out} ({nights} nights)
✅ Available: {len(available_nights)} nights
❌ Unavailable: {unavailable_nights} nights
💡 Try different dates or check other properties."""

    except ValueError:
        return "Invalid date format. Please use YYYY-MM-DD format."


@tool
def get_property_details(property_id: str) -> str:
    """Get detailed information about a specific property.

    Args:
        property_id: Property identifier

    Returns:
        Detailed property information
    """
    dummy_properties = {
        "miami_beach_01": {
            "name": "Ocean View Apartment - Miami Beach",
            "description": "Stunning 2BR/2BA apartment with direct ocean views",
            "amenities": ["Ocean view", "WiFi", "Kitchen", "Parking", "Pool", "Gym"],
            "capacity": "4 guests",
            "location": "Miami Beach, FL",
            "check_in": "3:00 PM",
            "check_out": "11:00 AM",
            "base_price": 150,
        },
        "downtown_02": {
            "name": "Downtown Miami Loft",
            "description": "Modern loft in the heart of downtown Miami",
            "amenities": ["City view", "WiFi", "Kitchen", "Parking", "Rooftop terrace"],
            "capacity": "2 guests",
            "location": "Downtown Miami, FL",
            "check_in": "3:00 PM",
            "check_out": "11:00 AM",
            "base_price": 120,
        },
        "brickell_03": {
            "name": "Brickell High-Rise Condo",
            "description": "Luxury condo with bay views in Brickell",
            "amenities": ["Bay view", "WiFi", "Kitchen", "Parking", "Pool", "Spa", "Concierge"],
            "capacity": "6 guests",
            "location": "Brickell, Miami, FL",
            "check_in": "4:00 PM",
            "check_out": "11:00 AM",
            "base_price": 200,
        },
    }

    if property_id not in dummy_properties:
        available_props = ", ".join(dummy_properties.keys())
        return f"Property {property_id} not found. Available properties: {available_props}"

    prop = dummy_properties[property_id]
    return f"""🏠 {prop['name']}
📍 Location: {prop['location']}
👥 Capacity: {prop['capacity']}
💰 Price: ${prop['base_price']}/night

📝 Description: {prop['description']}

🎯 Amenities:
{chr(10).join(f"• {amenity}" for amenity in prop['amenities'])}

⏰ Check-in: {prop['check_in']}
⏰ Check-out: {prop['check_out']}"""


@tool
def list_available_properties() -> str:
    """List all available properties with basic information.

    Returns:
        List of all properties with basic details
    """
    return """🏠 Available Properties:

1️⃣ miami_beach_01 - Ocean View Apartment
   📍 Miami Beach | 👥 4 guests | 💰 $150/night
   
2️⃣ downtown_02 - Downtown Miami Loft  
   📍 Downtown Miami | 👥 2 guests | 💰 $120/night
   
3️⃣ brickell_03 - Brickell High-Rise Condo
   📍 Brickell | 👥 6 guests | 💰 $200/night

💡 Use property IDs (miami_beach_01, downtown_02, brickell_03) to check availability or get details."""

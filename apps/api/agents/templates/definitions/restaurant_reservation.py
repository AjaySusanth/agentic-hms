"""
Restaurant Reservation workflow template.
Defines the steps for booking a table at any restaurant.
This is the LOGIC layer — it says WHAT happens.
The YAML config says WHERE it happens (which API, which field names).
"""

from agents.templates.schemas import TemplateDefinition


RESTAURANT_RESERVATION_TEMPLATE = TemplateDefinition(
    name="restaurant_reservation",
    description="Book a table at a restaurant",
    steps=[
        {
            "id": "collect_date_time",
            "type": "collect_input",
            "prompt": (
                "What date and time would you like to dine?\n"
                "Please provide in a format like: **March 15th at 7 PM**"
            ),
            "fields": ["reservation_date", "reservation_time"],
            "next": "collect_party_size",
        },
        {
            "id": "collect_party_size",
            "type": "collect_input",
            "prompt": "How many guests will be dining?",
            "fields": ["party_size"],
            "next": "search_tables",
        },
        {
            "id": "search_tables",
            "type": "api_call",
            "action": "search_tables",
            "display_results": True,
            "prompt": (
                "Here are the available tables:\n\n{results}\n\n"
                "Which table would you prefer? (Enter the number)"
            ),
            "fields": [],
            "next": "select_table",
        },
        {
            "id": "select_table",
            "type": "collect_input",
            "prompt": "",  # prompt is rendered dynamically from search results
            "fields": ["selected_table_id"],
            "next": "collect_guest_details",
        },
        {
            "id": "collect_guest_details",
            "type": "collect_input",
            "prompt": "Please provide your **name** and **phone number** for the reservation.",
            "fields": ["guest_name", "phone"],
            "next": "confirm_reservation",
        },
        {
            "id": "confirm_reservation",
            "type": "api_call",
            "action": "create_reservation",
            "display_results": False,
            "prompt": "Your reservation is confirmed! 🎉\n\n{results}",
            "fields": [],
            "next": "completed",
        },
    ],
)

import json
from datetime import datetime

def generate_status_report(json_file, report_date):
    def parse_date(date_string):
        """Helper to format dates or return None."""
        if not date_string:
            return None
        return datetime.fromisoformat(date_string.replace('Z', '+00:00')).strftime('%Y-%m-%d')

    try:
        # Load the JSON data
        with open(json_file, 'r') as file:
            data = json.load(file)

        # Extract lists, cards, labels, and checklist items
        lists = {lst["_id"]: lst["title"] for lst in data["lists"]}
        cards = data["cards"]
        labels = {lbl["_id"]: lbl["name"] for lbl in data.get("labels", [])}
        checklist_items = data.get("checklistItems", [])

        # Map checklist items to their respective cards
        card_checklists = {}
        for item in checklist_items:
            card_id = item["cardId"]
            status_symbol = "✅" if item.get("isFinished", False) else "⚒" if item.get("sort", 0) == 0 else "🔲"
            card_checklists.setdefault(card_id, []).append({
                "title": item["title"],
                "status": status_symbol
            })

        # Group cards by lists
        grouped_cards = {}
        for card in cards:
            list_title = lists.get(card["listId"], "Unknown List")
            grouped_cards.setdefault(list_title, []).append(card)

        # Generate the report
        report = [f"Status Report, Week Ending {report_date}\n"]
        for list_title, cards in grouped_cards.items():
            report.append(f"\nList: {list_title}\n" + "-" * 80)
            for card in cards:
                card_title = card.get("title", "Untitled")
                start_date = parse_date(card.get("startAt"))
                due_date = parse_date(card.get("dueAt"))
                labels_on_card = ", ".join([labels[label_id] for label_id in card.get("labelIds", [])]) or "None"
                non_completed_items = card_checklists.get(card["_id"], [])

                # Card Header
                report.append(f" Card: {card_title}")
                if start_date:
                    report.append(f" Start Date: {start_date}")
                if due_date:
                    report.append(f" Due Date: {due_date}")
                report.append(f" Labels: {labels_on_card}")

                # Checklist Items
                report.append("Tasks:")
                if non_completed_items:
                    for item in non_completed_items:
                        report.append(f"   - {item['status']} {item['title']}")
                else:
                    report.append("   None")
                report.append("-" * 80)

        # Print the report
        print("\n".join(report))

    except FileNotFoundError:
        print(f"File not found: {json_file}")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Replace 'export-board-11222024.json' with the path to your Wekan Board export JSON file
# ToDo: Make the date dynamic... maybe
generate_status_report('export-board-11222024.json', '11/22/2024')
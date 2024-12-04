from datetime import datetime
import requests
import xml.etree.ElementTree as ET

# URL of the Atom feed
url = "https://www.imperial.ac.uk/events/feed/atom/?campus=south-kensington"

# Send a GET request to the API
response = requests.get(url)

# Ensure the request was successful (status code 200)
if response.status_code == 200:
    # Parse the XML response
    root = ET.fromstring(response.text)

    # Define namespaces to handle the XML correctly
    namespaces = {
        "atom": "http://www.w3.org/2005/Atom",
        "imperialnewsevents": "http://www3.imperial.ac.uk/imperialnewsevents/schema",
    }

    # Extract event details
    events = []
    for entry in root.findall("atom:entry", namespaces):
        # Extract category
        category = entry.find("imperialnewsevents:category", namespaces)
        category = category.text if category is not None else "No category"

        if category not in ["Workshop", "Seminar", "Practice session", "Training Course"]:
            continue  # Filter for workshops only

        # Extract title
        title = entry.find("atom:title", namespaces).text

        # Extract summary
        summary = entry.find("atom:summary", namespaces)
        summary = (
            summary.text if summary is not None else "No summary available"
        )

        # Extract start date and time
        start_date_element = entry.find(
            "imperialnewsevents:event_start_date", namespaces
        )
        if start_date_element is not None:
            start_date = start_date_element.text  # Full date-time value
        else:
            start_date = "Unknown start date"

        # Extract end date and time
        end_date_element = entry.find(
            "imperialnewsevents:event_end_date", namespaces
        )
        if end_date_element is not None:
            end_date = end_date_element.text  # Full date-time value
        else:
            end_date = "Unknown end date"

        # Extract event link
        event_link = entry.find("atom:link", namespaces)
        event_link = (
            event_link.attrib["href"]
            if event_link is not None
            else "No link available"
        )

        # Format the start and end dates for display
        def format_datetime(dt_string):
            try:
                # Parse the string into a datetime object
                dt = datetime.fromisoformat(dt_string.replace("Z", "+00:00"))
                return dt
            except ValueError:
                return dt_string  # Return the raw string if parsing fails

        formatted_start_date = format_datetime(start_date)
        formatted_end_date = format_datetime(end_date)

        # Determine the best format for display
        if isinstance(formatted_start_date, datetime) and isinstance(
            formatted_end_date, datetime
        ):
            # Convert to UK time format
            if formatted_start_date.date() == formatted_end_date.date():
                # Same day: show date once and time range
                display_time = (f"{formatted_start_date.strftime('%d-%m-%Y %H:%M')}-"
                                f"{formatted_end_date.strftime('%H:%M')}")
            else:
                # Different days: show full date and time range
                display_time = (f"{formatted_start_date.strftime('%d-%m-%Y %H:%M')}-"
                                f" {formatted_end_date.strftime('%d-%m-%Y %H:%M')}")
        else:
            # Fallback to raw strings if parsing fails
            display_time = f"{start_date} - {end_date}"

        # Append event details to the list
        events.append(
            {
                "title": title,
                "summary": summary,
                "time_range": display_time,
                "link": event_link,
            }
        )

else:
    print(f"Failed to retrieve events. Status code: {response.status_code}")


# Save or pass events to the template
def fetch_events():
    return events

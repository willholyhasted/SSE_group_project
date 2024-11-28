import requests
import xml.etree.ElementTree as ET

def fetch_events():
    # URL of the Atom feed
    url = "https://www.imperial.ac.uk/events/feed/atom/?campus=south-kensington"

    # Send a GET request to the API
    response = requests.get(url)

    # Initialize the events list
    events = []
    

    # (Fetching logic here...)

    print(events) 

    if response.status_code == 200:
        # Parse the XML response
        root = ET.fromstring(response.text)

        # Define namespaces to handle the XML correctly
        namespaces = {
            'atom': 'http://www.w3.org/2005/Atom',
            'imperialnewsevents': 'http://www3.imperial.ac.uk/imperialnewsevents/schema'
        }

        # Extract event details
        for entry in root.findall('atom:entry', namespaces):
            category = entry.find('imperialnewsevents:category', namespaces)
            category = category.text if category is not None else 'No category'
            if category != "Workshop":
                continue

            title = entry.find('atom:title', namespaces).text
            summary = entry.find('atom:summary', namespaces).text if entry.find('atom:summary', namespaces) is not None else 'No summary available'

            start_date_element = entry.find('imperialnewsevents:event_start_date', namespaces)
            if start_date_element is not None and 'startdateval' in start_date_element.attrib:
                start_date = start_date_element.attrib['startdateval']
            else:
                start_date = 'Unknown date'

            event_link = entry.find('atom:link', namespaces).attrib['href'] if entry.find('atom:link', namespaces) is not None else 'No link available'

            # Append event details to the events list
            events.append({
                'title': title,
                'summary': summary,
                'category': category,
                'start_date': start_date,
                'event_link': event_link
            })
    
    else:
        print(f"Failed to retrieve events. Status code: {response.status_code}")
    
    return events
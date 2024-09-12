import re

# Define the regex pattern for a U.S. phone number
phone_pattern = re.compile(r'''
    (?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)? # Area Code
    ([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-8][02-9])\s*(?:[.-]\s*)? # Exchange Code
    ([0-9]{4}) # Subscriber Number
''', re.VERBOSE)

# Example text containing phone numbers
text = "Contact us at +1 (555) 123-4567 or 987.654.3210 for assistance."

# Use the compiled pattern for matching
matches = phone_pattern.findall(text)

print(matches)
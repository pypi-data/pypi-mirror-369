"""Debug searching for 'ST' text."""
from natural_pdf import PDF

pdf = PDF("pdfs/m27.pdf")
page = pdf.pages[0]

# Get the original ST element
headers = (
    page
    .find("text:contains(NUMBER)")
    .right(include_source=True)
    .expand(top=3, bottom=3)
    .find_all('text')
)
original_st = headers[4]
print(f"Original 'ST' element: '{original_st.text}' at {original_st.bbox}")

# Search for 'ST' using find
found_st = page.find('text:contains("ST")')
print(f"\nFound 'ST' using find: '{found_st.text}' at {found_st.bbox}")

# Find all elements containing 'ST'
all_st = page.find_all('text:contains("ST")')
print(f"\nAll elements containing 'ST':")
for i, elem in enumerate(all_st[:10]):  # First 10
    print(f"  {i}: '{elem.text}' at x={elem.x0:.2f}, bbox={elem.bbox}")

# Check what's at position 332.88
print(f"\nLooking for element at x≈332.88:")
all_text = page.find_all('text')
for elem in all_text:
    if 332 < elem.x0 < 334:
        print(f"  Found: '{elem.text}' at x={elem.x0:.5f}, bbox={elem.bbox}")
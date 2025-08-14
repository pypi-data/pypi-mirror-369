"""Debug the extra guide issue."""
from natural_pdf import PDF
from natural_pdf.analyzers.guides import Guides

pdf = PDF("pdfs/m27.pdf")
page = pdf.pages[0]

# Get headers
headers = (
    page
    .find("text:contains(NUMBER)")
    .right(include_source=True)
    .expand(top=3, bottom=3)
    .find_all('text')
)

print("Headers 3-5:")
for i, h in enumerate(headers[3:5]):
    print(f"  {i}: '{h.text}' bbox={h.bbox}")

# Create guides with just these two headers
guides = Guides(page)
guides.vertical.from_content(headers[3:5], align='left', outer=False)

print(f"\nResulting guides: {guides.vertical}")
print(f"Expected: [328.32012, 539.63316]")

# Let's also check what happens with each header individually
print("\nTesting each header individually:")
for i, h in enumerate(headers[3:5]):
    g = Guides(page)
    g.vertical.from_content([h], align='left', outer=False)
    print(f"  Header {i} guides: {g.vertical}")

# Check if it's related to the ElementCollection
print("\nTesting with manual list of text:")
text_list = [h.text for h in headers[3:5]]
print(f"Text list: {text_list}")
guides2 = Guides(page)
guides2.vertical.from_content(text_list, align='left', outer=False)
print(f"Guides from text list: {guides2.vertical}")
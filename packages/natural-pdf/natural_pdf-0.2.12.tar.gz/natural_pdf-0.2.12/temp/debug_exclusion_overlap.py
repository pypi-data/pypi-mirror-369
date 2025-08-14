"""Debug how exclusions work with overlapping regions"""
from natural_pdf import PDF
from natural_pdf.analyzers.guides import Guides

pdf = PDF("pdfs/m27.pdf")
page = pdf.pages[0]

# Add exclusion
pdf.add_exclusion(lambda page: page.find(text="PREMISE").above(), label="header")

# Get the exclusion region
exclusions = page._get_exclusion_regions()
excl_region = exclusions[0]
print(f"Exclusion region: {excl_region.bbox}")
print(f"Exclusion bottom: {excl_region.bbox[3]}")

# Create a test cell that overlaps the exclusion
# Cell 1 from before: (32.06, 0.5, 73.18288, 79.53999999999996)
test_cell = page.region(32.06, 0.5, 73.18288, 79.53999999999996)

print(f"\nTest cell: {test_cell.bbox}")
print(f"Cell overlaps exclusion: top={test_cell.bbox[1]} < excl_bottom={excl_region.bbox[3]}")

# Extract text from different y-ranges
print("\nText in different parts of the cell:")

# Part above exclusion line (should be empty)
upper_part = page.region(32.06, 0.5, 73.18288, 59.12)
print(f"Upper part (0.5 to 59.12): '{upper_part.extract_text(apply_exclusions=True)}'")

# Part below exclusion line (should have text)  
lower_part = page.region(32.06, 59.12, 73.18288, 79.54)
print(f"Lower part (59.12 to 79.54): '{lower_part.extract_text()}'")

# The whole cell
print(f"Whole cell with exclusions: '{test_cell.extract_text(apply_exclusions=True)}'")
print(f"Whole cell without exclusions: '{test_cell.extract_text(apply_exclusions=False)}'")

# Check what text elements are in this region
print("\nText elements in cell:")
cell_texts = test_cell.find_all('text')
for t in cell_texts[:5]:
    print(f"  '{t.text}' at y={t.top:.2f}-{t.bottom:.2f}")
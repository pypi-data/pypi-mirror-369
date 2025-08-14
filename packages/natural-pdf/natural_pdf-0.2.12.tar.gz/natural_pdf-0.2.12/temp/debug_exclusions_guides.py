"""Debug why exclusions aren't working with guides.extract_table()"""
from natural_pdf import PDF
from natural_pdf.analyzers.guides import Guides

pdf = PDF("pdfs/m27.pdf")
page = pdf.pages[0]

# Check initial text
print("Initial text:")
print(page.extract_text()[:200])
print()

# Add exclusions
pdf.add_exclusion(lambda page: page.find(text="PREMISE").above())
pdf.add_exclusion(lambda page: page.find("text:regex(Page \d+ of)").expand())

# Check text after exclusions
print("Text after exclusions:")
print(page.extract_text()[:100])
print()

# Debug exclusion regions
print("Checking exclusion regions:")
exclusions = page._get_exclusion_regions(debug=True)
print(f"\nTotal exclusions: {len(exclusions)}")
for i, exc in enumerate(exclusions):
    print(f"  {i}: {exc.bbox}")
print()

# Create guides
headers = (
    page
    .find(text="NUMBER")
    .right(include_source=True)
    .expand(top=3, bottom=3)
    .find_all('text')
)

guides = Guides(page)
guides.vertical.from_content(headers, align='left')
guides.horizontal.from_stripes()

# Build grid to see what regions are created
print("\nBuilding grid...")
grid_result = guides.build_grid(include_outer_boundaries=True)
table_region = grid_result["regions"]["table"]
print(f"Table region: {table_region}")
print(f"Table bbox: {table_region.bbox if table_region else 'None'}")

# Check if table region respects exclusions
if table_region:
    print("\nExtracting text from table region directly:")
    table_text = table_region.extract_text()[:200]
    print(f"Table text: {table_text}")
    
    # Now extract table
    print("\nExtracting table with apply_exclusions=True:")
    result = guides.extract_table(include_outer_boundaries=True, apply_exclusions=True, header=False)
    df = result.to_df()
    print(df.head())
    
    # Check if excluded content is in the table
    table_str = df.to_string()
    has_feb = "FEBRUARY 2014" in table_str or "FEBR" in table_str
    has_alphabetic = "ALPHABETIC LISTING" in table_str
    print(f"\nContains 'FEBRUARY': {has_feb}")
    print(f"Contains 'ALPHABETIC LISTING': {has_alphabetic}")
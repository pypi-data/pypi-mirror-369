"""Debug cell text extraction with exclusions"""
from natural_pdf import PDF
from natural_pdf.analyzers.guides import Guides

pdf = PDF("pdfs/m27.pdf")
page = pdf.pages[0]

# Add exclusions
pdf.add_exclusion(lambda page: page.find(text="PREMISE").above(), label="header")

# Check exclusions are registered
print("Exclusions on page:")
exclusions = page._get_exclusion_regions(debug=True)

# Create guides and build grid
headers = page.find(text="NUMBER").right(include_source=True).expand(top=3, bottom=3).find_all('text')
guides = Guides(page)
guides.vertical.from_content(headers, align='left')
guides.horizontal.from_stripes()

# Build grid and get cells
grid_result = guides.build_grid(include_outer_boundaries=True)
cells = grid_result["regions"]["cells"]

print(f"\nTotal cells: {len(cells)}")

# Check first row cells (these should be in excluded area)
first_row_cells = [c for c in cells if c.bbox[1] < 90]  # y < 90
print(f"\nFirst row cells: {len(first_row_cells)}")

for i, cell in enumerate(first_row_cells[:3]):
    print(f"\nCell {i}:")
    print(f"  Bbox: {cell.bbox}")
    print(f"  Raw text: {repr(cell.extract_text(apply_exclusions=False))}")
    print(f"  With exclusions: {repr(cell.extract_text(apply_exclusions=True))}")

# Now test the full table extraction
print("\n\nFull table extraction:")
result = guides.extract_table(include_outer_boundaries=True, apply_exclusions=True, header=False)
df = result.to_df()
print("\nFirst row of dataframe:")
print(df.iloc[0].to_dict() if not df.empty else "Empty")
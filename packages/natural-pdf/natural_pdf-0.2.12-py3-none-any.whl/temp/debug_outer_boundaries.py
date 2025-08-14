"""Debug outer boundaries issue with exclusions"""
from natural_pdf import PDF
from natural_pdf.analyzers.guides import Guides

pdf = PDF("pdfs/m27.pdf")
page = pdf.pages[0]

# Add exclusions
pdf.add_exclusion(lambda page: page.find(text="PREMISE").above())

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

print("Horizontal guides (sorted):")
for i, h in enumerate(sorted(guides.horizontal)):
    print(f"  {i}: {h:.2f}")

print(f"\nFirst content guide: {sorted(guides.horizontal)[0]:.2f}")
print(f"Page height: {page.height}")

# Test without outer boundaries
print("\n\nWithout outer boundaries:")
result1 = guides.extract_table(include_outer_boundaries=False, apply_exclusions=True, header=False)
df1 = result1.to_df()
print(f"Shape: {df1.shape}")
print("First row, first column:", df1.iloc[0, 0] if not df1.empty else "Empty")

# Test with outer boundaries
print("\n\nWith outer boundaries:")
result2 = guides.extract_table(include_outer_boundaries=True, apply_exclusions=True, header=False)
df2 = result2.to_df()
print(f"Shape: {df2.shape}")
print("First row, first column:", df2.iloc[0, 0] if not df2.empty else "Empty")

# The issue: include_outer_boundaries adds guides at 0 and 612,
# which creates cells that span into the exclusion zone
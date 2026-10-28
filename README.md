# Where Should the Next Store Open?

Prototype that compares 8 shortlisted Bengaluru neighbourhoods for a (fictional) supermarket chain, NammaBasket, and recommends where to open next within a capex budget, with reasons and trade-offs.

**Live app:** REPLACE-WITH-YOUR-GITHUB-PAGES-URL (e.g. https://your-username.github.io/nammabasket-store-location/)

## Recommendation (base case)
Open **Kanakapura Road** and **Whitefield**: Rs 7.26 Cr of the Rs 8 Cr budget, combined 9-year NPV Rs 8.65 Cr. Sarjapur Road is the reserve. Marathahalli has the highest footfall but negative value (mostly commuter footfall, high rent, 7 competitors).

## How it works
1. **Inputs**: population, household income, footfall (resident vs commuter), competitors, rent, accessibility, growth, coordinates; 6 existing stores with actual sales.
2. **Demand**: household-wallet method and footfall method, blended and calibrated on existing stores (factor 1.275, mean error ~5%).
3. **Cannibalisation**: share of sales taken from the nearest existing store (35% next door, 0% at 8 km).
4. **Unit economics**: store P&L, capex, 9-year NPV, payback.
5. **Financial gate**: payback <= 4 years and NPV > 0.
6. **Weighted score**: 7 criteria scaled 0-100, adjustable weights.
7. **Pick**: within budget, keeping new stores at least 5 km apart.

## Repository contents
| Path | What |
|---|---|
| `index.html` | Interactive web app (self-contained, open in any browser) |
| `model/NammaBasket_Location_Model.xlsx` | Excel model, 780 live formulas |
| `model/model.py` | Python reference implementation |
| `data/` | Candidate locations, existing stores, model results (CSV) |
| `docs/Project_Summary.docx` | 2-page summary for examiners |
| `docs/Store_Location_Prototype_Guide.docx` | Build guide, assumptions, results, pitch script |

## Data and assumptions
Locality data is **synthetic**, calibrated to public benchmarks: MoSPI HCES 2023-24 (urban MPCE Rs 6,996; food ~40% of spend), Census 2011 (Bengaluru), 2025 Bengaluru retail rent ranges, listed grocery chain sales per sq ft. Full list in the Excel `Assumptions` sheet and the guide.

## Key limitation
Synthetic locality data and calibration on only 6 stores: treat rankings as more reliable than rupee values, and validate footfall and rent on site before signing a lease.

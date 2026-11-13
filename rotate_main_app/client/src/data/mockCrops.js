// Demonstration crop profiles used when the optional API is unavailable.
// These values are illustrative placeholders, not validated agronomic data.

export const crops = [
  { id: "boro-rice", name: "Boro Rice", localName: "বোরো ধান", role: "Cereal", season: "Rabi (Dec–May)", waterNeed: 90, salinityTolerance: 30, soilBenefit: 40, summary: "Irrigated dry-season rice; high yields but heavy on water." },
  { id: "aman-rice", name: "Aman Rice", localName: "আমন ধান", role: "Cereal", season: "Kharif-II (Jul–Dec)", waterNeed: 70, salinityTolerance: 40, soilBenefit: 40, summary: "Monsoon-fed rice grown across most of the delta." },
  { id: "aus-rice", name: "Aus Rice", localName: "আউশ ধান", role: "Cereal", season: "Kharif-I (Mar–Aug)", waterNeed: 55, salinityTolerance: 45, soilBenefit: 40, summary: "Shorter-duration rice suited to pre-monsoon rainfall." },
  { id: "saline-rice", name: "Saline-tolerant Rice", localName: "লবণসহিষ্ণু ধান", role: "Cereal", season: "Kharif-II (Jul–Dec)", waterNeed: 65, salinityTolerance: 85, soilBenefit: 40, summary: "Rice varieties bred to cope with coastal salinity." },
  { id: "wheat", name: "Wheat", localName: "গম", role: "Cereal", season: "Rabi (Nov–Mar)", waterNeed: 45, salinityTolerance: 40, soilBenefit: 35, summary: "Cool-season cereal needing moderate irrigation." },
  { id: "jute", name: "Jute", localName: "পাট", role: "Fiber", season: "Kharif-I (Mar–Aug)", waterNeed: 75, salinityTolerance: 25, soilBenefit: 55, summary: "Fiber crop that adds organic matter through leaf fall." },
  { id: "lentil", name: "Lentil (Masoor)", localName: "মসুর", role: "Legume", season: "Rabi (Nov–Mar)", waterNeed: 30, salinityTolerance: 35, soilBenefit: 80, summary: "Nitrogen-fixing pulse with low water demand." },
  { id: "mungbean", name: "Mungbean (Green Gram)", localName: "মুগ", role: "Legume", season: "Pre-Kharif (Feb–Jun)", waterNeed: 30, salinityTolerance: 45, soilBenefit: 85, summary: "Short-duration legume that rebuilds soil nitrogen." },
  { id: "mustard", name: "Mustard", localName: "সরিষা", role: "Oilseed", season: "Rabi (Nov–Feb)", waterNeed: 35, salinityTolerance: 60, soilBenefit: 50, summary: "Winter oilseed with moderate salinity tolerance." },
  { id: "sunflower", name: "Sunflower", localName: "সূর্যমুখী", role: "Oilseed", season: "Rabi (Dec–Apr)", waterNeed: 45, salinityTolerance: 70, soilBenefit: 55, summary: "Oilseed that performs better than many crops in saline soils." },
  { id: "sesame", name: "Sesame", localName: "তিল", role: "Oilseed", season: "Kharif-I (Mar–Jul)", waterNeed: 30, salinityTolerance: 55, soilBenefit: 55, summary: "Drought-tolerant oilseed for shorter, drier seasons." },
];

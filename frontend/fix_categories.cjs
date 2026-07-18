const fs = require('fs');

const data = JSON.parse(fs.readFileSync('./public/dummy.json', 'utf8'));

// Add the missing categories to the global schema
const hasEducation = data.categories.some(c => c.id === 'education');
if (!hasEducation) {
  data.categories.push({
    "id": "education",
    "title": "Education",
    "description": "Bootcamps, universities, and learning resources"
  });
}

const hasBusiness = data.categories.some(c => c.id === 'business');
if (!hasBusiness) {
  data.categories.push({
    "id": "business",
    "title": "Business",
    "description": "Startups, venture capital, and market trends"
  });
}

fs.writeFileSync('./public/dummy.json', JSON.stringify(data, null, 2));
console.log("Added missing categories to dummy.json.");

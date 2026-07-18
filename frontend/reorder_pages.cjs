const fs = require('fs');

const data = JSON.parse(fs.readFileSync('./public/dummy.json', 'utf8'));

// Extract existing pages
const pFront = data.pages.find(p => p.title.includes("Front Page"));
const pObits = data.pages.find(p => p.title.includes("Obituaries"));
const pSports = data.pages.find(p => p.title.includes("Sports"));
const pClassifieds = data.pages.find(p => p.title.includes("Classifieds"));
const pWeather = data.pages.find(p => p.title.includes("Weather"));

// Rename Sports to just Sports
if (pSports) {
  pSports.title = "Sports";
  pSports.deck = "Play-by-play coverage of the fierce competition between tech giants and framework champions.";
}

// Create Education page
const pEducation = {
  "page": 2,
  "template": "three-column",
  "title": "Education",
  "deck": "Bootcamps, CS Degrees, and the continuous learning grind.",
  "articles": [
    {
      "id": "edu-cs50-rust",
      "page": 2,
      "category": "education",
      "importance": 4,
      "title": "Harvard CS50 announces controversial pivot to Rust",
      "subtitle": "The beloved introductory computer science course drops Python, citing memory safety as a fundamental right.",
      "kicker": "Curriculum",
      "authors": [{ "name": "Nora Patel", "role": "editorial" }],
      "sourceIds": [],
      "sources": [],
      "images": [],
      "content": [
        "In a shocking syllabus update, Harvard's legendary CS50 course announced it will transition its primary teaching language from Python to Rust. The teaching staff argued that if students can learn pointers in C, they can learn the borrow checker.",
        "Students are reportedly forming support groups to deal with compiler errors, but the teaching fellows insist the strict typing will build character."
      ],
      "tags": ["education", "rust", "university"],
      "publishedAt": "2026-07-16T09:00:00+05:30",
      "readTimeMin": 4
    },
    {
      "id": "edu-bootcamp-fall",
      "page": 2,
      "category": "education",
      "importance": 4,
      "title": "The 12-week bootcamp model faces an existential crisis",
      "subtitle": "As entry-level roles demand more system design experience, six-month apprenticeships are taking over.",
      "kicker": "Industry",
      "authors": [{ "name": "Ava Mehta", "role": "reporter" }],
      "sourceIds": [],
      "sources": [],
      "images": [],
      "content": [
        "The era of learning React in three months and immediately landing a six-figure salary has officially ended. Coding bootcamps are rapidly restructuring into longer, apprenticeship-style programs.",
        "Hiring managers are demanding proof of debugging complex distributed systems, leading schools to replace basic frontend curriculum with intensive backend architecture modules."
      ],
      "tags": ["bootcamp", "hiring", "career"],
      "publishedAt": "2026-07-16T10:15:00+05:30",
      "readTimeMin": 5
    },
    {
      "id": "edu-docs-teachers",
      "page": 2,
      "category": "education",
      "importance": 3,
      "title": "API references are the new textbooks",
      "subtitle": "Interactive docs are replacing formal course materials in the modern classroom.",
      "kicker": "Pedagogy",
      "authors": [{ "name": "Rohan Iyer", "role": "reporter" }],
      "sourceIds": [],
      "sources": [],
      "images": [],
      "content": [
        "University professors are increasingly ditching expensive textbooks in favor of simply assigning students to read Stripe and Vercel documentation.",
        "The modern API reference, complete with interactive sandboxes and executable curl commands, has proven far more effective at teaching REST principles than any printed textbook from 2018."
      ],
      "tags": ["documentation", "learning"],
      "publishedAt": "2026-07-16T11:00:00+05:30",
      "readTimeMin": 3
    }
  ]
};

// Create Economics page
const pEconomics = {
  "page": 3,
  "template": "longform",
  "title": "Economics",
  "deck": "SaaS pricing, venture capital, and the macro trends affecting the tech industry.",
  "articles": [
    {
      "id": "econ-saas-tiers",
      "page": 3,
      "category": "business",
      "importance": 5,
      "title": "The ZIRP-era of free SaaS tiers is officially over",
      "subtitle": "Companies are quietly removing 'Forever Free' from their pricing pages as interest rates stabilize.",
      "kicker": "Markets",
      "authors": [{ "name": "Dispatch Editorial Desk", "role": "editorial" }],
      "sourceIds": [],
      "sources": [],
      "images": [{
        "src": "/images/dispatch-1.svg",
        "alt": "Chart showing decline of free tiers",
        "caption": "The freemium funnel is getting much narrower.",
        "credit": "Dispatch"
      }],
      "content": [
        "The zero-interest rate phenomenon (ZIRP) funded a decade of incredibly generous free tiers. Startups offered unlimited bandwidth, gigabytes of storage, and endless compute just to acquire users.",
        "That era is dead. Over the last quarter, 40% of the top developer tools have quietly introduced hard caps on their hobby tiers, nudging users toward $10/month pro plans.",
        "Economists note that this return to fundamental unit economics is healthy for the industry, even if developers are mourning the loss of their massive free server fleets."
      ],
      "tags": ["pricing", "saas", "economics"],
      "publishedAt": "2026-07-16T12:00:00+05:30",
      "readTimeMin": 6
    },
    {
      "id": "econ-api-pricing",
      "page": 3,
      "category": "business",
      "importance": 4,
      "title": "The great API token price war continues",
      "subtitle": "Another 50% price cut sends shockwaves through the inference market.",
      "kicker": "Commodities",
      "authors": [{ "name": "Nora Patel", "role": "reporter" }],
      "sourceIds": [],
      "sources": [],
      "images": [],
      "content": [
        "Intelligence is becoming cheaper than electricity. As inference providers optimize their GPU utilization, the cost per million tokens has plummeted yet again.",
        "Startups building wrappers around these APIs are struggling to capture value as the underlying commodity becomes practically free."
      ],
      "tags": ["api", "pricing", "ai"],
      "publishedAt": "2026-07-16T13:30:00+05:30",
      "readTimeMin": 4
    }
  ]
};

// Reorder pages!
// Front Page -> Education -> Economics -> Classifieds -> Weather -> Obituaries -> Sports
const newPages = [
  pFront,
  pEducation,
  pEconomics,
  pClassifieds,
  pWeather,
  pObits,
  pSports
].filter(Boolean); // just in case one is missing

// Reassign page numbers
newPages.forEach((page, index) => {
  const newPageNum = index + 1;
  page.page = newPageNum;
  page.articles.forEach(article => {
    article.page = newPageNum;
  });
});

data.pages = newPages;

fs.writeFileSync('./public/dummy.json', JSON.stringify(data, null, 2));
console.log("Pages reordered and new pages added successfully.");

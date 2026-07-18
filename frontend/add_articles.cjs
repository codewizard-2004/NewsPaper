const fs = require('fs');

const data = JSON.parse(fs.readFileSync('./public/dummy.json', 'utf8'));

const pEducation = data.pages.find(p => p.title === "Education");
const pEconomics = data.pages.find(p => p.title === "Economics");

if (pEducation) {
  pEducation.articles.push(
    {
      "id": "edu-haskell-comeback",
      "page": 2,
      "category": "education",
      "importance": 3,
      "title": "Haskell makes a surprise comeback in sophomore curriculum",
      "subtitle": "Students are finding solace in pure functions after a semester of unpredictable state mutations.",
      "kicker": "Curriculum Trends",
      "authors": [{ "name": "Ava Mehta", "role": "reporter" }],
      "sourceIds": [],
      "sources": [],
      "images": [],
      "content": [
        "In a surprising reversal of industry trends, several top-tier universities are reintroducing Haskell as a mandatory requirement for second-year computer science students.",
        "After years of wrestling with side effects and null pointer exceptions in object-oriented paradigms, students are reportedly embracing the strict, mathematical purity of functional programming.",
        "One student noted, 'If it compiles, it works. That is a kind of peace I have never felt in Javascript.'"
      ],
      "tags": ["education", "haskell", "functional-programming"],
      "publishedAt": "2026-07-17T09:15:00+05:30",
      "readTimeMin": 3
    },
    {
      "id": "edu-ai-plagiarism",
      "page": 2,
      "category": "education",
      "importance": 2,
      "title": "The 'AI Plagiarism' debate shifts from essays to code reviews",
      "subtitle": "Teaching Assistants admit they can't tell the difference between Copilot and a bright freshman.",
      "kicker": "Campus Life",
      "authors": [{ "name": "Dispatch Editorial Desk", "role": "editorial" }],
      "sourceIds": [],
      "sources": [],
      "images": [],
      "content": [
        "The academic integrity offices that spent last year worrying about generated English essays are now pivoting to a much harder problem: generated Python scripts.",
        "Computer science departments are abandoning legacy code-similarity checkers. Instead, professors are shifting toward entirely oral examinations, forcing students to verbally explain the Big-O time complexity of the algorithms they submitted."
      ],
      "tags": ["ai", "plagiarism", "education"],
      "publishedAt": "2026-07-17T10:30:00+05:30",
      "readTimeMin": 2
    }
  );
}

if (pEconomics) {
  pEconomics.articles.push(
    {
      "id": "econ-agent-bubble",
      "page": 3,
      "category": "business",
      "importance": 4,
      "title": "Investors pour billions into 'Agentic' startups lacking a moat",
      "subtitle": "The term 'Agent' is doing incredibly heavy lifting in Series A pitch decks this quarter.",
      "kicker": "Venture Capital",
      "authors": [{ "name": "Nora Patel", "role": "reporter" }],
      "sourceIds": [],
      "sources": [],
      "images": [],
      "content": [
        "Sand Hill Road is currently experiencing a gold rush funded almost entirely by semantic ambiguity. Venture capitalists are actively deploying billions of dollars into seed-stage startups whose entire product architecture consists of a thin system prompt wrapped around an upstream language model API.",
        "Founders are quickly learning that prepending the word 'Autonomous' to a standard Python script can increase a company's valuation by a factor of ten.",
        "Market analysts warn that once the foundation model providers vertically integrate these basic agentic loops into their base offerings, this entire cohort of heavily funded startups will face an existential threat."
      ],
      "tags": ["vc", "startups", "ai", "economics"],
      "publishedAt": "2026-07-17T11:45:00+05:30",
      "readTimeMin": 5
    },
    {
      "id": "econ-open-source-labor",
      "page": 3,
      "category": "business",
      "importance": 3,
      "title": "The open-source subsidy model is cracking under commercial pressure",
      "subtitle": "Maintainers of critical infrastructure packages are increasingly putting their work behind commercial licenses.",
      "kicker": "Labor Economics",
      "authors": [{ "name": "Rohan Iyer", "role": "reporter" }],
      "sourceIds": [],
      "sources": [],
      "images": [],
      "content": [
        "For two decades, the modern internet has been heavily subsidized by the unpaid weekend labor of open-source maintainers. That social contract is currently unraveling.",
        "Following a string of high-profile burnout cases and supply-chain attacks, the developers maintaining the foundational libraries used by Fortune 500 companies are demanding equitable compensation. Many are transitioning their projects from permissive MIT licenses to dual-license models that force enterprise users to pay for usage.",
        "The shift represents a fundamental restructuring of how digital public goods are funded, moving the ecosystem away from corporate charity and toward sustainable, contractual business relationships."
      ],
      "tags": ["open-source", "economics", "licensing"],
      "publishedAt": "2026-07-17T14:15:00+05:30",
      "readTimeMin": 4
    },
    {
      "id": "econ-cloud-repatriation",
      "page": 3,
      "category": "business",
      "importance": 3,
      "title": "The hidden macroeconomic costs of cloud repatriation",
      "subtitle": "Leaving managed cloud services for bare metal saves millions in compute, until you have to hire a platform team.",
      "kicker": "Infrastructure",
      "authors": [{ "name": "Ava Mehta", "role": "reporter" }],
      "sourceIds": [],
      "sources": [],
      "images": [],
      "content": [
        "The great 'Cloud Exit' trend is facing its first major reality check. Mid-sized enterprises that successfully migrated their workloads from managed AWS services to rented bare-metal server racks are indeed seeing an 80% reduction in their monthly compute bills.",
        "However, those savings are being rapidly consumed by payroll. Operating bare metal requires a specialized in-house platform engineering team capable of managing hardware failures, network peering, and distributed storage arrays—skills that command a massive premium in the current labor market.",
        "Chief Financial Officers are learning the hard way that you are always paying someone for reliability; you are just choosing whether to pay a cloud provider's margin or a senior engineer's base salary."
      ],
      "tags": ["cloud", "infrastructure", "economics"],
      "publishedAt": "2026-07-17T16:00:00+05:30",
      "readTimeMin": 4
    }
  );
}

fs.writeFileSync('./public/dummy.json', JSON.stringify(data, null, 2));
console.log("Added new dummy articles successfully.");

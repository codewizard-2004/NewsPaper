const fs = require('fs');

const data = JSON.parse(fs.readFileSync('./public/dummy.json', 'utf8'));

// 1. Add job postings to Education
const pEducation = data.pages.find(p => p.title === "Education");
if (pEducation) {
  pEducation.articles.push(
    {
      "id": "edu-job-prompt-eng",
      "category": "education",
      "importance": 2,
      "title": "HIRING: Adjunct Professor of Prompt Engineering",
      "subtitle": "Must have 10 years of experience in a 2-year-old field. Tenure track not available.",
      "kicker": "Job Board",
      "authors": [{ "name": "University Admin", "role": "classifieds" }],
      "sourceIds": [],
      "sources": [],
      "images": [],
      "content": [
        "State University is urgently seeking an adjunct professor to teach 'Intro to LLM Whispering 101'.",
        "The ideal candidate will have a deep understanding of negative prompting, few-shot chain-of-thought, and the patience to grade 300 AI-generated final projects."
      ],
      "tags": ["hiring", "education", "jobs"],
      "publishedAt": "2026-07-18T09:00:00+05:30",
      "readTimeMin": 1
    },
    {
      "id": "edu-job-systems",
      "category": "education",
      "importance": 1,
      "title": "HIRING: Teaching Assistant for Distributed Systems",
      "subtitle": "Required: Master's Degree. Compensation: Minimum wage and free pizza.",
      "kicker": "Job Board",
      "authors": [{ "name": "University Admin", "role": "classifieds" }],
      "sourceIds": [],
      "sources": [],
      "images": [],
      "content": [
        "The Computer Science department is looking for someone to help students debug their Raft consensus implementations.",
        "Warning: 90% of your time will be spent explaining why their network partitions are failing the autograder."
      ],
      "tags": ["hiring", "education", "jobs"],
      "publishedAt": "2026-07-18T09:15:00+05:30",
      "readTimeMin": 1
    }
  );
}

// 2. Create AI Page
const pAI = {
  "template": "split",
  "title": "AI & Machine Learning",
  "deck": "Frontier models, inference economics, and the quest for artificial general intelligence.",
  "articles": [
    {
      "id": "ai-model-collapse",
      "category": "ai_ml",
      "importance": 5,
      "title": "Model Collapse becomes a reality as AI trains on AI",
      "subtitle": "The internet is running out of human-generated text, forcing frontier models into an inescapable feedback loop.",
      "kicker": "Research",
      "authors": [{ "name": "Nora Patel", "role": "reporter" }],
      "sourceIds": [],
      "sources": [],
      "images": [{
        "src": "/images/dispatch-2.svg",
        "alt": "AI feedback loop",
        "caption": "The recursive training loop degrades output quality over generations.",
        "credit": "Dispatch"
      }],
      "content": [
        "Researchers at top labs have confirmed their worst fears: the latest generation of language models is actively deteriorating due to 'model collapse.'",
        "Because the internet is now predominantly filled with AI-generated SEO spam, newer models are ingesting synthetic data during their pre-training phase. This recursive loop acts like a digital photocopy of a photocopy, gradually smoothing out the nuances of human language.",
        "In response, data brokers are now selling 'certified pre-2022 artisanal human text' at massive premiums, treating it like digital gold."
      ],
      "tags": ["ai", "research", "data"],
      "publishedAt": "2026-07-18T10:00:00+05:30",
      "readTimeMin": 5
    },
    {
      "id": "ai-local-inference",
      "category": "ai_ml",
      "importance": 4,
      "title": "The Macbook Pro is the new GPU cluster",
      "subtitle": "Apple Silicon’s unified memory architecture makes local inference the default for developers.",
      "kicker": "Hardware",
      "authors": [{ "name": "Rohan Iyer", "role": "reporter" }],
      "sourceIds": [],
      "sources": [],
      "images": [],
      "content": [
        "Cloud inference providers are seeing a sharp decline in developer usage as engineering teams realize they can run highly quantized 70B models directly on their M4 Max laptops.",
        "The ability to iterate on complex local workflows without incurring massive API bills or compromising user data privacy has triggered a renaissance in on-device AI tooling."
      ],
      "tags": ["ai", "hardware", "mac"],
      "publishedAt": "2026-07-18T11:00:00+05:30",
      "readTimeMin": 4
    },
    {
      "id": "ai-context-windows",
      "category": "ai_ml",
      "importance": 3,
      "title": "Context windows reach 10 million tokens",
      "subtitle": "You can now paste your entire codebase, your Slack history, and 'War and Peace'.",
      "kicker": "Engineering",
      "authors": [{ "name": "Ava Mehta", "role": "reporter" }],
      "sourceIds": [],
      "sources": [],
      "images": [],
      "content": [
        "Model providers have officially solved the context length problem, pushing limits to 10 million tokens.",
        "However, developers are quickly discovering the 'needle in a haystack' problem: just because the model can ingest an entire codebase doesn't mean it won't hallucinate the implementation details."
      ],
      "tags": ["ai", "context", "llm"],
      "publishedAt": "2026-07-18T11:30:00+05:30",
      "readTimeMin": 3
    }
  ]
};

// 3. Create Security Page
const pSecurity = {
  "template": "longform",
  "title": "Security & Privacy",
  "deck": "Zero-days, identity architecture, and the never-ending battle against supply-chain attacks.",
  "articles": [
    {
      "id": "sec-supply-chain",
      "category": "security",
      "importance": 5,
      "title": "Another NPM package compromised, millions of CI pipelines halt",
      "subtitle": "A rogue maintainer injected a cryptominer into a library that pads strings, reminding us the supply chain is terrifyingly fragile.",
      "kicker": "Incident",
      "authors": [{ "name": "Dispatch Editorial Desk", "role": "editorial" }],
      "sourceIds": [],
      "sources": [],
      "images": [{
        "src": "/images/dispatch-4.svg",
        "alt": "Supply chain pipeline",
        "caption": "A single compromised dependency can break thousands of builds.",
        "credit": "Dispatch"
      }],
      "content": [
        "At 3:00 AM UTC, the maintainer of 'left-pad-ultra'—a package downloaded 40 million times a week—pushed a minor version bump that included an obfuscated Monero miner.",
        "Within minutes, automated Dependabot PRs propagated the malicious code into the CI/CD pipelines of Fortune 500 companies.",
        "The incident has sparked renewed calls for rigorous Software Bill of Materials (SBOM) enforcement and the outright banning of transitive dependencies in sensitive enterprise environments."
      ],
      "tags": ["security", "npm", "supply-chain"],
      "publishedAt": "2026-07-18T12:00:00+05:30",
      "readTimeMin": 6
    },
    {
      "id": "sec-passkeys",
      "category": "security",
      "importance": 4,
      "title": "Passwords are officially dead. Long live the Passkey.",
      "subtitle": "Major banks and consumer apps have aggressively mandated WebAuthn, ending the era of 'Password123!'.",
      "kicker": "Identity",
      "authors": [{ "name": "Nora Patel", "role": "reporter" }],
      "sourceIds": [],
      "sources": [],
      "images": [],
      "content": [
        "In a coordinated push by Apple, Google, and Microsoft, the traditional password is being phased out of consumer interfaces. Passkeys, built on public key cryptography, are now the default.",
        "Phishing attacks have plummeted by 80% on platforms that enforce passkey logins, proving that moving security to the hardware level is the only viable path forward."
      ],
      "tags": ["security", "passkeys", "identity"],
      "publishedAt": "2026-07-18T13:00:00+05:30",
      "readTimeMin": 4
    },
    {
      "id": "sec-quantum",
      "category": "security",
      "importance": 3,
      "title": "NIST finalizes post-quantum cryptographic standards",
      "subtitle": "The countdown to 'Q-Day' begins as enterprises scramble to upgrade their TLS certificates.",
      "kicker": "Cryptography",
      "authors": [{ "name": "Rohan Iyer", "role": "reporter" }],
      "sourceIds": [],
      "sources": [],
      "images": [],
      "content": [
        "The National Institute of Standards and Technology has officially standardized the algorithms designed to withstand attacks from future quantum computers.",
        "Chief Information Security Officers are now facing the daunting task of auditing decades of legacy infrastructure to rip and replace RSA and Elliptic Curve cryptography before a cryptographically relevant quantum computer comes online."
      ],
      "tags": ["security", "crypto", "quantum"],
      "publishedAt": "2026-07-18T14:30:00+05:30",
      "readTimeMin": 5
    },
    {
      "id": "sec-zero-trust",
      "category": "security",
      "importance": 2,
      "title": "VPNs replaced by Zero-Trust overlays",
      "subtitle": "The corporate perimeter is gone, replaced by continuous identity verification.",
      "kicker": "Architecture",
      "authors": [{ "name": "Ava Mehta", "role": "reporter" }],
      "sourceIds": [],
      "sources": [],
      "images": [],
      "content": [
        "Traditional VPNs are being rapidly decommissioned. IT departments are instead deploying Zero-Trust Network Access (ZTNA) overlays that authenticate every single internal request.",
        "Employees can no longer trust being 'on the network'; their device posture and identity are re-evaluated continuously."
      ],
      "tags": ["security", "zero-trust", "vpn"],
      "publishedAt": "2026-07-18T15:00:00+05:30",
      "readTimeMin": 3
    }
  ]
};

// Collect existing pages, remove them from data, and weave them into a new order
const existingPages = data.pages;

// Let's create the final sequence:
// 1. Front Page
// 2. Education (Now with Jobs)
// 3. AI & Machine Learning (NEW)
// 4. Security & Privacy (NEW)
// 5. Economics
// 6. Classifieds
// 7. Weather & Puzzles
// 8. Obituaries
// 9. Sports

const orderedPages = [
  existingPages.find(p => p.title.includes("Front Page")),
  existingPages.find(p => p.title.includes("Education")),
  pAI,
  pSecurity,
  existingPages.find(p => p.title.includes("Economics")),
  existingPages.find(p => p.title.includes("Classifieds")),
  existingPages.find(p => p.title.includes("Weather")),
  existingPages.find(p => p.title.includes("Obituaries")),
  existingPages.find(p => p.title.includes("Sports"))
].filter(Boolean); // Safety filter

// Reassign pages sequentially
orderedPages.forEach((page, index) => {
  const pageNumber = index + 1;
  page.page = pageNumber;
  
  if (!page.articles) page.articles = [];
  page.articles.forEach(article => {
    article.page = pageNumber;
  });
});

data.pages = orderedPages;

fs.writeFileSync('./public/dummy.json', JSON.stringify(data, null, 2));
console.log("Added AI and Security pages, plus Education jobs.");

const fs = require('fs');

const data = JSON.parse(fs.readFileSync('./public/dummy.json', 'utf8'));

// Page 2 -> Obituaries & Births
const page2 = data.pages.find(p => p.page === 2);
if (page2) {
  page2.title = "Obituaries & Births";
  page2.deck = "Mourning deprecated frameworks and celebrating the birth of new standards in the ecosystem.";
  
  // prompt caching -> Birth
  const p1 = page2.articles.find(a => a.id === "systems-prompt-caching");
  if (p1) {
    p1.title = "Birth Announcement: Native Prompt Caching Framework";
    p1.subtitle = "The standard library welcomes a healthy, 2MB-optimized context reuse module.";
    p1.kicker = "Births";
    p1.content[0] = "The developer community rejoiced yesterday as Native Prompt Caching was officially delivered into the core architectural stack. Weighing in at a highly optimized 2MB and boasting sub-millisecond response times, the new framework is already making friends across the ecosystem.";
    p1.content[1] = "Proud parents at the major AI labs report that the caching layer is sleeping soundly through the night, successfully bypassing the pre-fill phase for thousands of concurrent sessions without waking the PagerDuty on-call rotation.";
  }

  // local review -> Birth
  const p2 = page2.articles.find(a => a.id === "systems-local-review");
  if (p2) {
    p2.title = "Birth Announcement: Local-First SQLite Code Reviewer";
    p2.subtitle = "A speedy bundle of joy arrives to save engineers from network latency.";
    p2.kicker = "Births";
    p2.content[0] = "We are thrilled to announce the arrival of Local-First Review, a beautiful new tool that keeps git objects and symbol graphs right where they belong: on the developer's workstation.";
    p2.content[1] = "Unlike its cloud-based siblings, this new arrival requires no internet connection to thrive, happily rendering complex architectural refactors at 30,000 feet.";
  }

  // rust linux -> Birth
  const p3 = page2.articles.find(a => a.id === "systems-rust-linux-kernel");
  if (p3) {
    p3.title = "Milestone: Rust officially takes its first steps in Linux Kernel";
    p3.subtitle = "The memory-safe prodigy moves out of experimental and into core networking paths.";
    p3.kicker = "Milestones";
  }

  // incident shrinking -> Obituary
  const p4 = page2.articles.find(a => a.id === "systems-incident"); // Wait, id is systems-incident or something else? I'll just use index.
  page2.articles.forEach(a => {
    if (a.title.includes("Incident teams")) {
      a.title = "Obituary: The 50-Page Incident Postmortem Deck (2014-2026)";
      a.subtitle = "Survived by crisp timelines and actionable remediation tracking.";
      a.kicker = "Obituaries";
      a.content[0] = "The 50-Page Incident Postmortem Deck passed away peacefully this week, surrounded by exhausted SREs. It was known for padded keynotes, endless root cause analysis diagrams, and taking up entirely too much space on Google Drive.";
      a.content[1] = "In lieu of flowers, operations teams ask that you please just write a one-page summary of what broke and how you plan to fix it.";
    }
    if (a.title.includes("SQLite replication")) {
      a.title = "Obituary: The Sprawling Multi-Region Consensus Cluster";
      a.subtitle = "Complex, expensive, and ultimately outlived by single-file edge databases.";
      a.kicker = "Obituaries";
      a.content[0] = "The Sprawling Multi-Region Consensus Cluster, 12, passed away Tuesday due to complications from network partitions and excessive AWS billing.";
      a.content[1] = "It is survived by a much simpler, cheaper, and faster SQLite edge replication architecture.";
    }
    if (a.title.includes("Browser extension")) {
      a.title = "Obituary: Unrestricted DOM Access for Extensions";
      a.subtitle = "Quietly collecting data since 2008, finally laid to rest by platform policies.";
      a.kicker = "Obituaries";
      a.content[0] = "Unrestricted DOM Access, a long-time resident of the browser ecosystem, was forcibly retired yesterday following a prolonged battle with security auditors and platform policy enforcers.";
    }
  });
}

// Page 3 -> Sports & Markets
const page3 = data.pages.find(p => p.page === 3);
if (page3) {
  page3.title = "Sports & Markets";
  page3.deck = "Play-by-play coverage of the fierce competition between tech giants and startup challengers.";
  
  page3.articles.forEach(a => {
    if (a.title.includes("A startup is selling reliability")) {
      a.title = "Team Vercel pushes past Netlify in the Edge Compute Finals";
      a.subtitle = "A stunning fourth-quarter rally in caching metrics secures the championship.";
      a.kicker = "Sports";
      a.content[0] = "In a breathtaking display of engineering athleticism, Team Vercel dominated the edge compute finals yesterday, out-caching their longtime rivals at Netlify with a sub-20ms TTFB average.";
    }
    if (a.title.includes("React 19")) {
      a.title = "Heavyweight Bout: React 19 vs Vue in the Server Component Arena";
      a.subtitle = "Both frameworks came out swinging, but only one can take home the belt.";
      a.kicker = "Sports";
      a.content[0] = "The stadium was packed as React 19 debuted its new primitives, landing several heavy blows in the first round. Vue's corner remains confident, relying on their famously nimble reactivity system to dodge the heavyweight's complex compiler requirements.";
    }
    if (a.title.includes("WebAssembly")) {
      a.title = "WASM takes Gold in the Database Extension Decathlon";
      a.subtitle = "Shattering previous records for cross-language query execution.";
      a.kicker = "Sports";
    }
    if (a.title.includes("Tailwind v4")) {
      a.title = "Tailwind Engine Revs Up, Shatters Build-Time Course Records";
      a.subtitle = "The CSS utility racing team drops milliseconds off their qualifying laps.";
      a.kicker = "Sports";
    }
  });
}

// Page 4 -> Classifieds
const page4 = data.pages.find(p => p.page === 4);
if (page4) {
  page4.title = "Classifieds";
  page4.deck = "Looking for co-founders, trading legacy servers, and selling premium domain names.";
  
  page4.articles.forEach(a => {
    if (a.title.includes("Security mandates")) {
      a.title = "FOR SALE: Barely Used K8s Cluster. Must Go!";
      a.subtitle = "Moving to serverless. Willing to trade for a reliable SQLite setup.";
      a.kicker = "Classifieds";
      a.content[0] = "Excellent condition Kubernetes cluster. Only crashed twice. Comes with 43 YAML configuration files and a headache. Serious inquiries only.";
    }
    if (a.title.includes("Policy teams")) {
      a.title = "SEEKING: 10x Rust Developer for 'The Next Google'";
      a.subtitle = "Must have 15 years experience in a language that is 10 years old. Equity only.";
      a.kicker = "Classifieds";
    }
    if (a.title.includes("Privacy settings")) {
      a.title = "LOST: One API Key. Answers to 'sk_live_...'";
      a.subtitle = "Last seen accidentally committed to a public GitHub repository. Please return, AWS bill is getting high.";
      a.kicker = "Classifieds";
    }
    if (a.title.includes("OAuth")) {
      a.title = "WANTED: Someone to explain OAuth to me";
      a.subtitle = "I have read the RFC three times and I am still confused. Will pay in pizza.";
      a.kicker = "Classifieds";
    }
  });
}

// Page 5 -> Weather & Comics
const page5 = data.pages.find(p => p.page === 5);
if (page5) {
  page5.title = "Weather & Puzzles";
  page5.deck = "Cloud forecasts, outage reports, and the daily LeetCode crossword.";
  
  page5.articles.forEach(a => {
    if (a.title.includes("Model teams")) {
      a.title = "Cloud Forecast: Heavy AWS Outages expected in US-East-1";
      a.subtitle = "Grab an umbrella and a multi-region failover strategy.";
      a.kicker = "Weather";
    }
    if (a.title.includes("PostgreSQL")) {
      a.title = "Today's Puzzle: Invert a Binary Tree in under 5 minutes";
      a.subtitle = "A fun brain-teaser for when the build is compiling.";
      a.kicker = "Puzzles";
    }
    if (a.title.includes("cleaner terminal")) {
      a.title = "Comics: 'The Junior Dev and the Force Push'";
      a.subtitle = "A tragicomedy in three git commands.";
      a.kicker = "Comics";
    }
  });
}

fs.writeFileSync('./public/dummy.json', JSON.stringify(data, null, 2));
console.log("Rewrote dummy.json successfully.");

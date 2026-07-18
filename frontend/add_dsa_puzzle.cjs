const fs = require('fs');

const data = JSON.parse(fs.readFileSync('./public/dummy.json', 'utf8'));

const pWeather = data.pages.find(p => p.title.includes("Weather"));

if (pWeather) {
  // Find the old puzzle and replace it, or just add a new one
  const existingPuzzleIndex = pWeather.articles.findIndex(a => a.kicker === "Puzzles");
  
  const dsaPuzzle = {
    "id": "puzzle-dsa-rain-water",
    "page": pWeather.page,
    "category": "misc",
    "importance": 4,
    "title": "The Daily DSA: The Trapping Rain Water Enigma",
    "subtitle": "O(N) time complexity is required. Solution printed in tomorrow's edition.",
    "kicker": "Daily Puzzle",
    "authors": [{ "name": "The Algorithms Desk", "role": "editorial" }],
    "sourceIds": [],
    "sources": [],
    "images": [{
      "src": "/images/dispatch-3.svg",
      "alt": "Rainwater elevation map",
      "caption": "Can you compute the trapped water in a single pass?",
      "credit": "Dispatch Graphics"
    }],
    "content": [
      "Welcome to the Daily DSA! Just as physical newspapers have their daily crosswords and Sudokus, The Dispatch presents a daily test of pointer manipulation and algorithmic efficiency.",
      "**The Problem:** Given `n` non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap after raining.",
      "**Example:** Input: `height = [0,1,0,2,1,0,1,3,2,1,2,1]`. Expected Output: `6`.",
      "**Hint:** You could easily use two arrays to pre-compute the maximum heights to the left and right of every index. But can you solve this puzzle using exactly `O(1)` extra space?",
      "Grab a coffee and a whiteboard. The optimal `O(N)` two-pointer solution will be published in tomorrow's edition (Vol. 1, No. 128) at the bottom of the Classifieds page."
    ],
    "tags": ["dsa", "puzzle", "algorithms"],
    "publishedAt": "2026-07-18T05:00:00+05:30",
    "readTimeMin": 2
  };

  if (existingPuzzleIndex !== -1) {
    pWeather.articles[existingPuzzleIndex] = dsaPuzzle;
  } else {
    pWeather.articles.push(dsaPuzzle);
  }
}

fs.writeFileSync('./public/dummy.json', JSON.stringify(data, null, 2));
console.log("Replaced old puzzle with Daily DSA puzzle.");

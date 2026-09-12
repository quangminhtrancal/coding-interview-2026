// 1. Interfaces vs. TypesFor a senior interview, 
// emphasize that Interfaces are for defining object shapes and 
// supporting "declaration merging," while Types are for unions, intersections, and aliases.
// TypeScript// Interface: Great for objects and extendability
interface User {
  id: number;
  name: string;
}

interface Admin extends User {
  role: 'admin' | 'superadmin';
}

// Type: Great for unique logic or unions
type Status = 'pending' | 'active' | 'closed';
type DataResponse = User | { error: string }; // Union type (Interfaces can't do this)

/*
2. Stack & Queue (LIFO vs. FIFO)
In TypeScript, we use the Array methods, but for a senior role, 
you should wrap them in a class to ensure the API is restricted and predictable.
TypeScript// Stack (LIFO) - Think "Undo" buttons

*/
const stack: number[] = [];
stack.push(10); // Add
const lastItem = stack.pop(); // Remove 10 (O(1))

// Queue (FIFO) - Think "Processing Tasks"
const queue: string[] = [];
queue.push("Task 1"); 
const firstTask = queue.shift(); // Remove "Task 1" (O(n) in JS arrays)

/*
3. Maps & SetsUse these for $O(1)$ lookups. 
Maps are superior to Objects when keys aren't strings or when you need to maintain insertion order.
TypeScript// Set: Unique values only (Great for de-duping)
*/
const uniqueIds = new Set<number>([1, 2, 2, 3]); // Result: {1, 2, 3}
const hasId = uniqueIds.has(1); // O(1) lookup

// Map: Key-Value pairs
const stockPrices = new Map<string, number>();
stockPrices.set("MSFT", 420);
stockPrices.set("AAPL", 180);

if (stockPrices.has("MSFT")) {
  console.log(stockPrices.get("MSFT")); // 420
}

/*
4. Advanced LoopsAvoid traditional for loops unless you need manual index control. 
Use for...of for readability.TypeScriptconst stocks = ["MS", "GS", "JPM"];

*/

// Modern loop for arrays/sets/maps
for (const symbol of stocks) {
  console.log(`Trading: ${symbol}`);
}

// Map specific loop
for (const [symbol, price] of stockPrices) {
  console.log(`${symbol} is trading at $${price}`);
}

/*
5. Priority Queue (The "Senior" Differentiator)Standard JS/TS doesn't have a built-in 
Priority Queue. For an interview, you might be asked to 
implement one or describe how it works. 
It stores elements based on priority rather than just order of arrival.
*/

interface Job {
  priority: number;
  task: string;
}

class SimplePriorityQueue {
  private heap: Job[] = [];

  push(job: Job) {
    this.heap.push(job);
    // In a real Min-Heap, you would "bubble up" here.
    // Simple version: Sort by priority (Ascending)
    this.heap.sort((a, b) => a.priority - b.priority);
  }

  pop(): Job | undefined {
    return this.heap.shift(); // Get the highest priority (lowest number)
  }
}

const pq = new SimplePriorityQueue();
pq.push({ priority: 3, task: "Low Priority" });
pq.push({ priority: 1, task: "CRITICAL FIX" });
console.log(pq.pop()?.task); // "CRITICAL FIX"
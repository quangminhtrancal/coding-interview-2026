https://www.linkedin.com/posts/soubhik285_autodesk-interviewexperience-paidpartnership-activity-7321848474394574848-V5y9/

→ JavaScript​: Polyfills, callback hell, memoization, garbage collection, promises, async/await
→ React: Reconciliation, virtual DOM updates, useReducer, useMemo, custom hooks
→ Redux: Usage, comparison with useContext, and when to prefer it


## JavaScript: Core & Async1. PolyfillsQuestion: What is a polyfill, and can you write a simplified polyfill for Array.prototype.map?Answer: A polyfill is a piece of code used to provide modern functionality on older browsers that do not natively support it.

### Implementation:JavaScript

'''
if (!Array.prototype.myMap) {
  Array.prototype.myMap = function(callback) {
    const result = [];
    for (let i = 0; i < this.length; i++) {
      result.push(callback(this[i], i, this));
    }
    return result;
  };
}
'''

2. Callback Hell & PromisesQuestion: How do Promises solve "Callback Hell," and what are the trade-offs?Answer: Callback hell occurs when multiple nested callbacks make code unreadable and hard to debug (the "pyramid of doom"). Promises flatten this structure using .then() chaining.Trade-off: While Promises improve readability, they can still lead to "Promise chaining hell." async/await is the modern solution to make asynchronous code read like synchronous code.

3. MemoizationQuestion: Implement a generic memoize function.Answer: Memoization is an optimization technique that stores the results of expensive function calls.


function memoize(fn) {
  const cache = {};
  return function(...args) {
    const key = JSON.stringify(args);
    if (cache[key]) return cache[key];
    const result = fn.apply(this, args);
    cache[key] = result;
    return result;
  };
}

4. Garbage Collection (GC)Question: How does JavaScript handle memory management, and what is a common cause of memory leaks?Answer: JS uses a Mark-and-Sweep algorithm. It starts from "roots" (global objects) and marks everything reachable. Unreachable objects are swept.Memory Leaks: Common causes include forgotten timers (setInterval), global variables, and closures holding onto large objects longer than necessary.

## React: Internals & Performance

1. Reconciliation & Virtual DOMQuestion: Explain the reconciliation process and the role of "keys."Answer: React creates a Virtual DOM (a lightweight JS object). When state changes, a new VDOM is created. React "diffs" the new VDOM against the old one (reconciliation) to calculate the minimum number of changes needed for the Real DOM.Keys: Keys provide a stable identity for elements in a list, allowing React to track which items changed, were added, or were removed, rather than re-rendering the whole list.

2. useReducer vs. useStateQuestion: When would you choose useReducer over useState?Answer: Use useReducer when:The state logic is complex (multiple sub-values).The next state depends on the previous state.You want to optimize performance for components that trigger deep updates (you can pass dispatch down instead of callbacks).

3. useMemo & Custom HooksQuestion: What is the risk of overusing useMemo?Answer: useMemo has its own overhead (memory for the cache and the cost of the dependency check). If used for cheap calculations, the overhead might outweigh the benefits.Question: Why use Custom Hooks?Answer: They allow you to extract component logic into reusable functions. This follows the DRY (Don't Repeat Yourself) principle and keeps components focused on the UI.

## Redux: Scalability & State

1. Usage & ArchitectureQuestion: Describe the Redux data flow.Answer: It follows a unidirectional data flow:Action: An object describing "what happened."Reducer: A pure function that calculates the new state based on the action.Store: The single source of truth holding the state.View: Subscribes to the store and updates.

2. Redux vs. useContextQuestion: When do you prefer Redux over the Context API?Table Comparison:FeatureContext APIReduxPrimary GoalDependency Injection (passing data)State ManagementPerformanceRe-renders all consumers on any changeOptimized; only subscribed components re-renderDebuggingBasicAdvanced (Redux DevTools, Time Travel)MiddlewareNone (requires custom logic)Built-in (Saga, Thunk for side effects)

Final Answer: Prefer Redux for large-scale applications with frequent state updates and complex logic (like GCPay’s payment flows). Use Context for low-frequency updates like themes, user locales, or authentication state.
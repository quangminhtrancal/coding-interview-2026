/*
 1. Build a Debounced Search Component
 The goal here is to prevent "API spam." If a user types "Construction," 
 you don't want 12 API calls; you want one.

 */

 import React, { useState, useEffect, useMemo } from 'react';

 const SearchBox: React.FC = () => {
    const [query, setQuery] = useState<string>("");
    const [results, setResults] = useState<any[]>([]);

    useEffect(() => {
        // 1. set the timer
        const handler = setTimeout(() => {
            if (query) {
                console.log(`Fetching results for: ${query}`);

                fetch(`/api/search?q=${query}`)
                .then(data => data.json())
                .then(jsonData => setResults(jsonData))
                .catch(error => console.error(`Error during fetching ${error}`));
            }
        }, 300);

        // 2. Cleanup: This runs if 'query' changes before 300 ms is up
        return () => {
            clearTimeout(handler)
        };
    }, [query]);

    return (
        <input 
            type="text"
            placeholder="Search infoices ..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
        />
    );

 };

/*
2. Reusable Table Component with Sorting
In professional UI, we never hardcode tables. We drive them with a columns configuration.
*/

interface Column {
    key: string;
    label: string;
}

interface Props {
    data: any[];
    columns: Column[];
}

const SortableTable = ({ data, columns }: Props) => {
    const [sortConfig, setSortConfig] = useState<{ key: string, direction: 'asc'| 'desc'} | null>(null);

    // Memoiz sorted data to prevent re-sorting on every render
    const sortedData = useMemo(() => {
        if (!sortConfig) {
            return data;
        }

        return [...data].sort((a, b) => {
            if (a[sortConfig.key] < b[sortConfig.key]) {
                return sortConfig.direction === 'asc'? -1 : 1;
            }
            else if (a[sortConfig.key] > b[sortConfig.key]) {
                return sortConfig.direction === 'asc'? 1: -1;
            }
            else {
                return 0;
            }
        });
    }, [data, sortConfig]);

    return (
        <table>
            <thead>
                <tr>
                    {columns.map(col => (
                        <th key={col.key} onClick={() => setSortConfig({
                            key: col.key,
                            direction: sortConfig?.key === col.key && sortConfig.direction === 'asc' ? 'desc': 'asc'
                        })}>
                            {col.label} {sortConfig?.key === col.key ? (sortConfig.direction === 'asc' ? '▲' : '▼') : ''}
                        </th>
                    ))}
                </tr>
            </thead>
            <tbody>
                {sortedData.map((row, i) => (
                    <tr key={i}>    
                        {columns.map(col => <td key={col.key}>{row[col.key]}</td>)}
                    </tr>
                ))}
            </tbody>
        </table>
    );
};

/*
3. Implement a Custom Hook: useFetch
This demonstrates your ability to abstract logic away from the view layer.
*/
function useFetch<T>(url: string) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController(); // Senior move: Handle unmounted component fetches

    setLoading(true);
    fetch(url, { signal: controller.signal })
      .then(res => res.json())
      .then(setData)
      .catch(err => {
        if (err.name !== 'AbortError') setError(err.message);
      })
      .finally(() => setLoading(false));

    return () => controller.abort(); // Cleanup
  }, [url]);

  return { data, loading, error };
}


 /*1. useStateUsed for managing local state. TypeScript usually infers the type, 
but you can be explicit using generics.TypeScriptimport { useState } from 'react';
 */

const Counter = () => {
  // TypeScript infers this is a number
  const [count, setCount] = useState<number>(0);
  
  // For complex objects or nulls
  interface User { name: string; age: number }
  const [user, setUser] = useState<User | null>(null);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(prev => prev + 1)}>Increment</button>
    </div>
  );
};

// 2. useEffectUsed for side effects like API calls or subscriptions. It doesn't require a generic type because it returns nothing (void or a cleanup function).TypeScriptimport { useEffect, useState } from 'react';

const DataFetcher = () => {
  useEffect(() => {
    const timer = setTimeout(() => {
      console.log("Effect running");
    }, 1000);

    // Cleanup function (Crucial for performance)
    return () => clearTimeout(timer);
  }, []); // Empty array means it runs once on mount

  return <div>Check the console</div>;
};

// 3. useContextUsed to share data across the component tree without prop drilling.TypeScriptimport { createContext, useContext, useState } from 'react';

// 1. Define the shape of the context
type Theme = 'light' | 'dark';
interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

// 2. Create the context with a default value
const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider = ({ children }: { children: React.ReactNode }) => {
  const [theme, setTheme] = useState<Theme>('light');
  const toggleTheme = () => setTheme(t => t === 'light' ? 'dark' : 'light');

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

// 3. Use the hook
const ThemeButton = () => {
  const context = useContext(ThemeContext);
  if (!context) throw new Error("Must be used within ThemeProvider");
  
  return <button onClick={context.toggleTheme}>Style: {context.theme}</button>;
};

// 4. useRefUsed for accessing DOM elements or storing mutable values that don't trigger re-renders.TypeScriptimport { useRef, useEffect } from 'react';

const FocusInput = () => {
  // Explicitly type the DOM element
  const inputRef = useRef<HTMLInputElement>(null);

  const handleClick = () => {
    // Current might be null, so we use optional chaining
    inputRef.current?.focus();
  };

  return (
    <>
      <input ref={inputRef} type="text" />
      <button onClick={handleClick}>Focus the input</button>
    </>
  );
};

// 5. useMemo & useCallbackuseMemo: Memoizes a value (prevents expensive recalculations).useCallback: Memoizes a function (prevents unnecessary child re-renders).TypeScriptimport { useState, useMemo, useCallback } from 'react';

const ExpensiveComponent = () => {
  const [count, setCount] = useState(0);
  const [items] = useState([1, 2, 3, 4, 5]);

  // Only recalculates if 'items' changes
  const sum = useMemo(() => {
    console.log("Calculating...");
    return items.reduce((a, b) => a + b, 0);
  }, [items]);

  // Returns the same function instance unless 'count' changes
  const logCount = useCallback(() => {
    console.log(`Current count: ${count}`);
  }, [count]);

  return <button onClick={() => setCount(count + 1)}>Sum is {sum}</button>;
};

// 6. useReducerAn alternative to useState for complex state logic (similar to Redux).TypeScriptimport { useReducer } from 'react';

type State = { count: number };
type Action = { type: 'increment' } | { type: 'decrement' } | { type: 'reset'; payload: number };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'increment': return { count: state.count + 1 };
    case 'decrement': return { count: state.count - 1 };
    case 'reset': return { count: action.payload };
    default: return state;
  }
}

const Counter = () => {
  const [state, dispatch] = useReducer(reducer, { count: 0 });

  return (
    <div>
      {state.count}
      <button onClick={() => dispatch({ type: 'increment' })}>+</button>
      <button onClick={() => dispatch({ type: 'reset', payload: 0 })}>Reset</button>
    </div>
  );
};
// Comparison TableHookPurposeCommon TS Type RequirementuseStateLocal variablesGeneric: 
// <T>useRefDOM or persistent valuesElement type: <HTMLDivElement>useContextGlobal-ish stateInterface 
// for the context objectuseReducerComplex logicUnion types for Actions

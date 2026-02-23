import { useState, useEffect } from "react";

export default function SearchComponent({ query }: { query: string }) {
  const [result, setResults] = useState<any[]>(null);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const response = await fetch(`/api/search?q=${query}`);
        const jsonData = await response.json();
        setResults(jsonData);
      } catch (error) {
        console.error(`Error during fetching ${error}`);
      }
    };

  const handler = setTimeout(() => {
    if (query) fetchResults();
  }, 300);

  return () => clearTimeout(handler);
}, [query]);

// ===================
interface User {
  id: number;
  name: string;
}

interface UserSettings {
  theme: 'light' | 'dark';
  notifications: boolean;
}

// Map using an Object as a Key
const userPreferences = new Map<User, UserSettings>();

const alice: User = { id: 1, name: "Alice" };

userPreferences.set(alice, {
  theme: 'dark',
  notifications: true
});

// Accessing by the object reference
console.log(userPreferences.get(alice)?.theme); // "dark"

// =====================
// Define a Map with string keys and number values
const inventory = new Map<string, number>();

// Adding items
inventory.set("Hammer", 10);
inventory.set("Screwdriver", 25);
inventory.set("Wrench", 15);

// Getting a value
const hammerCount = inventory.get("Hammer"); // 10

// Checking existence
if (inventory.has("Wrench")) {
  console.log("Wrenches are in stock!");
}

// Deleting an item
inventory.delete("Screwdriver");

// Size of the map
console.log(inventory.size); // 2

// ==============
const statusCodes = new Map<number, string>([
  [200, "OK"],
  [404, "Not Found"],
  [500, "Internal Server Error"]
]);
// ===================
const user = {
  id: 1,
  username: "jdoe_fintech",
  email: "jd@gcpay.com"
};

Object.keys(user).forEach((key) => {
  // We cast 'key' to 'keyof typeof user' so TS knows it's a valid property
  const value = user[key as keyof typeof user];
  console.log(`${key}: ${value}`);
});

for (const [key, value] of Object.entries(user)) {
    console.log();
}

// ############ Flatten nested
function flatten(value) {
    if (Array.isArray(value)) {
      return flattenArrays(value)
    }
    else if (value instanceof Object) {
      return flattenObject(value)
    }
    else {
      return value;  
    }
}

function flattenArrays(array) {
    const result = [];
    for (let i = 0; i< array.length; i++) {
        const element = flatten(array[i]);

        if (Array.isArray(element)) {
            result.push(...element);
        }
        else {
            result.push(element);
        }
    }

    return result;
}

function flattenObject(object) {
    const flattennedObject = {}
    for (const [key, value] of Object.entries(object)) {
        const flattenedValue = flatten(value);

        if (value instanceof Object) {
            Object.assign(flattennedObject, flattenedValue);
        }
        else {
            flattennedObject[key] = flattenedValue;
        }
    }

    return flattennedObject;
}

// Infinite scrolling

const commentsContainer = document.getElementById('test-comment');
commentsContainer?.addEventListener('scroll', handleScroll);

function handleScroll() {
    if (!canFetchComments) {
        return;
    }

    fetchAndAppendComments();

}

async function fetchAndAppendComments() {
    canFetchComments = false;

    const response = await fetch(url);
    const {hasNext, comments} = await response.json();

    const fragment = document.createDocumentFragment();
    comments.foreach((comment) => {
        fragment.appendChild(createCommentElement(comment));
    });

    commentsContainer?.appendChild(fragment);

    if (hasNext) {
        // get cursor for next call to update url 
    } else {
        commentsContainer?.removeEventListener('scroll', handleScroll);
    }

    canFetchComments = true;
}

function createCommentElement(message) {
    const commentElement = document.createElement('p');

    commentElement.classList.add('comment');
    commentElement.textContent = message;
    return commentElement;
}
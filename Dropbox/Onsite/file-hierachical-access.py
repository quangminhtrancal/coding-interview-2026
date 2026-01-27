'''
"You are asked to simulate a simple hierarchical file system and implement an access-check function.\n\nThe file system consists of folders arranged in a tree. A user is granted **direct access** to a subset of folders. Access is **inherited down the tree**: if the user has access to a parent folder, they automatically have access to all of its descendant folders.\n\nYou are given:\n\n- A list of all folders in the system, represented as absolute paths from the root. For example, a tree like:\n\n```text\n/\n├── A\n│   ├── B\n│   │   ├── C\n│   │   └── D\n│   └── E\n└── F\n```\n\ncould be represented as:\n\n```text\nallFolders = [\n  \"/\",      \n  \"/A\",\n  \"/A/B\",\n  \"/A/B/C\",\n  \"/A/B/D\",\n  \"/A/E\",\n  \"/F\"\n]\n```\n\n- A set of folder paths `accessibleFolders` representing folders to which the user has **direct** access. For example:\n\n```text\naccessibleFolders = { \"/A\", \"/F\" }\n```\n\nYou need to implement the function:\n\n```text\nbool HasAccess(string folderPath)\n```\n\nthat returns:\n\n- `true` if the user has access to `folderPath` **either** because:\n  - `folderPath` is in `accessibleFolders`, **or**\n  - some ancestor folder of `folderPath` (e.g., `/A` is an ancestor of `/A/B/C`) is in `accessibleFolders`.\n- `false` otherwise.\n\nAssume:\n\n- All folder paths in `allFolders` and `accessibleFolders` are normalized absolute paths starting with `'/'`, with components separated by `'/'` (e.g., `/A/B/C`).\n- `folderPath` passed into `HasAccess` is always a valid folder path present in `allFolders`.\n\nExamples (given the tree above and `accessibleFolders = {\"/A\", \"/F\"}`):\n\n- `HasAccess(\"/A\")` → `true` (direct access)\n- `HasAccess(\"/A/B\")` → `true` (inherits from `/A`)\n- `HasAccess(\"/A/B/C\")` → `true` (inherits from `/A`)\n- `HasAccess(\"/A/E\")` → `true` (inherits from `/A`)\n- `HasAccess(\"/F\")` → `true` (direct access)\n- `HasAccess(\"/\")` → `false` (no access to root unless `/` is in `accessibleFolders`)\n\nDesign and implement `HasAccess` so that it can be called many times efficiently after the initial inputs (`allFolders` and `accessibleFolders`) are known.",

https://prachub.com/interview-questions/implement-hierarchical-folder-access-check

You are asked to simulate a simple hierarchical file system and implement an access-check function.

The file system consists of folders arranged in a tree. A user is granted direct access to a subset of folders. Access is inherited down the tree: if the user has access to a parent folder, they automatically have access to all of its descendant folders.

You are given:

A list of all folders in the system, represented as absolute paths from the root. For example, a tree like:
/
├── A
│   ├── B
│   │   ├── C
│   │   └── D
│   └── E
└── F
could be represented as:

allFolders = [
  "/",      
  "/A",
  "/A/B",
  "/A/B/C",
  "/A/B/D",
  "/A/E",
  "/F"
]
A set of folder paths accessibleFolders representing folders to which the user has direct access. For example:
accessibleFolders = { "/A", "/F" }
You need to implement the function:

bool HasAccess(string folderPath)
that returns:

true if the user has access to folderPath either because:
folderPath is in accessibleFolders , or
some ancestor folder of folderPath (e.g., /A is an ancestor of /A/B/C ) is in accessibleFolders .
false otherwise.
Assume:

All folder paths in allFolders and accessibleFolders are normalized absolute paths starting with '/' , with components separated by '/' (e.g., /A/B/C ).
folderPath passed into HasAccess is always a valid folder path present in allFolders .
Examples (given the tree above and accessibleFolders = {"/A", "/F"}):

HasAccess("/A") → true (direct access)
HasAccess("/A/B") → true (inherits from /A )
HasAccess("/A/B/C") → true (inherits from /A )
HasAccess("/A/E") → true (inherits from /A )
HasAccess("/F") → true (direct access)
HasAccess("/") → false (no access to root unless / is in accessibleFolders )
Design and implement HasAccess so that it can be called many times efficiently after the initial inputs (allFolders and accessibleFolders) are known.
'''
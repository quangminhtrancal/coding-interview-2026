/*
1.)Given an integer array named yCoordinates where yCoordinates[i] represents the Y axis and each index represents the X axis. Find the strictly increasing contiguous slope of the give points of size exactly K.

Example:
Input:

[6,5,7,8,3,5,6] and k=3

The points are (0,6),(1,5),(2,7),(3,8),(4,3),(5,5),(6,6)

output : 2

Possible increasing slopes are:
(1,5),(2,7),(3,8)
(4,3)(5,5),(6,6)

constraints:
1<=yCoordinates.size()<=10^5;
yCoorinates[i]>=1

https://leetcode.com/discuss/post/8513902/ibm-coding-assessment-2-on-campus-by-ano-vs12/ 
*/

import java.util.Arrays;

public class LCQuestions {

    static int countIncreasingSlopes(int[] yCoordinates, int k) {
        int n = yCoordinates.length;
        if (k <= 0 || n < k) {
            return 0;
        }
        if (k == 1) {
            return n;
        }

        int count = 0;
        int runLength = 1;

        for (int i = 1; i < n; i++) {
            if (yCoordinates[i] > yCoordinates[i - 1]) {
                runLength++;
            } else {
                runLength = 1;
            }
            if (runLength >= k) {
                count++;
            }
        }

        return count;
    }

    public static void main(String[] args) {
        int[] yCoordinates = {6, 5, 7, 8, 3, 5, 6};
        System.out.println(countIncreasingSlopes(yCoordinates, 3));
        System.out.println(Arrays.toString(areSimilar(
                new String[]{"aabaab", "aaaaabb"},
                new String[]{"bbabbc", "abbbbbb"})));
    }

    static String[] areSimilar(String[] first, String[] second) {
        String[] result = new String[first.length];

        for (int i = 0; i < first.length; i++) {
            int[] freqFirst = new int[26];
            int[] freqSecond = new int[26];

            for (char ch : first[i].toCharArray()) {
                freqFirst[ch - 'a']++;
            }
            for (char ch : second[i].toCharArray()) {
                freqSecond[ch - 'a']++;
            }

            boolean similar = true;
            for (int c = 0; c < 26; c++) {
                if (Math.abs(freqFirst[c] - freqSecond[c]) > 3) {
                    similar = false;
                    break;
                }
            }

            result[i] = similar ? "YES" : "NO";
        }

        return result;
    }
}

/*
https://leetcode.com/discuss/post/8499672/ibm-coding-assessment-question-similar-s-x19p/

I encountered this problem in an IBM Coding Assessment and found the frequency-counting observation quite straightforward but interesting. Sharing it here for others preparing for IBM coding assessments and DSA interviews.

Problem Statement

You are given two arrays of strings, s and t, each of length n.

Each pair s[i] and t[i] contains two lowercase English strings.

Two strings are considered similar if, for every lowercase English letter from 'a' to 'z', the absolute difference between the number of occurrences of that letter in the two strings is at most 3.

In other words, for every character x:

abs(count(s[i], x) - count(t[i], x)) <= 3

Your task is to check every corresponding pair s[i] and t[i].

Return an array where:

"YES" means the pair is similar.
"NO" means the pair is not similar.
Example

Suppose we have two pairs of strings.

For the first pair, after counting the characters, we get something like:

Letter Count in s Count in t Difference
a 4 1 3
b 2 4 2
c 0 1 1

Since every difference is at most 3, this pair is similar.

For the second pair:

Letter Count in s Count in t Difference
a 5 1 4
b 2 6 4

Here the difference is greater than 3, so this pair is not similar.

Therefore, the output can be:

["YES", "NO"]
Key Observation

We don't need to compare the strings character-by-character.

The condition only depends on the frequency of each lowercase English letter.

Since there are only 26 lowercase letters, for every pair we can:

Count the frequency of all characters in the first string.
Count the frequency of all characters in the second string.
Compare the frequencies of 'a' through 'z'.
If any frequency difference is greater than 3, return "NO".
Otherwise, return "YES".
Algorithm

For every corresponding pair (s[i], t[i]):

Create two frequency arrays of size 26.
Count characters in s[i].
Count characters in t[i].
For every character from 'a' to 'z':
Calculate the absolute difference between the two frequencies.
If the difference is greater than 3, mark the pair as "NO".
If all 26 characters satisfy the condition, mark the pair as "YES".
Return the resulting array.
Python 3 Solution
def areSimilar(s, t):
result = []

for str1, str2 in zip(s, t):
    freq1 = [0] * 26
    freq2 = [0] * 26

    for ch in str1:
        freq1[ord(ch) - ord('a')] += 1

    for ch in str2:
        freq2[ord(ch) - ord('a')] += 1

    similar = True

    for i in range(26):
        if abs(freq1[i] - freq2[i]) > 3:
            similar = False
            break

    result.append("YES" if similar else "NO")

return result
Complexity

Let L be the total length of the strings being processed.

For each pair, we count every character once and then check 26 letters.

Time Complexity:

O(L + 26n)

Since 26 is constant, this is effectively:

O(L)

Space Complexity:

O(26) = O(1)

for the frequency arrays.

Why This Works

The definition of similarity depends only on character frequencies, not on the order of characters in the strings.

For example:

"abcabc"
"cbacba"

have exactly the same frequency for every character, so they are similar.

The only thing we need to verify is:

|frequency_in_s - frequency_in_t| <= 3

for all 26 lowercase letters.

This problem was encountered in an IBM Coding Assessment.

If anyone else received a similar IBM assessment question, feel free to share the approach or any edge cases that should be considered.

#IBM #CodingAssessment #IBMJobs #DSA #Strings #FrequencyCounting #Python #CodingInterview #OnlineAssessment

*/


/*
https://leetcode.com/discuss/post/8488656/ibm-india-online-assessment-oa-applicati-sevo/
    I encountered this problem in an IBM Coding Assessment and found the frequency-counting observation quite straightforward but interesting. Sharing it here for others preparing for IBM coding assessments and DSA interviews.

Problem Statement

You are given two arrays of strings, s and t, each of length n.

Each pair s[i] and t[i] contains two lowercase English strings.

Two strings are considered similar if, for every lowercase English letter from 'a' to 'z', the absolute difference between the number of occurrences of that letter in the two strings is at most 3.

In other words, for every character x:

abs(count(s[i], x) - count(t[i], x)) <= 3

Your task is to check every corresponding pair s[i] and t[i].

Return an array where:

"YES" means the pair is similar.
"NO" means the pair is not similar.
Example

Suppose we have two pairs of strings.

For the first pair, after counting the characters, we get something like:

Letter Count in s Count in t Difference
a 4 1 3
b 2 4 2
c 0 1 1

Since every difference is at most 3, this pair is similar.

For the second pair:

Letter Count in s Count in t Difference
a 5 1 4
b 2 6 4

Here the difference is greater than 3, so this pair is not similar.

Therefore, the output can be:

["YES", "NO"]
Key Observation

We don't need to compare the strings character-by-character.

The condition only depends on the frequency of each lowercase English letter.

Since there are only 26 lowercase letters, for every pair we can:

Count the frequency of all characters in the first string.
Count the frequency of all characters in the second string.
Compare the frequencies of 'a' through 'z'.
If any frequency difference is greater than 3, return "NO".
Otherwise, return "YES".
Algorithm

For every corresponding pair (s[i], t[i]):

Create two frequency arrays of size 26.
Count characters in s[i].
Count characters in t[i].
For every character from 'a' to 'z':
Calculate the absolute difference between the two frequencies.
If the difference is greater than 3, mark the pair as "NO".
If all 26 characters satisfy the condition, mark the pair as "YES".
Return the resulting array.
Python 3 Solution
def areSimilar(s, t):
result = []

for str1, str2 in zip(s, t):
    freq1 = [0] * 26
    freq2 = [0] * 26

    for ch in str1:
        freq1[ord(ch) - ord('a')] += 1

    for ch in str2:
        freq2[ord(ch) - ord('a')] += 1

    similar = True

    for i in range(26):
        if abs(freq1[i] - freq2[i]) > 3:
            similar = False
            break

    result.append("YES" if similar else "NO")

return result
Complexity

Let L be the total length of the strings being processed.

For each pair, we count every character once and then check 26 letters.

Time Complexity:

O(L + 26n)

Since 26 is constant, this is effectively:

O(L)

Space Complexity:

O(26) = O(1)

for the frequency arrays.

Why This Works

The definition of similarity depends only on character frequencies, not on the order of characters in the strings.

For example:

"abcabc"
"cbacba"

have exactly the same frequency for every character, so they are similar.

The only thing we need to verify is:

|frequency_in_s - frequency_in_t| <= 3

for all 26 lowercase letters.

This problem was encountered in an IBM Coding Assessment.

If anyone else received a similar IBM assessment question, feel free to share the approach or any edge cases that should be considered.

#IBM #CodingAssessment #IBMJobs #DSA #Strings #FrequencyCounting #Python #CodingInterview #OnlineAssessment
*/

/*
https://leetcode.com/discuss/post/8429606/ibm-oa-30-july-2026-dsa-question-by-arya-6i52/
IBM OA 30 July 2026 - DSA Question (from offline images 1.jpeg, 2.jpeg, code.jpeg):

Question 1:
You are given two arrays of strings, s and t, each of length n.
Each pair (s[i], t[i]) contains two lowercase English strings.
Two strings are considered similar if for every letter x ('a' to 'z'),
the absolute difference in how many times x appears in the two strings is at most 3.

Task:
- For each pair (s[i], t[i]), check whether the strings are similar.
- Return an array of n elements: "YES" if similar, "NO" otherwise.

Example:
s = ["aabaab", "aaaaabb"] and t = ["bbabbc", "abbbbbb"]
Output: ["YES", "NO"]
s[0] counts: a=4 b=2 c=0; t[0] counts: a=1 b=4 c=1; diffs 3,2,1 -> YES.
s[1] counts: a=5 b=2; t[1] counts: a=1 b=6; diffs 4,4 -> NO.

Constraints:
1 <= n <= 5
1 <= length of any string <= 10^5

Test Case Input Format:
first line n, next n lines s[i], next line n, next n lines t[i].

Answer: areSimilar() below. O(totalLength + 26*n) time, O(26)=O(1) aux space.
*/

/*
https://leetcode.com/discuss/post/8335130/ibm-coding-assesment-for-ai-backend-engi-uf85/
Given an array arr and an integer d, count the number of triplets (i, j, k) such that i < j < k and the difference between the maximum and minimum element in the triplet is at most d. Return the count modulo 10^9 + 7. The optimal solution uses sorting + two pointers/sliding window + combinations to count valid triplets efficiently.

Given a runner's sex and marathon_name, use a paginated REST API to find the runner with the highest top_speed. First fetch page 1 to get total_pages, then iterate through all pages, process the data array, track the maximum top_speed, and return the corresponding runner's name. This tests API handling, pagination, JSON parsing, and iteration, not advanced DSA.
*/

/*
Focus on golang mainly concepts like Goroutines, channels, mutex, context, race condition, program on these concepts and expect DSA too. Recruiter told me there will be DSA and I would say system design of your current project
I have interview on monday. Please share your experience after ur interview. That would be helpful for me.
*/

/*
https://leetcode.com/discuss/post/7597918/ibm-ai-developer-entry-level-interview-q-9qza/
The first question took me around 5 minutes to do. The second one hit me in a large blind spot, and no question on Leetcode will prepare you for it. Putting this here as a potential warning. Even with 50 minutes left over, I wasn't ready to answer Q2. Apologies if some of it doesn't entirely make sense. I am doing this entirely by memory. The whole interview was an hour.

Q1. Leetcode (Easy)
You are given a list of strings that represent a set of requests sent by different machines at particular points.

An example:
For 3 machines this would be the result of five requests.
["YYN", "NNN", "YNY", "YYY", "YYY"]

We want to find the max amount of times in a row all machines respond with "Y".

["YYN", "NNN", "YNY", "YYY", "YYY"] --> 2
["YYY", "YYY", "YNY", "YYY", "YYY", "YYY"] --> 3
[] --> 0

Q2. REST API Question (Easy to Med)
You are given a URL format which gets several bits of information.

http://api.notrealwebsite.xyz/movies/page/{insertNumHere}

The insertNumHere will give you the data on specified page number. The API will return the following.

"currentPage" : Gives current page.
"totalResults" : gives total Number of hits for the request across all pages
"totalPages" : This is the number of different page URLs provided by the request.
"data": Gives an JSONArray with several data points. Will max out at 10 per page (or request since each request will need a different page number

Within data, you can get several things such as the description, date published, ect. But only three important pieces are relevent.

data[i]{
movietitle : "Lord of the Rings"
genre : "Fantasy, Action, Fiction" (Multiple genres can be found on a movie)
rating : "9.5"
}

==========================

You are given a function that has a string parameter: "genre".
You function should return a string which is the name of the highest rated movie title of said genre. To get the data, you will need to use REST API requests at the provided the URL with the correct format. If you have two or more movies with the same rating, return the lexicogrpahically smallest. (Aka, closest to A in the alphabet.)

You will have imports pre-given to you, likely the ones most commonly used in your programming language. But you will not be given any instruction on how to use any of the imports. It is assumed that you now how to use the imports to make a REST API request yourself, as well as properly translate it into JSON and JSON arrays.

You will also have to use a try/catch, but not throw any sort of custom exception (unless specified) because you cannot edit all of the code on the page. I tried to throw a generic exception, but the function that called it then needed said exception to be thrown, but I couldn't edit said block.
*/
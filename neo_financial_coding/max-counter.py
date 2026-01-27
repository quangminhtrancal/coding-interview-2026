'''
// Instructions:
// You are given N counterArray, initially set to 0, and you have two possible operations on them:

// increase(X) − counter X is increased by 1,
// max counter − all counterArray are set to the maximum value of any counter.
// A non-empty array A of M integers is given. This array represents consecutive operations:

// if A[K] = X, such that 1 ≤ X ≤ N, then operation K is increase(X),
// if A[K] = N + 1 then operation K is max counter.
// For example, given integer N = 5 and array A such that:

//     A[0] = 3
//     A[1] = 4
//     A[2] = 4
//     A[3] = 6
//     A[4] = 1
//     A[5] = 4
//     A[6] = 4
// the values of the counterArray after each consecutive operation will be:

//     (0, 0, 1, 0, 0)
//     (0, 0, 1, 1, 0)
//     (0, 0, 1, 2, 0)
//     (2, 2, 2, 2, 2)
//     (3, 2, 2, 2, 2)
//     (3, 2, 2, 3, 2)
//     (3, 2, 2, 4, 2)
// The goal is to calculate the value of every counter after all operations.

// Write a function:

// function solution(N, A);

// that, given an integer N and a non-empty array A consisting of M integers, returns a sequence of integers representing the values of the counterArray.

// Result array should be returned as an array of integers.

// For example, given:

//     A[0] = 3
//     A[1] = 4
//     A[2] = 4
//     A[3] = 6
//     A[4] = 1
//     A[5] = 4
//     A[6] = 4
// the function should return [3, 2, 2, 4, 2], as explained above.

// Write an efficient algorithm for the following assumptions:

// N and M are integers within the range [1..100,000];
// each element of array A is an integer within the range [1..N + 1].
'''

def solution(N, A):
    counters = [0] * N
    max_counter = 0
    last_update = 0

    for op in A:
        if 1 <= op <= N:
            idx = op - 1
            # Ensure counter is at least last_update before increment
            if counters[idx] < last_update:
                counters[idx] = last_update
            counters[idx] += 1
            if counters[idx] > max_counter:
                max_counter = counters[idx]
        elif op == N + 1:
            last_update = max_counter # Do we need to reset last_update here?

    # Final update for all counters
    for i in range(N):
        if counters[i] < last_update:
            counters[i] = last_update

    return counters
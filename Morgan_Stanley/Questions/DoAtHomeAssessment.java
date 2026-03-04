// Do-At-Home Assessment
//
// Assignment (Java): Java Programming and Unit Test
//
// Write a Java program that does the following: given an array of numbers, find the highest number in the array and print it to console.
//
// Example of the array: int[] numbers = new int[]{5, 4, 14, 7, 2, 18, 11}
//
// Also, please write meaningful unit test/s that tests your Java program.

public class DoAtHomeAssessment {

    /**
     * Finds the highest number in an array
     * @param numbers array of integers
     * @return the highest number in the array
     * @throws IllegalArgumentException if array is null or empty
     */
    public static int findHighestNumber(int[] numbers) {
        if (numbers == null || numbers.length == 0) {
            throw new IllegalArgumentException("Array cannot be null or empty");
        }

        int highest = numbers[0];
        for (int i = 1; i < numbers.length; i++) {
            if (numbers[i] > highest) {
                highest = numbers[i];
            }
        }
        return highest;
    }

    public static void main(String[] args) {
        int[] numbers = new int[]{5, 4, 14, 7, 2, 18, 11};
        int highest = findHighestNumber(numbers);
        System.out.println("The highest number is: " + highest);
    }
}

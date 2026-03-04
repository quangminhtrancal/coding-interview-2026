/*
Unit tests for DoAtHomeAssessment

Write a Java program that does the following: given an array of numbers, 
find the highest number in the array and print it to console
Example of the array: int[] numbers = new int[]{5, 4, 14, 7, 2, 18, 11} 
 This file contains meaningful unit tests 
 for the findHighestNumber method
*/


import org.junit.Test;
import static org.junit.Assert.*;

public class DoAtHomeAssessmentTest {

    @Test
    public void testFindHighestNumber_withGivenExample() {
        int[] numbers = new int[]{5, 4, 14, 7, 2, 18, 11};
        int result = DoAtHomeAssessment.findHighestNumber(numbers);
        assertEquals(18, result);
    }

    @Test
    public void testFindHighestNumber_withSingleElement() {
        int[] numbers = new int[]{42};
        int result = DoAtHomeAssessment.findHighestNumber(numbers);
        assertEquals(42, result);
    }

    @Test
    public void testFindHighestNumber_withNegativeNumbers() {
        int[] numbers = new int[]{-5, -10, -3, -20, -1};
        int result = DoAtHomeAssessment.findHighestNumber(numbers);
        assertEquals(-1, result);
    }

    @Test
    public void testFindHighestNumber_withMixedNumbers() {
        int[] numbers = new int[]{-5, 0, 10, -3, 20};
        int result = DoAtHomeAssessment.findHighestNumber(numbers);
        assertEquals(20, result);
    }

    @Test
    public void testFindHighestNumber_withDuplicates() {
        int[] numbers = new int[]{5, 10, 10, 3, 10};
        int result = DoAtHomeAssessment.findHighestNumber(numbers);
        assertEquals(10, result);
    }

    @Test
    public void testFindHighestNumber_highestAtBeginning() {
        int[] numbers = new int[]{100, 5, 10, 3};
        int result = DoAtHomeAssessment.findHighestNumber(numbers);
        assertEquals(100, result);
    }

    @Test
    public void testFindHighestNumber_highestAtEnd() {
        int[] numbers = new int[]{5, 10, 3, 100};
        int result = DoAtHomeAssessment.findHighestNumber(numbers);
        assertEquals(100, result);
    }

    @Test(expected = IllegalArgumentException.class)
    public void testFindHighestNumber_withNullArray() {
        DoAtHomeAssessment.findHighestNumber(null);
    }

    @Test(expected = IllegalArgumentException.class)
    public void testFindHighestNumber_withEmptyArray() {
        int[] numbers = new int[]{};
        DoAtHomeAssessment.findHighestNumber(numbers);
    }
}

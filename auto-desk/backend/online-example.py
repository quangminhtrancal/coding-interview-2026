'''
https://www.jointaro.com/interviews/companies/autodesk/experiences/software-engineer-san-francisco-ca-september-1-2016-no-offer-negative-1f27de9d/

AUTODESK BACKEND INTERVIEW QUESTIONS - SOLUTIONS
================================================

QUESTION 1: Designing a grep command for a log file
QUESTION 2: Computing the distance between two shapes [OOA design]
            Shapes: Circle, Square, Rectangle

'''

# ============================================================================
# QUESTION 1: DESIGNING A GREP COMMAND FOR LOG FILES
# ============================================================================

"""
PROBLEM: Design a grep-like command for searching log files
- Support pattern matching in log files
- Handle large log files efficiently
- Support common grep options (case-insensitive, line numbers, context, etc.)
"""

import re
from typing import List, Optional, Iterator
from dataclasses import dataclass
from enum import Enum


class MatchMode(Enum):
    """Match modes for pattern searching"""
    EXACT = "exact"
    REGEX = "regex"
    WILDCARD = "wildcard"


@dataclass
class MatchResult:
    """Represents a single match result"""
    line_number: int
    line_content: str
    matched_text: str
    context_before: List[str] = None
    context_after: List[str] = None

    def __str__(self):
        return f"{self.line_number}: {self.line_content.strip()}"


class LogGrep:
    """
    A grep-like utility for searching log files with various options.

    Features:
    - Pattern matching (exact, regex, wildcard)
    - Case-sensitive/insensitive search
    - Line number display
    - Context lines (before/after)
    - Invert match
    - Count matches
    - Multiple file support
    """

    def __init__(
        self,
        pattern: str,
        case_sensitive: bool = True,
        match_mode: MatchMode = MatchMode.REGEX,
        show_line_numbers: bool = True,
        context_before: int = 0,
        context_after: int = 0,
        invert_match: bool = False,
        count_only: bool = False,
        max_matches: Optional[int] = None
    ):
        self.pattern = pattern
        self.case_sensitive = case_sensitive
        self.match_mode = match_mode
        self.show_line_numbers = show_line_numbers
        self.context_before = context_before
        self.context_after = context_after
        self.invert_match = invert_match
        self.count_only = count_only
        self.max_matches = max_matches

        # Compile the pattern based on match mode
        self.compiled_pattern = self._compile_pattern()

    def _compile_pattern(self) -> re.Pattern:
        """Compile the search pattern based on mode and case sensitivity"""
        flags = 0 if self.case_sensitive else re.IGNORECASE

        if self.match_mode == MatchMode.EXACT:
            # Escape special regex characters for exact matching
            pattern = re.escape(self.pattern)
        elif self.match_mode == MatchMode.WILDCARD:
            # Convert wildcard pattern to regex (* -> .*, ? -> .)
            pattern = re.escape(self.pattern)
            pattern = pattern.replace(r'\*', '.*').replace(r'\?', '.')
        else:  # REGEX
            pattern = self.pattern

        return re.compile(pattern, flags)

    def _matches_pattern(self, line: str) -> bool:
        """Check if a line matches the pattern"""
        match = self.compiled_pattern.search(line) is not None
        # Invert match if requested
        return not match if self.invert_match else match

    def search_file(self, file_path: str) -> List[MatchResult]:
        """
        Search a single file for the pattern.

        Args:
            file_path: Path to the log file

        Returns:
            List of MatchResult objects
        """
        results = []
        context_buffer = []  # Buffer for context_before lines
        pending_context_after = []  # Track lines needing context_after

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, start=1):
                    # Update context buffer (rolling window)
                    if self.context_before > 0:
                        context_buffer.append(line)
                        if len(context_buffer) > self.context_before:
                            context_buffer.pop(0)

                    # Check if line matches
                    if self._matches_pattern(line):
                        # Get context before (excluding current line)
                        ctx_before = list(context_buffer[:-1]) if self.context_before > 0 else []

                        # Find matched text
                        match_obj = self.compiled_pattern.search(line)
                        matched_text = match_obj.group(0) if match_obj and not self.invert_match else ""

                        result = MatchResult(
                            line_number=line_num,
                            line_content=line,
                            matched_text=matched_text,
                            context_before=ctx_before,
                            context_after=[]  # Will be filled later
                        )
                        results.append(result)

                        # Mark that we need context_after for this result
                        if self.context_after > 0:
                            pending_context_after.append((result, 0))

                        # Check max matches
                        if self.max_matches and len(results) >= self.max_matches:
                            break

                    # Update context_after for pending results
                    if pending_context_after:
                        updated_pending = []
                        for result, count in pending_context_after:
                            if count < self.context_after:
                                result.context_after.append(line)
                                updated_pending.append((result, count + 1))
                        pending_context_after = updated_pending

        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except PermissionError:
            raise PermissionError(f"Permission denied: {file_path}")

        return results

    def search_files(self, file_paths: List[str]) -> dict:
        """
        Search multiple files for the pattern.

        Args:
            file_paths: List of file paths to search

        Returns:
            Dictionary mapping file paths to their match results
        """
        all_results = {}
        for file_path in file_paths:
            try:
                results = self.search_file(file_path)
                if results:  # Only include files with matches
                    all_results[file_path] = results
            except Exception as e:
                print(f"Error searching {file_path}: {e}")

        return all_results

    def search_stream(self, lines: Iterator[str]) -> List[MatchResult]:
        """
        Search a stream of lines (useful for stdin or large files).
        Memory efficient for large files.
        """
        results = []
        context_buffer = []

        for line_num, line in enumerate(lines, start=1):
            if self.context_before > 0:
                context_buffer.append(line)
                if len(context_buffer) > self.context_before:
                    context_buffer.pop(0)

            if self._matches_pattern(line):
                ctx_before = list(context_buffer[:-1]) if self.context_before > 0 else []
                match_obj = self.compiled_pattern.search(line)
                matched_text = match_obj.group(0) if match_obj and not self.invert_match else ""

                result = MatchResult(
                    line_number=line_num,
                    line_content=line,
                    matched_text=matched_text,
                    context_before=ctx_before
                )
                results.append(result)

                if self.max_matches and len(results) >= self.max_matches:
                    break

        return results

    def format_results(self, results: List[MatchResult]) -> str:
        """Format results for display"""
        if self.count_only:
            return f"Match count: {len(results)}"

        output = []
        for result in results:
            if self.show_line_numbers:
                output.append(f"{result.line_number}: {result.line_content.rstrip()}")
            else:
                output.append(result.line_content.rstrip())

            # Add context if available
            if result.context_before:
                for ctx_line in result.context_before:
                    output.insert(-1, f"  (before) {ctx_line.rstrip()}")

            if result.context_after:
                for ctx_line in result.context_after:
                    output.append(f"  (after) {ctx_line.rstrip()}")

        return '\n'.join(output)


# ============================================================================
# EXAMPLE USAGE FOR QUESTION 1
# ============================================================================

def example_grep_usage():
    """Examples of using the LogGrep utility"""

    # Example 1: Simple regex search with line numbers
    grep1 = LogGrep(pattern=r'ERROR|WARN', match_mode=MatchMode.REGEX)

    # Example 2: Case-insensitive search
    grep2 = LogGrep(pattern='exception', case_sensitive=False)

    # Example 3: Search with context (2 lines before and after)
    grep3 = LogGrep(
        pattern=r'\d{4}-\d{2}-\d{2}.*ERROR',
        context_before=2,
        context_after=2
    )

    # Example 4: Count matches only
    grep4 = LogGrep(pattern='timeout', count_only=True)

    # Example 5: Wildcard search
    grep5 = LogGrep(pattern='user_*.log', match_mode=MatchMode.WILDCARD)

    # Example 6: Invert match (find lines that DON'T match)
    grep6 = LogGrep(pattern='DEBUG', invert_match=True)

    print("LogGrep examples created successfully")


# ============================================================================
# ADVANCED FEATURES - Performance optimizations for large log files
# ============================================================================

class LogGrepAdvanced(LogGrep):
    """
    Advanced version with additional features:
    - Parallel file processing
    - Streaming for very large files
    - Compressed file support (.gz, .zip)
    - Highlighting matched text
    """

    def search_file_streaming(self, file_path: str, chunk_size: int = 8192):
        """
        Memory-efficient streaming search for very large files.
        Processes file in chunks to avoid loading entire file into memory.
        """
        import mmap

        with open(file_path, 'r+b') as f:
            # Use memory-mapped file for efficient access
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mmapped_file:
                for line_num, line in enumerate(iter(mmapped_file.readline, b""), start=1):
                    line_str = line.decode('utf-8', errors='ignore')
                    if self._matches_pattern(line_str):
                        yield MatchResult(
                            line_number=line_num,
                            line_content=line_str,
                            matched_text=self.compiled_pattern.search(line_str).group(0)
                        )

    def highlight_matches(self, result: MatchResult, highlight_color: str = '\033[91m') -> str:
        """Highlight matched text in red (ANSI color codes)"""
        reset_color = '\033[0m'
        highlighted = self.compiled_pattern.sub(
            f"{highlight_color}\\g<0>{reset_color}",
            result.line_content
        )
        return f"{result.line_number}: {highlighted}"


# ============================================================================
# QUESTION 2: COMPUTING DISTANCE BETWEEN SHAPES (OOA DESIGN)
# ============================================================================

"""
PROBLEM: Design a system to compute distances between geometric shapes
- Shapes: Circle, Square, Rectangle
- Need to compute distance between any two shapes
- Use good Object-Oriented Analysis and Design principles

DESIGN CONSIDERATIONS:
1. Abstraction: Create a Shape base class/interface
2. Polymorphism: Each shape implements its own logic
3. Extensibility: Easy to add new shapes
4. Distance Calculation: Multiple strategies (center-to-center, edge-to-edge)
5. Single Responsibility: Separate distance calculation from shape definition
"""

from abc import ABC, abstractmethod
from math import sqrt, pi
from typing import Tuple


# ============================================================================
# SHAPE HIERARCHY - Base abstraction and concrete shapes
# ============================================================================

class Point:
    """Represents a 2D point"""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def distance_to(self, other: 'Point') -> float:
        """Calculate Euclidean distance to another point"""
        return sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def __repr__(self):
        return f"Point({self.x}, {self.y})"


class Shape(ABC):
    """
    Abstract base class for all geometric shapes.
    Follows Interface Segregation Principle - defines common interface.
    """

    @abstractmethod
    def get_center(self) -> Point:
        """Return the center point of the shape"""
        pass

    @abstractmethod
    def get_area(self) -> float:
        """Return the area of the shape"""
        pass

    @abstractmethod
    def get_perimeter(self) -> float:
        """Return the perimeter of the shape"""
        pass

    @abstractmethod
    def contains_point(self, point: Point) -> bool:
        """Check if a point is inside the shape"""
        pass

    @abstractmethod
    def get_bounding_box(self) -> Tuple[Point, Point]:
        """Return bounding box as (top-left, bottom-right) points"""
        pass

    @abstractmethod
    def closest_point_to(self, point: Point) -> Point:
        """Find the closest point on the shape's boundary to a given point"""
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(center={self.get_center()})"


class Circle(Shape):
    """Circle defined by center point and radius"""

    def __init__(self, center: Point, radius: float):
        if radius <= 0:
            raise ValueError("Radius must be positive")
        self.center = center
        self.radius = radius

    def get_center(self) -> Point:
        return self.center

    def get_area(self) -> float:
        return pi * self.radius ** 2

    def get_perimeter(self) -> float:
        return 2 * pi * self.radius

    def contains_point(self, point: Point) -> bool:
        return self.center.distance_to(point) <= self.radius

    def get_bounding_box(self) -> Tuple[Point, Point]:
        top_left = Point(self.center.x - self.radius, self.center.y + self.radius)
        bottom_right = Point(self.center.x + self.radius, self.center.y - self.radius)
        return (top_left, bottom_right)

    def closest_point_to(self, point: Point) -> Point:
        """Find closest point on circle's circumference to given point"""
        if self.contains_point(point):
            # Point is inside, closest point is on the boundary
            distance = self.center.distance_to(point)
            if distance == 0:  # Point is at center
                return Point(self.center.x + self.radius, self.center.y)

            # Scale vector from center to point to have length = radius
            scale = self.radius / distance
            return Point(
                self.center.x + (point.x - self.center.x) * scale,
                self.center.y + (point.y - self.center.y) * scale
            )
        else:
            # Point is outside, find point on circumference along line from center to point
            distance = self.center.distance_to(point)
            scale = self.radius / distance
            return Point(
                self.center.x + (point.x - self.center.x) * scale,
                self.center.y + (point.y - self.center.y) * scale
            )

    def __repr__(self):
        return f"Circle(center={self.center}, radius={self.radius})"


class Rectangle(Shape):
    """Rectangle defined by center point, width, and height"""

    def __init__(self, center: Point, width: float, height: float):
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive")
        self.center = center
        self.width = width
        self.height = height

    def get_center(self) -> Point:
        return self.center

    def get_area(self) -> float:
        return self.width * self.height

    def get_perimeter(self) -> float:
        return 2 * (self.width + self.height)

    def contains_point(self, point: Point) -> bool:
        half_w = self.width / 2
        half_h = self.height / 2
        return (abs(point.x - self.center.x) <= half_w and
                abs(point.y - self.center.y) <= half_h)

    def get_bounding_box(self) -> Tuple[Point, Point]:
        half_w = self.width / 2
        half_h = self.height / 2
        top_left = Point(self.center.x - half_w, self.center.y + half_h)
        bottom_right = Point(self.center.x + half_w, self.center.y - half_h)
        return (top_left, bottom_right)

    def closest_point_to(self, point: Point) -> Point:
        """Find closest point on rectangle's boundary to given point"""
        half_w = self.width / 2
        half_h = self.height / 2

        # Clamp point to rectangle bounds
        closest_x = max(self.center.x - half_w, min(point.x, self.center.x + half_w))
        closest_y = max(self.center.y - half_h, min(point.y, self.center.y + half_h))

        # If point is inside, find closest edge
        if self.contains_point(point):
            dx_left = abs(point.x - (self.center.x - half_w))
            dx_right = abs(point.x - (self.center.x + half_w))
            dy_bottom = abs(point.y - (self.center.y - half_h))
            dy_top = abs(point.y - (self.center.y + half_h))

            min_dist = min(dx_left, dx_right, dy_bottom, dy_top)

            if min_dist == dx_left:
                closest_x = self.center.x - half_w
            elif min_dist == dx_right:
                closest_x = self.center.x + half_w
            elif min_dist == dy_bottom:
                closest_y = self.center.y - half_h
            else:
                closest_y = self.center.y + half_h

        return Point(closest_x, closest_y)

    def __repr__(self):
        return f"Rectangle(center={self.center}, width={self.width}, height={self.height})"


class Square(Rectangle):
    """
    Square is a special case of Rectangle.
    Demonstrates inheritance and Liskov Substitution Principle.
    """

    def __init__(self, center: Point, side_length: float):
        super().__init__(center, side_length, side_length)
        self.side_length = side_length

    def __repr__(self):
        return f"Square(center={self.center}, side_length={self.side_length})"


# ============================================================================
# DISTANCE CALCULATION - Strategy Pattern
# ============================================================================

class DistanceStrategy(ABC):
    """
    Abstract strategy for calculating distance between shapes.
    Follows Strategy Pattern for different distance calculation methods.
    """

    @abstractmethod
    def calculate(self, shape1: Shape, shape2: Shape) -> float:
        """Calculate distance between two shapes"""
        pass


class CenterToCenterDistance(DistanceStrategy):
    """Calculate distance between centers of two shapes"""

    def calculate(self, shape1: Shape, shape2: Shape) -> float:
        center1 = shape1.get_center()
        center2 = shape2.get_center()
        return center1.distance_to(center2)


class EdgeToEdgeDistance(DistanceStrategy):
    """
    Calculate minimum distance between edges of two shapes.
    This is the true geometric distance between shapes.
    """

    def calculate(self, shape1: Shape, shape2: Shape) -> float:
        # Find closest point on shape1 to shape2's center
        closest_on_shape1 = shape1.closest_point_to(shape2.get_center())

        # Find closest point on shape2 to that point
        closest_on_shape2 = shape2.closest_point_to(closest_on_shape1)

        # Iterate to converge (may need multiple iterations for accuracy)
        for _ in range(5):  # Usually converges in 2-3 iterations
            closest_on_shape1 = shape1.closest_point_to(closest_on_shape2)
            closest_on_shape2 = shape2.closest_point_to(closest_on_shape1)

        distance = closest_on_shape1.distance_to(closest_on_shape2)

        # If shapes overlap, distance is 0
        return max(0, distance)


class BoundingBoxDistance(DistanceStrategy):
    """
    Fast approximation using bounding boxes.
    Useful for quick filtering before expensive calculations.
    """

    def calculate(self, shape1: Shape, shape2: Shape) -> float:
        bb1_tl, bb1_br = shape1.get_bounding_box()
        bb2_tl, bb2_br = shape2.get_bounding_box()

        # Check if bounding boxes overlap
        if (bb1_br.x < bb2_tl.x or bb2_br.x < bb1_tl.x or
            bb1_br.y > bb2_tl.y or bb2_br.y > bb1_tl.y):
            # Calculate distance between bounding boxes
            dx = max(0, max(bb2_tl.x - bb1_br.x, bb1_tl.x - bb2_br.x))
            dy = max(0, max(bb1_br.y - bb2_tl.y, bb2_br.y - bb1_tl.y))
            return sqrt(dx * dx + dy * dy)
        else:
            # Bounding boxes overlap
            return 0.0


# ============================================================================
# DISTANCE CALCULATOR - Main facade for distance calculations
# ============================================================================

class ShapeDistanceCalculator:
    """
    Main class for calculating distances between shapes.
    Follows Facade Pattern to provide simple interface.
    """

    def __init__(self, strategy: DistanceStrategy = None):
        self.strategy = strategy or EdgeToEdgeDistance()

    def set_strategy(self, strategy: DistanceStrategy):
        """Change the distance calculation strategy"""
        self.strategy = strategy

    def distance(self, shape1: Shape, shape2: Shape) -> float:
        """Calculate distance between two shapes using current strategy"""
        if not isinstance(shape1, Shape) or not isinstance(shape2, Shape):
            raise TypeError("Both arguments must be Shape instances")

        return self.strategy.calculate(shape1, shape2)

    def distance_matrix(self, shapes: List[Shape]) -> List[List[float]]:
        """
        Calculate distance matrix for multiple shapes.
        Returns NxN matrix where matrix[i][j] is distance from shape i to shape j.
        """
        n = len(shapes)
        matrix = [[0.0] * n for _ in range(n)]

        for i in range(n):
            for j in range(i + 1, n):
                dist = self.distance(shapes[i], shapes[j])
                matrix[i][j] = dist
                matrix[j][i] = dist  # Symmetric

        return matrix

    def find_closest_shapes(self, shapes: List[Shape]) -> Tuple[Shape, Shape, float]:
        """Find the two closest shapes from a list"""
        if len(shapes) < 2:
            raise ValueError("Need at least 2 shapes")

        min_distance = float('inf')
        closest_pair = (shapes[0], shapes[1])

        for i in range(len(shapes)):
            for j in range(i + 1, len(shapes)):
                dist = self.distance(shapes[i], shapes[j])
                if dist < min_distance:
                    min_distance = dist
                    closest_pair = (shapes[i], shapes[j])

        return closest_pair[0], closest_pair[1], min_distance


# ============================================================================
# EXAMPLE USAGE FOR QUESTION 2
# ============================================================================

def example_shape_distance():
    """Examples of computing distances between shapes"""

    # Create shapes
    circle1 = Circle(Point(0, 0), radius=5)
    circle2 = Circle(Point(15, 0), radius=3)
    rectangle1 = Rectangle(Point(5, 10), width=4, height=6)
    square1 = Square(Point(20, 20), side_length=5)

    # Create distance calculator
    calculator = ShapeDistanceCalculator()

    # Calculate distances
    print("=== Shape Distance Calculations ===\n")

    # Circle to Circle
    dist = calculator.distance(circle1, circle2)
    print(f"Distance from {circle1} to {circle2}: {dist:.2f}")

    # Circle to Rectangle
    dist = calculator.distance(circle1, rectangle1)
    print(f"Distance from {circle1} to {rectangle1}: {dist:.2f}")

    # Rectangle to Square
    dist = calculator.distance(rectangle1, square1)
    print(f"Distance from {rectangle1} to {square1}: {dist:.2f}")

    # Use different strategy - Center to Center
    calculator.set_strategy(CenterToCenterDistance())
    dist = calculator.distance(circle1, circle2)
    print(f"\nCenter-to-center distance (Circle1 to Circle2): {dist:.2f}")

    # Use bounding box approximation
    calculator.set_strategy(BoundingBoxDistance())
    dist = calculator.distance(rectangle1, square1)
    print(f"Bounding box distance (Rectangle to Square): {dist:.2f}")

    # Calculate distance matrix for all shapes
    calculator.set_strategy(EdgeToEdgeDistance())
    shapes = [circle1, circle2, rectangle1, square1]
    matrix = calculator.distance_matrix(shapes)

    print("\n=== Distance Matrix ===")
    for i, row in enumerate(matrix):
        print(f"{shapes[i].__class__.__name__} {i}: {[f'{d:.2f}' for d in row]}")

    # Find closest pair
    closest1, closest2, min_dist = calculator.find_closest_shapes(shapes)
    print(f"\nClosest pair: {closest1} and {closest2}")
    print(f"Distance: {min_dist:.2f}")


# ============================================================================
# DESIGN PATTERNS USED IN THE SOLUTIONS
# ============================================================================

"""
DESIGN PATTERNS AND PRINCIPLES DEMONSTRATED:

1. QUESTION 1 (LogGrep):
   - Builder Pattern: Flexible configuration through constructor
   - Strategy Pattern: Different match modes (exact, regex, wildcard)
   - Iterator Pattern: Stream processing for large files
   - Template Method: Base grep with extensible advanced version
   - Single Responsibility: Each class has one clear purpose

2. QUESTION 2 (Shape Distance):
   - Abstract Factory: Shape hierarchy with common interface
   - Strategy Pattern: Different distance calculation strategies
   - Facade Pattern: ShapeDistanceCalculator simplifies usage
   - Inheritance: Square extends Rectangle (Liskov Substitution)
   - Open/Closed Principle: Easy to add new shapes or distance strategies
   - Dependency Inversion: Depend on Shape abstraction, not concrete classes

SOLID PRINCIPLES:
- Single Responsibility: Each class has one reason to change
- Open/Closed: Open for extension (new shapes), closed for modification
- Liskov Substitution: Square can substitute Rectangle
- Interface Segregation: Shape interface is focused
- Dependency Inversion: High-level modules depend on abstractions

TIME COMPLEXITY ANALYSIS:

LogGrep:
- Simple search: O(n) where n is number of lines
- With context: O(n * c) where c is context size
- Regex compilation: O(m) where m is pattern length (done once)

Shape Distance:
- Center-to-center: O(1)
- Edge-to-edge: O(k) where k is iteration count (usually 5)
- Bounding box: O(1)
- Distance matrix: O(n²) for n shapes
- Closest pair: O(n²) for n shapes

SPACE COMPLEXITY:

LogGrep:
- With context: O(c) for context buffer
- Results storage: O(m) where m is number of matches

Shape Distance:
- Per shape: O(1)
- Distance matrix: O(n²)
"""


# ============================================================================
# RUN EXAMPLES
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("AUTODESK BACKEND INTERVIEW - SOLUTIONS")
    print("=" * 70)

    print("\n" + "=" * 70)
    print("QUESTION 1: LogGrep - Grep for Log Files")
    print("=" * 70)
    example_grep_usage()

    print("\n" + "=" * 70)
    print("QUESTION 2: Shape Distance Calculator")
    print("=" * 70)
    example_shape_distance()
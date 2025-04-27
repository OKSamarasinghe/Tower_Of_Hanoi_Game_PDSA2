import unittest
from hanoi_algorithms import recursive_hanoi, iterative_hanoi, frame_stewart, calculate_min_moves
import sys

class TestHanoiAlgorithms(unittest.TestCase):
    """Test cases for Tower of Hanoi algorithms"""
    
    def setUp(self):
        # Print the name of the test being run
        print(f"\n{self._testMethodName}: {self._testMethodDoc}")
    
    def test_recursive_3_disks(self):
        """Test recursive algorithm with 3 disks"""
        expected = [
            ('A', 'C'), ('A', 'B'), ('C', 'B'),
            ('A', 'C'), ('B', 'A'), ('B', 'C'), ('A', 'C')
        ]
        result = recursive_hanoi(3, 'A', 'C', 'B')
        print(f"Expected moves: {expected}")
        print(f"Actual moves: {result}")
        self.assertEqual(result, expected)
        self.assertEqual(len(result), 7)  # 2^3 - 1 = 7
        print("✓ Test passed!")

    def test_recursive_0_disk(self):
        """Test recursive algorithm with 0 disks (edge case)"""
        result = recursive_hanoi(0, 'A', 'C', 'B')
        print(f"Result: {result}")
        self.assertEqual(result, [])
        print("✓ Test passed!")

    def test_recursive_1_disk(self):
        """Test recursive algorithm with 1 disk"""
        result = recursive_hanoi(1, 'A', 'C', 'B')
        print(f"Result: {result}")
        self.assertEqual(result, [('A', 'C')])
        print("✓ Test passed!")

    def test_recursive_larger_disks(self):
        """Test recursive algorithm with larger disk count"""
        # For n=4, should have 2^4 - 1 = 15 moves
        moves = recursive_hanoi(4, 'A', 'C', 'B')
        print(f"Number of moves for 4 disks: {len(moves)}")
        print(f"First move: {moves[0]}, Last move: {moves[-1]}")
        self.assertEqual(len(moves), 15)
        
        # Verify first and last moves based on the actual implementation
        self.assertEqual(moves[0], ('A', 'B'))
        self.assertEqual(moves[-1], ('B', 'C'))
        print("✓ Test passed!")

    def test_iterative_3_disks(self):
        """Test iterative algorithm with 3 disks"""
        moves = iterative_hanoi(3, 'A', 'C', 'B')
        print(f"Number of moves for 3 disks (iterative): {len(moves)}")
        print(f"Moves: {moves}")
        self.assertEqual(len(moves), 7)  # 2^3 - 1 = 7
        self.assertTrue(all(isinstance(move, tuple) and len(move) == 2 for move in moves))
        print("✓ Test passed!")

    def test_iterative_4_disks(self):
        """Test iterative algorithm with 4 disks"""
        moves = iterative_hanoi(4, 'A', 'C', 'B')
        print(f"Number of moves for 4 disks (iterative): {len(moves)}")
        self.assertEqual(len(moves), 15)  # 2^4 - 1 = 15
        print("✓ Test passed!")

    def test_iterative_edge_cases(self):
        """Test iterative algorithm with edge cases"""
        moves_0 = iterative_hanoi(0, 'A', 'C', 'B')
        moves_1 = iterative_hanoi(1, 'A', 'C', 'B')
        print(f"0 disks moves: {moves_0}")
        print(f"1 disk moves: {moves_1}")
        self.assertEqual(len(moves_0), 0)
        self.assertEqual(len(moves_1), 1)
        print("✓ Test passed!")

    def test_recursive_iterative_equivalence(self):
        """Test that recursive and iterative solutions give same number of moves"""
        print("Testing equivalence for disks 0 to 4:")
        for n in range(5):
            recursive_moves = recursive_hanoi(n, 'A', 'C', 'B')
            iterative_moves = iterative_hanoi(n, 'A', 'C', 'B')
            print(f"  {n} disks: Recursive={len(recursive_moves)}, Iterative={len(iterative_moves)}")
            self.assertEqual(len(recursive_moves), len(iterative_moves))
        print("✓ Test passed!")

    def test_frame_stewart_3_disks(self):
        """Test Frame-Stewart algorithm with 3 disks"""
        moves = frame_stewart(3, ['A', 'B', 'C', 'D'], 'A', 'D')
        print(f"Frame-Stewart moves for 3 disks: {len(moves)}")
        print(f"Moves: {moves}")
        # For small n, Frame-Stewart might not be more efficient
        self.assertTrue(len(moves) <= 7)  # Not worse than standard algorithm
        self.assertTrue(all(isinstance(move, tuple) and len(move) == 2 for move in moves))
        print("✓ Test passed!")

    def test_frame_stewart_1_disk(self):
        """Test Frame-Stewart algorithm with 1 disk"""
        moves = frame_stewart(1, ['A', 'B', 'C', 'D'], 'A', 'D')
        print(f"Result: {moves}")
        self.assertEqual(moves, [('A', 'D')])
        print("✓ Test passed!")

    def test_frame_stewart_0_disk(self):
        """Test Frame-Stewart algorithm with 0 disks"""
        moves = frame_stewart(0, ['A', 'B', 'C', 'D'], 'A', 'D')
        print(f"Result: {moves}")
        self.assertEqual(moves, [])
        print("✓ Test passed!")

    def test_frame_stewart_efficiency(self):
        """Test Frame-Stewart algorithm efficiency for larger disk counts"""
        n = 10
        moves_3peg = recursive_hanoi(n, 'A', 'C', 'B')
        moves_4peg = frame_stewart(n, ['A', 'B', 'C', 'D'], 'A', 'D')
        print(f"For {n} disks:")
        print(f"  3-peg solution (recursive): {len(moves_3peg)} moves")
        print(f"  4-peg solution (Frame-Stewart): {len(moves_4peg)} moves")
        print(f"  Efficiency improvement: {len(moves_3peg) - len(moves_4peg)} fewer moves")
        self.assertLess(len(moves_4peg), len(moves_3peg))
        print("✓ Test passed!")

    def test_calculate_min_moves(self):
        """Test minimum move calculation"""
        # 3-peg tests
        print("Testing minimum moves calculation:")
        for n in range(1, 5):
            min_moves_3peg = calculate_min_moves(n, 3)
            print(f"  {n} disks, 3 pegs: {min_moves_3peg} moves")
            self.assertEqual(min_moves_3peg, 2**n - 1)
        
        # 4-peg tests
        for n in range(1, 5):
            min_moves_4peg = calculate_min_moves(n, 4)
            print(f"  {n} disks, 4 pegs: {min_moves_4peg} moves")
        
        # Verify 4-peg more efficient for larger n
        n = 10
        min_3peg = calculate_min_moves(n, 3)
        min_4peg = calculate_min_moves(n, 4)
        print(f"  {n} disks: 3-peg={min_3peg}, 4-peg={min_4peg}, Savings={min_3peg - min_4peg}")
        self.assertTrue(min_4peg < min_3peg)
        
        # Edge case
        print("  Testing invalid peg count (expecting ValueError)")
        with self.assertRaises(ValueError):
            calculate_min_moves(3, 5)  # Only 3 or 4 pegs supported
        print("✓ Test passed!")

    def test_valid_moves(self):
        """Test that all moves are valid according to Tower of Hanoi rules"""
        def is_valid_sequence(moves, n):
            """Check if a sequence of moves is valid"""
            # Initialize pegs
            pegs = {'A': list(range(n, 0, -1)), 'B': [], 'C': []}
            
            for source, target in moves:
                # Check if source peg has disks
                if not pegs[source]:
                    return False
                    
                # Check if move follows the rule (smaller on larger)
                if pegs[target] and pegs[source][-1] > pegs[target][-1]:
                    return False
                    
                # Make the move
                pegs[target].append(pegs[source].pop())
                
            # Check final state - all disks should be on target peg
            return len(pegs['C']) == n and not pegs['A'] and not pegs['B']
        
        # Test recursive algorithm moves
        recursive_moves = recursive_hanoi(3, 'A', 'C', 'B')
        recursive_valid = is_valid_sequence(recursive_moves, 3)
        print(f"Recursive algorithm produces valid moves: {recursive_valid}")
        self.assertTrue(recursive_valid)
        
        # Test iterative algorithm moves
        iterative_moves = iterative_hanoi(3, 'A', 'C', 'B')
        iterative_valid = is_valid_sequence(iterative_moves, 3)
        print(f"Iterative algorithm produces valid moves: {iterative_valid}")
        self.assertTrue(iterative_valid)
        print("✓ Test passed!")


def get_test_runner():
    """Return a test runner with verbose output"""
    return unittest.TextTestRunner(verbosity=2, stream=sys.stdout)


if __name__ == '__main__':
    print("=" * 70)
    print("TOWER OF HANOI ALGORITHM TESTS")
    print("=" * 70)
    
    # Create a test suite with all tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestHanoiAlgorithms)
    
    # Run the tests with custom runner
    result = get_test_runner().run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print(f"SUMMARY: Ran {result.testsRun} tests")
    print(f"  Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print("=" * 70)
    
    # Exit with appropriate code
    sys.exit(not result.wasSuccessful())
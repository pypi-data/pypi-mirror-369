#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath('..'))

from klotho.tonos.systems.combination_product_sets import Hexany, Eikosany, match_pattern

def test_hexany_triangles():
    """Test triangle matching in Hexany"""
    print("Testing Hexany triangle matching...")
    hx = Hexany()
    result = match_pattern(hx, [0, 2, 5])
    
    expected = {(0, 2, 3), (0, 3, 4), (1, 2, 5), (1, 3, 4), (1, 4, 5)}
    actual = {tuple(sorted(match)) for match in result}
    
    print(f"Expected: {sorted(expected)}")
    print(f"Actual:   {sorted(actual)}")
    
    if actual == expected:
        print("✅ PASS: Hexany triangle test")
        return True
    else:
        print("❌ FAIL: Hexany triangle test")
        missing = expected - actual
        extra = actual - expected
        if missing:
            print(f"Missing: {sorted(missing)}")
        if extra:
            print(f"Extra: {sorted(extra)}")
        return False

def test_eikosany_hexagon():
    """Test hexagon matching in Eikosany"""
    print("\nTesting Eikosany hexagon matching...")
    ek = Eikosany(master_set='asterisk')
    result = match_pattern(ek, [11, 6, 10, 15, 18, 8])
    
    expected = {
        (0, 1, 4, 5, 10, 15), (0, 2, 4, 7, 15, 18), (0, 4, 7, 9, 12, 16), 
        (0, 6, 10, 12, 14, 15), (1, 3, 6, 10, 11, 13), (2, 3, 7, 9, 13, 19), 
        (4, 5, 7, 9, 17, 19), (6, 11, 13, 14, 17, 19), (8, 9, 11, 13, 16, 19)
    }
    actual = {tuple(sorted(match)) for match in result}
    
    print(f"Expected: {sorted(expected)}")
    print(f"Actual:   {sorted(actual)}")
    
    if actual == expected:
        print("✅ PASS: Eikosany hexagon test")
        return True
    else:
        print("❌ FAIL: Eikosany hexagon test")
        missing = expected - actual
        extra = actual - expected
        if missing:
            print(f"Missing: {sorted(missing)}")
        if extra:
            print(f"Extra: {sorted(extra)}")
        return False

def test_eikosany_t_shape():
    """Test slanted T-shape matching in Eikosany"""
    print("\nTesting Eikosany T-shape matching...")
    ek = Eikosany(master_set='asterisk')
    result = match_pattern(ek, [11, 6, 10, 14])
    
    expected = {
        tuple(sorted([10, 6, 15, 1])), tuple(sorted([15, 10, 0, 18])), 
        tuple(sorted([0, 15, 4, 12])), tuple(sorted([4, 0, 7, 5])), 
        tuple(sorted([7, 4, 9, 2])), tuple(sorted([9, 7, 19, 16])), 
        tuple(sorted([19, 9, 13, 17])), tuple(sorted([13, 19, 11, 3])), 
        tuple(sorted([11, 13, 6, 8]))
    }
    actual = {tuple(sorted(match)) for match in result}
    
    print(f"Expected: {sorted(expected)}")
    print(f"Actual:   {sorted(actual)}")
    
    if actual == expected:
        print("✅ PASS: Eikosany T-shape test")
        return True
    else:
        print("❌ FAIL: Eikosany T-shape test")
        missing = expected - actual
        extra = actual - expected
        if missing:
            print(f"Missing: {sorted(missing)}")
        if extra:
            print(f"Extra: {sorted(extra)}")
        return False

def main():
    print("Running match_pattern tests...\n")
    
    test1_passed = test_hexany_triangles()
    test2_passed = test_eikosany_hexagon()
    test3_passed = test_eikosany_t_shape()
    
    print(f"\nSummary:")
    print(f"Hexany test: {'PASS' if test1_passed else 'FAIL'}")
    print(f"Eikosany hexagon test: {'PASS' if test2_passed else 'FAIL'}")
    print(f"Eikosany T-shape test: {'PASS' if test3_passed else 'FAIL'}")
    
    if test1_passed and test2_passed and test3_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n💥 Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())

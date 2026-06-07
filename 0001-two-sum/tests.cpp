#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#include "../lib/doctest.h"
#include "solution.cpp"

TEST_CASE("two sum"){
  Solution sol;
  vector<int> nums{2,7,11,15};
  CHECK(sol.twoSum(nums,9) == vector<int>{0,1});
  vector<int> b{3,2,4};
  CHECK(sol.twoSum(b,6) == vector<int>{1,2});
  vector<int> c{3,3};
  CHECK(sol.twoSum(c,6) == vector<int>{0,1});
}
TEST_CASE("two sum - edge cases"){
  Solution sol;
  vector<int> d{-1,-2,-3,-4};
  CHECK(sol.twoSum(d,-7) == vector<int>{2,3});
}

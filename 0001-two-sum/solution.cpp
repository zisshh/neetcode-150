// 1. Two Sum
// https://leetcode.com/problems/two-sum/
//
// Solve it yourself. Run:  ./run 0001-two-sum

#pragma once
#include <algorithm>
#include <climits>
#include <cmath>
#include <functional>
#include <map>
#include <numeric>
#include <queue>
#include <set>
#include <stack>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>
using namespace std;

class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        unordered_map<int,int> mp;
        for(int i=0;i<nums.size();i++){
          int complement=target-nums[i];
          if(mp.count(complement)){
            return {mp[complement],i};
          }
          mp[nums[i]]=i;
        }
        return {};
    }
};

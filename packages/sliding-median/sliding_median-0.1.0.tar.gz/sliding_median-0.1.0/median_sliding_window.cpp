#define PY_SSIZE_T_CLEAN
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <queue>
#include <vector>
#include <utility>

using namespace std;
namespace py = pybind11;

class Solution {
public:
    // 小顶堆比较器（用于存储较大的一半元素）
    struct cmp{
        bool operator()(const pair<double, int>& a, const pair<double, int>& b) const{
            if(a.first != b.first) return a.first > b.first; // 按数值升序
            return a.second > b.second; // 数值相同时按索引升序（旧元素优先出队）
        }
    };
    
    // 接收double类型的输入（支持整数和浮点数）
    vector<double> medianSlidingWindow(vector<double>& nums, int k) {
        int n = nums.size();
        // 大顶堆（存储较小的一半元素）：元素类型为pair<double, int>
        priority_queue<pair<double, int>> front; 
        // 小顶堆（存储较大的一半元素）：容器类型与元素类型一致（均为pair<double, int>）
        priority_queue<pair<double, int>, vector<pair<double, int>>, cmp> back; 
        int right = -1;
        
        // 初始化窗口
        while(right < k - 1){
            right++;
            back.push(make_pair(nums[right], right));
        }
        
        // 平衡两个堆
        vector<int> pos(n, 0); // 标记元素所在堆（1表示在front堆）
        for(int i = 0; i < static_cast<int>(k/2); i++){ // 修复类型转换警告
            pos[back.top().second] = 1;
            front.push(back.top());
            back.pop();
        }
        
        vector<double> result;
        // 计算第一个窗口的中位数
        if(k & 1){
            result.push_back(back.top().first);
        } else{
            result.push_back((back.top().first + front.top().first) / 2.0);
        }
        
        // 滑动窗口处理剩余元素
        while(right < n - 1){
            right++;
            if(nums[right] >= back.top().first){
                back.push(make_pair(nums[right], right));
                while(back.top().second <= right - k) back.pop();
                if(pos[right - k]){
                    pos[back.top().second] = 1;
                    front.push(back.top());
                    back.pop();
                }
            } else{
                front.push(make_pair(nums[right], right));
                pos[right] = 1;
                while(front.top().second <= right - k) front.pop();
                if(!pos[right - k]){
                    pos[front.top().second] = 0;
                    back.push(front.top());
                    front.pop();
                }
            }
            
            // 清理过期元素
            while(!front.empty() && front.top().second <= right - k) front.pop();
            while(back.top().second <= right - k) back.pop();
            
            // 计算当前窗口中位数
            if(k & 1){
                result.push_back(back.top().first);
            } else{
                result.push_back((back.top().first + front.top().first) / 2.0);
            }
        }
        
        return result;
    }
};

// 绑定到Python
PYBIND11_MODULE(sliding_median, m) {
    m.doc() = "Sliding window median with float support";
    py::class_<Solution>(m, "Solution")
        .def(py::init<>())
        .def("median_sliding_window", &Solution::medianSlidingWindow,
             py::arg("nums"), py::arg("k"));
}
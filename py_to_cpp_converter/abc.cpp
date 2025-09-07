#include <iostream>
#include <vector>
#include <string>
using namespace std;

int main() {
    int a = 10;
    int b = 20;
    int c = (a + b);
    cout << "Sum is" << c << endl;
    if ((c > 25)) {
        cout << "Value is large" << endl;
    } else {
        cout << "Value is small" << endl;
        int i = 0;
        while ((i < 3)) {
            cout << "While loop index:" << i << endl;
            i = (i + 1);
            for (int j = 0; j < 5; j++) {
                cout << "Range loop value:" << j << endl;
                vector<int> numbers = std::vector<int>{5, 15, 25};
                for (auto n : numbers) {
                    cout << "List item:" << n << endl;
                    int total = ((c + i) + j);
                    cout << "Final total is" << total << endl;
                }
            }
        }
    }
    return 0;
}
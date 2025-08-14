"""
Example code snippets for agents to optimize
"""

EXAMPLE_CODES = {
    "fibonacci": """
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

def calculate_fibonacci_sum(limit):
    total = 0
    for i in range(limit):
        total = total + fibonacci(i)
    return total

result = calculate_fibonacci_sum(20)
print(result)
""",

    "data_processing": """
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    
    sum_value = 0
    for value in result:
        sum_value = sum_value + value
    
    average = sum_value / len(result) if result else 0
    
    filtered = []
    for x in result:
        if x > average:
            filtered.append(x)
    
    return filtered

def find_duplicates(list1, list2):
    duplicates = []
    for item1 in list1:
        for item2 in list2:
            if item1 == item2:
                if item1 not in duplicates:
                    duplicates.append(item1)
    return duplicates

data = list(range(100))
processed = process_data(data)
""",

    "string_operations": """
def reverse_string(s):
    result = ""
    for i in range(len(s) - 1, -1, -1):
        result = result + s[i]
    return result

def count_vowels(text):
    count = 0
    vowels = ['a', 'e', 'i', 'o', 'u']
    for char in text.lower():
        if char in vowels:
            count = count + 1
    return count

def remove_duplicates(text):
    seen = []
    result = ""
    for char in text:
        if char not in seen:
            result = result + char
            seen.append(char)
    return result

def is_palindrome(s):
    cleaned = ""
    for char in s.lower():
        if char.isalnum():
            cleaned = cleaned + char
    
    reversed_str = reverse_string(cleaned)
    
    if cleaned == reversed_str:
        return True
    else:
        return False

test_string = "Hello World! This is a test string for optimization."
reversed_result = reverse_string(test_string)
vowel_count = count_vowels(test_string)
unique_chars = remove_duplicates(test_string)
""",

    "sorting_searching": """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                temp = arr[j]
                arr[j] = arr[j + 1]
                arr[j + 1] = temp
    return arr

def linear_search(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1

def find_min_max(numbers):
    if not numbers:
        return None, None
    
    min_val = numbers[0]
    max_val = numbers[0]
    
    for num in numbers:
        if num < min_val:
            min_val = num
        if num > max_val:
            max_val = num
    
    return min_val, max_val

numbers = [64, 34, 25, 12, 22, 11, 90, 88, 45, 23, 67, 89]
sorted_numbers = bubble_sort(numbers.copy())
index = linear_search(sorted_numbers, 45)
min_num, max_num = find_min_max(numbers)
""",

    "class_based": """
class DataContainer:
    def __init__(self):
        self.data = []
    
    def add_item(self, item):
        self.data.append(item)
    
    def remove_item(self, item):
        new_data = []
        for i in self.data:
            if i != item:
                new_data.append(i)
        self.data = new_data
    
    def get_size(self):
        count = 0
        for item in self.data:
            count = count + 1
        return count
    
    def contains(self, item):
        for i in self.data:
            if i == item:
                return True
        return False
    
    def get_all_items(self):
        result = []
        for item in self.data:
            result.append(item)
        return result

class Calculator:
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b
    
    def multiply(self, a, b):
        result = 0
        for i in range(b):
            result = result + a
        return result
    
    def divide(self, a, b):
        if b == 0:
            return None
        return a / b

container = DataContainer()
for i in range(10):
    container.add_item(i * 2)
""",

    "file_processing": """
def read_file_lines(filename):
    lines = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                lines.append(line.strip())
    except:
        pass
    return lines

def count_words(text):
    words = text.split()
    count = 0
    for word in words:
        count = count + 1
    return count

def find_longest_word(text):
    words = text.split()
    longest = ""
    for word in words:
        if len(word) > len(longest):
            longest = word
    return longest

def process_csv_data(csv_string):
    rows = []
    lines = csv_string.split('\\n')
    for line in lines:
        if line:
            columns = []
            values = line.split(',')
            for value in values:
                columns.append(value.strip())
            rows.append(columns)
    return rows

sample_text = "The quick brown fox jumps over the lazy dog"
word_count = count_words(sample_text)
longest = find_longest_word(sample_text)

csv_data = "name,age,city\\nJohn,30,NYC\\nJane,25,LA"
parsed_csv = process_csv_data(csv_data)
"""
}

TEST_SUITES = {
    "fibonacci": """
# Test fibonacci function
assert fibonacci(0) == 0
assert fibonacci(1) == 1
assert fibonacci(5) == 5
assert fibonacci(10) == 55
""",

    "data_processing": """
# Test data processing
test_data = [1, 2, 3, 4, 5, -1, -2]
result = process_data(test_data)
assert len(result) > 0

# Test duplicate finder
list1 = [1, 2, 3, 4]
list2 = [3, 4, 5, 6]
dups = find_duplicates(list1, list2)
assert 3 in dups
assert 4 in dups
""",

    "string_operations": """
# Test string operations
assert reverse_string("hello") == "olleh"
assert count_vowels("hello") == 2
assert is_palindrome("racecar") == True
assert is_palindrome("hello") == False
""",

    "sorting_searching": """
# Test sorting and searching
test_arr = [5, 2, 8, 1, 9]
sorted_arr = bubble_sort(test_arr.copy())
assert sorted_arr == [1, 2, 5, 8, 9]
assert linear_search(sorted_arr, 5) == 2
assert linear_search(sorted_arr, 10) == -1
""",

    "class_based": """
# Test DataContainer
container = DataContainer()
container.add_item(1)
container.add_item(2)
assert container.get_size() == 2
assert container.contains(1) == True
assert container.contains(3) == False

# Test Calculator
calc = Calculator()
assert calc.add(2, 3) == 5
assert calc.multiply(3, 4) == 12
""",

    "file_processing": """
# Test file processing functions
assert count_words("hello world") == 2
assert find_longest_word("the quick brown fox") == "quick"

csv_test = "a,b\\n1,2"
result = process_csv_data(csv_test)
assert len(result) == 2
assert result[0] == ['a', 'b']
"""
}
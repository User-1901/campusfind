# Searching Algorithms & Complexity Analysis

## 1. Classical Searching Paradigm

A searching algorithm is a systematic procedure to determine whether a given target key exists within a collection of data, returning its location or associated metadata if present.

In **CampusFind**, searching is applied to the vocabulary extracted by the inverted indexing engine to locate documents containing specific campus terms.

---

## 2. Linear Search (Sequential Search)

### 2.1 Definition & Mechanism
Linear Search is a straightforward searching algorithm that sequentially inspects each element in an array from index $0$ to index $n-1$.

### 2.2 Algorithm Logic (Python)
```python
def linear_search(vocabulary: list[str], target: str) -> tuple[int, int]:
    """
    Sequentially searches for target in vocabulary.
    Returns: (index, total_comparisons)
    """
    comparisons = 0
    clean_target = target.lower()

    for i in range(len(vocabulary)):
        comparisons += 1
        if vocabulary[i].lower() == clean_target:
            return i, comparisons  # Target located

    return -1, comparisons         # Target absent
```

### 2.3 Complexity Derivation
- **Best-Case Complexity — $\mathcal{O}(1)$:**  
  The target resides at index $0$. The algorithm performs exactly $1$ comparison and halts.
- **Worst-Case Complexity — $\mathcal{O}(n)$:**  
  The target resides at index $n-1$ or does not exist in the collection. All $n$ items are checked.
- **Average-Case Complexity — $\mathcal{O}(n)$:**  
  Assuming uniform probability across all $n$ positions:
  $$\text{Expected Comparisons} = \frac{1}{n} \sum_{i=1}^{n} i = \frac{n(n + 1)}{2n} = \frac{n + 1}{2} \approx \frac{n}{2} \in \mathcal{O}(n)$$
- **Auxiliary Space Complexity — $\mathcal{O}(1)$:**  
  Only scalar loop index and comparison counter variables are allocated in memory.

### 2.4 Advantages & Disadvantages
- **Advantages:** Works on unsorted data; works on linear data structures (e.g. linked lists) without random access; zero preprocessing overhead.
- **Disadvantages:** Scales linearly; performance degrades noticeably as vocabulary expands into tens of thousands of terms.

---

## 3. Binary Search (Divide and Conquer)

### 3.1 Definition & Mechanism
Binary Search is an optimal searching algorithm that operates on **sorted** collections by repeatedly bisecting the search interval in half.

### 3.2 The Strict Sorted Data Invariant
> **Mathematical Invariant:**  
> When Binary Search compares $\text{target}$ with $\text{data}[\text{mid}]$:  
> - If $\text{target} < \text{data}[\text{mid}]$, it prunes the entire upper partition $[\text{mid} \dots \text{right}]$.  
> - This pruning is **mathematically sound if and only if** all items with index $> \text{mid}$ are guaranteed to be greater than or equal to $\text{data}[\text{mid}]$.  
> - In an unsorted array, smaller items could reside in the pruned partition. Pruning causes Binary Search to discard valid elements, resulting in false negatives.

### 3.3 Algorithm Logic (Python)
```python
def binary_search(sorted_vocabulary: list[str], target: str) -> tuple[int, int]:
    """
    Searches for target in a SORTED vocabulary using iterative Binary Search.
    Returns: (index, total_comparisons)
    """
    left = 0
    right = len(sorted_vocabulary) - 1
    comparisons = 0
    clean_target = target.lower()

    while left <= right:
        # Midpoint calculation preventing integer overflow
        mid = left + (right - left) // 2
        comparisons += 1
        current = sorted_vocabulary[mid].lower()

        if current == clean_target:
            return mid, comparisons
        elif clean_target < current:
            right = mid - 1
        else:
            left = mid + 1

    return -1, comparisons
```

### 3.4 Complexity Derivation & Recurrence
At each step, Binary Search performs $\mathcal{O}(1)$ work (calculating `mid` and comparing keys) and reduces problem size $n$ to $n/2$:
$$T(n) = T\left(\frac{n}{2}\right) + \mathcal{O}(1)$$

By the **Master Theorem** ($a = 1, b = 2, f(n) = \mathcal{O}(1) = \mathcal{O}(n^{\log_2 1}) = \mathcal{O}(n^0)$):
$$T(n) = \mathcal{O}(\log_2 n)$$

- **Best-Case Complexity — $\mathcal{O}(1)$:** Target key matches the initial midpoint element.
- **Worst-Case Complexity — $\mathcal{O}(\log_2 n)$:** Target is found at the leaf level or is absent. Maximum comparisons:
  $$\text{Max Comparisons} = \lfloor \log_2 n \rfloor + 1$$
- **Average-Case Complexity — $\mathcal{O}(\log_2 n)$:** The expected number of comparisons is $\approx \log_2 n - 1$.
- **Auxiliary Space Complexity — $\mathcal{O}(1)$ (Iterative):** Constant space for pointers (`left`, `right`, `mid`).

---

## 4. Detailed Side-by-Side Comparison

| Parameter | Linear Search | Binary Search |
| :--- | :--- | :--- |
| **Data Requirement** | Unsorted or Sorted | **Strictly Sorted Order Required** |
| **Core Paradigm** | Brute-force Sequential Scan | Divide and Conquer |
| **Best-Case Time** | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ |
| **Average-Case Time** | $\mathcal{O}(n)$ | $\mathcal{O}(\log_2 n)$ |
| **Worst-Case Time** | $\mathcal{O}(n)$ | $\mathcal{O}(\log_2 n)$ |
| **Space Complexity** | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ iterative |
| **Hardware Random Access** | Not required (works on streams/linked lists) | **Required** ($\mathcal{O}(1)$ indexing by array position) |
| **Comparisons for $N = 1,000$** | Up to $1,000$ comparisons | At most $10$ comparisons |
| **Comparisons for $N = 10,000$** | Up to $10,000$ comparisons | At most $14$ comparisons |

---

## 5. Walkthrough Dry-Run Example

**Sorted Array:** `[10, 20, 30, 40, 50, 60, 70]` ($N = 7$)  
**Target:** `50`

### Binary Search Trace:
1. **Initial:** $\text{left} = 0, \text{right} = 6$.
2. **Iteration 1:**
   - $\text{mid} = 0 + (6 - 0) // 2 = 3$.
   - $\text{Value} = \text{data}[3] = 40$.
   - Is $50 == 40$? No. Is $50 > 40$? Yes.
   - Action: Prune left partition $[\text{left} \dots \text{mid}]$. Update $\text{left} = \text{mid} + 1 = 4$.
3. **Iteration 2:**
   - $\text{left} = 4, \text{right} = 6$.
   - $\text{mid} = 4 + (6 - 4) // 2 = 5$.
   - $\text{Value} = \text{data}[5] = 60$.
   - Is $50 == 60$? No. Is $50 < 60$? Yes.
   - Action: Prune right partition $[\text{mid} \dots \text{right}]$. Update $\text{right} = \text{mid} - 1 = 4$.
4. **Iteration 3:**
   - $\text{left} = 4, \text{right} = 4$.
   - $\text{mid} = 4 + (4 - 4) // 2 = 4$.
   - $\text{Value} = \text{data}[4] = 50$.
   - Is $50 == 50$? **YES! Target Found at index 4.**
   - Total Comparisons: **3**

### Linear Search Trace (Same Target `50`):
- Step 1: Check index 0 (`10` == `50`) $\to$ Mismatch.
- Step 2: Check index 1 (`20` == `50`) $\to$ Mismatch.
- Step 3: Check index 2 (`30` == `50`) $\to$ Mismatch.
- Step 4: Check index 3 (`40` == `50`) $\to$ Mismatch.
- Step 5: Check index 4 (`50` == `50`) $\to$ **Match Found!**
- Total Comparisons: **5**

---

## 6. Engineering Realities: Is Binary Search Always Faster?

**No.** Software engineers must account for practical system factors:
1. **The Cost of Sorting:** Sorting an unsorted array takes $\mathcal{O}(n \log n)$ time. If an unsorted dataset is only searched **once**, Linear Search takes $\mathcal{O}(n)$ time, which is strictly faster than sorting followed by binary search:
   $$\mathcal{O}(n) < \mathcal{O}(n \log n + \log n)$$
2. **Small Dataset Overhead:** For very small lists ($N < 20$), Linear Search is frequently faster in wall-clock execution because it avoids pointer arithmetic and takes advantage of contiguous CPU cache prefetching.
3. **When Binary Search is Superior:** When an inverted index is queried repeatedly across thousands of user requests. The $\mathcal{O}(V \log V)$ sorting cost is paid once during offline ingestion, after which every search completes in microsecond logarithmic time.


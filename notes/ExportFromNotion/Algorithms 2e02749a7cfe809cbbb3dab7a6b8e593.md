# Algorithms

```csharp
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;

public static class MainClass
{
    public static bool IsAlphaNumeric(char c) => (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9');
    public static void Main(string[] args)
    {
    label:
        Console.Write("Input :");
        var input = Console.ReadLine();
        //Console.WriteLine(BracketMatchingUsingStack(input));
        //Console.WriteLine(ReverseEachWordInSentance(input));
        //Console.WriteLine(IsPlaindrome(input));
        //WordCount(input);
        //RemoveDuplicateWords(input);
        //PascalsTriangle(Int32.Parse(input));
        //PerfectNumber(Int32.Parse(input));
        //Console.WriteLine(SquareRoot(Int32.Parse(input)));
        //Fibonacci(Int32.Parse(input));
        //ThreeDigitEvenNumbers();
        //ThreeDigitPrimeNumbers();
        //ThreeDigitUniqueEvenNumbers(Regex.Matches(input, @"\d").Select(m => int.Parse(m.Value)).ToArray());
        //GetUniquePermutations(Regex.Matches(input, @"\d").Select(m => int.Parse(m.Value)).ToArray());
        //GetUniquePermutationsString(input.ToCharArray(),2);
        //LongestCommonPrefix(input.Split(","));
        //Console.WriteLine(EveryAAppearsBeforeB(input.Split(",")[0], input.Split(",")[1]));
        //CapitalizeEachWordIfMoreThan2Letters(input);
        //BubbleSort(input.Split(",").Select(i => Convert.ToInt32(i)).ToArray());
        //QuickSortSimple(input.Split(",").Select(i => Convert.ToInt32(i)).ToArray());
        //QuickSort(input.Split(",").Select(i => Convert.ToInt32(i)).ToArray());
        //MergeSort(input.Split(",").Select(i => Convert.ToInt32(i)).ToArray());
        //BinarySearch(input.Split(",").Select(i => Convert.ToInt32(i)).ToArray());
        //ConcurrencyDemo();
        //ConcurrentOddEven();
        LinqOperationsDemo();
        goto label;
    }
    private static void LinqOperationsDemo()
    {
        Linq.Demo();
    }

```

```csharp
    public static async Task ConcurrentOddEven()
    {
        ConcurrentBag<int> odds = new ConcurrentBag<int>();
        ConcurrentBag<int> evens = new ConcurrentBag<int>();
        var numbers = Enumerable.Range(1, 100);
        await Parallel.ForEachAsync(numbers, async (i,_) =>
        {
            if (await IsOddEven(i)) evens.Add(i); else odds.Add(i);
        });
        Console.WriteLine(string.Join(", ", odds.ToArray()));
        Console.WriteLine(string.Join(", ", evens.ToArray()));

        var tasks = new List<Task<bool>>();
        var result = new ConcurrentBag<bool>();
        for (int i = 0; i < numbers.Count(); i++)
        {
            if (tasks.Count() > 3)
            {
                await Task.WhenAny(tasks);
                var completeTasks = tasks.Where(t=>t.IsCompleted).ToList();
                MergeResults(completeTasks);
                completeTasks.ForEach(t => tasks.Remove(t));
            }
            tasks.Add(IsOddEven(numbers.ElementAt(i)));
        }
        await Task.WhenAll(tasks);
        MergeResults(tasks);

        using (var semaphore = new SemaphoreSlim(3))
        {
            ConcurrentBag<bool> results = new ConcurrentBag<bool>();
            var tasksSem = new List<Task>();
            for (int i = 0; i < numbers.Count(); i++)
            {
                tasksSem.Add(Task.Run(async () =>
                    {
                        try
                        {
                            await semaphore.WaitAsync();
                            results.Add(await IsOddEven(numbers.ElementAt(i)));
                        }
                        finally
                        {
                            semaphore.Release();
                        }
                    }));
                
            }
            await Task.WhenAll(tasks);
            MergeResults(tasks);
        }

        void MergeResults(List<Task<bool>> completedTasks)
        {
            foreach (var task in completedTasks) { 
                result.Add(task.Result);
            }
        }
    }

    public static async Task<bool> IsOddEven(int n) => await Task.FromResult(n % 2 == 0);
```

```csharp
    private static void ConcurrencyDemo()
    {
        // 1. Update List<int> at particular position
        List<int> list = Enumerable.Range(0, 10).ToList();
        list[5] = 999; // Direct update
        Console.WriteLine($"1. Updated List at index 5: {string.Join(",", list)}");

        // 2. Parallel.For and Parallel.ForEach
        Console.WriteLine("\n2. Parallel Loops:");
        Parallel.For(0, 5, i => Console.Write($"For:{i} "));
        Console.WriteLine();
        Parallel.ForEach(list.Take(5), item => Console.Write($"ForEach:{item} "));
        Console.WriteLine();

        // 3. Read asynchronously (Simulated processing)
        Console.WriteLine("\n3. Read/Process Asynchronously:");
        var asyncTasks = list.Take(3).Select(async item =>
        {
            await Task.Delay(10); // Simulate async I/O
            return item * 2;
        });
        // In a real async method, use 'await Task.WhenAll'. Here we use .Result for the void Main demo.
        var results = Task.WhenAll(asyncTasks).Result;
        Console.WriteLine($"Processed Async: {string.Join(",", results)}");

        // 4. Odd/Even Parallel Processing
        Console.WriteLine("\n4. Odd/Even Parallel Processing:");
        var numbers = Enumerable.Range(1, 100).ToList();

        // 4a. With Locking (Thread Safe, Arbitrary Order)
        var evensLocked = new List<int>();
        var oddsLocked = new List<int>();
        object lockObj = new object();

        Parallel.ForEach(numbers, n =>
        {
            lock (lockObj)
            {
                if (n % 2 == 0) evensLocked.Add(n);
                else oddsLocked.Add(n);
            }
        });
        Console.WriteLine($"Locked (Safe): Evens={evensLocked.Count}, Odds={oddsLocked.Count}");

        // 4b. Without Locking (ConcurrentBag - Thread Safe, Unordered)
        var evensBag = new System.Collections.Concurrent.ConcurrentBag<int>();
        Parallel.ForEach(numbers, n =>
        {
            if (n % 2 == 0) evensBag.Add(n);
        });
        Console.WriteLine($"ConcurrentBag (Safe, Unordered): Count={evensBag.Count}");

        // 4c. Ordered (PLINQ)
        var evensOrdered = numbers.AsParallel().AsOrdered().Where(n => n % 2 == 0).ToList();
        Console.WriteLine($"PLINQ (Safe, Ordered): First={evensOrdered.First()}, Last={evensOrdered.Last()}");

        // 5. SemaphoreSlim (Throttling)
        Console.WriteLine("\n5. SemaphoreSlim (Throttling to 2):");
        using (var sem = new SemaphoreSlim(2)) // Allow only 2 threads at a time
        {
            var tasks = new List<Task>();
            for (int i = 1; i <= 5; i++)
            {
                int id = i;
                tasks.Add(Task.Run(() =>
                {
                    sem.Wait(); // Block if 2 threads are already busy
                    try { Console.WriteLine($"Task {id} entered."); Thread.Sleep(50); }
                    finally { Console.WriteLine($"Task {id} left."); sem.Release(); }
                }));
            }
            Task.WaitAll(tasks.ToArray());
        }
    }

```

```csharp
    private static void BinarySearch(int[] sortedArr)
    {
        Console.WriteLine("Enter the number to search");
        int n = Convert.ToInt32(Console.ReadLine());

        int left = 0, right = sortedArr.Length - 1;
        int found = -1;
        while (left < right)
        {
            var mid = (left + right) / 2;
            if (sortedArr[mid] == n)
            {
                found = mid;
                break;
            }
            else if (sortedArr[mid] < n)
                left = mid + 1;
            else
                right = mid - 1;
        }
        Console.WriteLine($"Found at : {found}");
    }

    private static void MergeSort(int[] arr)
    {
        if (arr == null || arr.Length == 0) return;
        int[] sorted = MergeSortRecursive(arr);
        Console.WriteLine($"[{string.Join(",", sorted)}]");
    }

    private static int[] MergeSortRecursive(int[] arr)
    {
        // Base Case: Arrays with 0 or 1 element are already sorted
        if (arr.Length <= 1) return arr;

        int mid = arr.Length / 2;
        int[] left = arr.Take(mid).ToArray();
        int[] right = arr.Skip(mid).ToArray();

        return Merge2Array(MergeSortRecursive(left), MergeSortRecursive(right));
    }

    private static int[] Merge2Array(int[] left, int[] right)
    {
        int[] result = new int[left.Length + right.Length];
        int i = 0, j = 0, k = 0;

        while (i < left.Length && j < right.Length)
        {
            if (left[i] <= right[j])
                result[k++] = left[i++];
            else
                result[k++] = right[j++];
        }
        while (i < left.Length) result[k++] = left[i++];
        while (j < right.Length) result[k++] = right[j++];
        return result;
    }
```

```csharp
    public static void QuickSortSimple(int[] arr)
    {
        // This version is easier to understand but uses more memory (not in-place).
        // We convert to a List to make adding/removing easier.
        var sorted = QuickSortSimpleRecursive(arr.ToList());
        Console.WriteLine($"[{string.Join(",", sorted)}]");
    }

    private static List<int> QuickSortSimpleRecursive(List<int> list)
    {
        // Base Case: A list with 0 or 1 element is already sorted.
        if (list.Count <= 1) return list;

        int pivot = list[list.Count / 2]; // Pick middle element as pivot
        List<int> left = new List<int>();
        List<int> equal = new List<int>();
        List<int> right = new List<int>();

        foreach (var item in list)
        {
            if (item < pivot) left.Add(item);       // Smaller goes left
            else if (item == pivot) equal.Add(item);// Equal goes middle
            else right.Add(item);                   // Larger goes right
        }

        var result = new List<int>();
        result.AddRange(QuickSortSimpleRecursive(left));
        result.AddRange(equal);
        result.AddRange(QuickSortSimpleRecursive(right));
        return result;
    }

    public static void QuickSort(int[] arr, int left, int right)
    {
        if (left >= right)
            return;
        int p = QPartition(arr, left, right);
        QuickSort(arr, left, p - 1);
        QuickSort(arr, p + 1, right);
    }

    public static int QPartition(int[] arr, int left, int right)
    {
        int pivot = (left + right) / 2;
        int pValue = arr[pivot];

        (arr[pivot], arr[right]) = (arr[right], arr[pivot]);
        int storeIdx = left;
        for (int i = left; i < right; i++)
        {
            if (arr[i] < pValue)
            {
                (arr[i], arr[storeIdx]) = (arr[storeIdx], arr[i]);
                storeIdx++;
            }
        }
        (arr[right], arr[storeIdx]) = (arr[storeIdx], arr[right]);
        return storeIdx;
    }

    public static void QuickSort(int[] arr)
    {
        if (arr == null || arr.Length == 0) return;
        QuickSort(arr, 0, arr.Length - 1);
        Console.WriteLine($"[{string.Join(",", arr)}]");
    }
```

```csharp
    private static void BubbleSort(int[] arr)
    {
        for (int i = 0; i < arr.Length - 1; i++)
        {
            for (int j = 0; j < arr.Length - 1 - i; j++)
            {
                if (arr[j] > arr[j + 1])
                {
                    //swap
                    arr[j] = arr[j] + arr[j + 1];
                    arr[j + 1] = arr[j] - arr[j + 1];
                    arr[j] = arr[j] - arr[j + 1];
                }
            }
        }
        Console.WriteLine(string.Join(',', arr));
    }

    public static void CapitalizeEachWordIfMoreThan2Letters(string input)
    {
        var strb = new StringBuilder();
        var start = 0;
        for (int i = 0; i <= input.Length; i++)
        {
            if (i == input.Length || !IsAlphaNumeric(input[i]))
            {
                if (i < input.Length)
                {
                    strb.Append(input[i]);
                    start = i + 1;
                }
                if (i > start && i - start > 2)
                {
                    strb[start] = char.ToUpper(input[start]);
                }
            }
            else
                strb.Append(char.ToLower(input[i]));
        }
        Console.WriteLine(strb.ToString());
    }
```

```csharp
    private static bool EveryAAppearsBeforeB(string input, string sequence)
    {
        /* Given a string s consisting of only the characters 'a' and 'b', return true if every 'a' appears before every 'b' in the string. Otherwise, return false.
            Example 1:

            Input: s = "aaabbb"
            Output: true
            Explanation:
            The 'a's are at indices 0, 1, and 2, while the 'b's are at indices 3, 4, and 5.
            Hence, every 'a' appears before every 'b' and we return true.
            Example 2:

            Input: s = "abab"
            Output: false
            Explanation:
            There is an 'a' at index 2 and a 'b' at index 1.
            Hence, not every 'a' appears before every 'b' and we return false.
            Example 3:

            Input: s = "bbb"
            Output: true
            Explanation:
            There are no 'a's, hence, every 'a' appears before every 'b' and we return true.
         */
        // Optimization: Map sequence characters to their indices for O(1) lookup.
        // This reduces time complexity from O(N*M) to O(N+M).
        var charRank = new Dictionary<char, int>();
        for (int i = 0; i < sequence.Length; i++)
            charRank[sequence[i]] = i; // Stores the last index if duplicates exist

        int lastRank = -1;
        for (int i = 0; i < input.Length; i++)
        {
            // Default to 0 to match original behavior (chars not in sequence are treated as rank 0)
            int currentRank = charRank.GetValueOrDefault(input[i], 0);
            if (i > 0 && lastRank > currentRank)
                return false;
            lastRank = currentRank;
        }

        return true;
    }

    private static void LongestCommonPrefix(string[] input)
    {
        if (input == null || input.Length == 0)
        {
            Console.WriteLine(string.Empty);
            return;
        }

        // Vertical Scanning: Compare column by column
        for (int i = 0; i < input[0].Length; i++)
        {
            char c = input[0][i];
            for (int j = 1; j < input.Length; j++)
            {
                // If we reach the end of any string or find a mismatch
                if (i == input[j].Length || input[j][i] != c)
                {
                    Console.WriteLine(input[0][..i]);
                    return;
                }
            }
        }
        Console.WriteLine(input[0]);
    }
    public static void GetUniquePermutations(int[] nums, int k = -1)
    {
        int targetLen = k == -1 ? nums.Length : k;

        Array.Sort(nums);
        var results = new List<List<int>>();
        BacktrackPermutations(nums, new bool[nums.Length], new List<int>(), results, targetLen);

        Console.WriteLine($"Total Unique Permutations of length {targetLen}: {results.Count}");
        foreach (var item in results)
        {
            Console.WriteLine($"[{string.Join(",", item)}]");
        }
    }
    public static void GetUniquePermutationsString(char[] nums, int k = -1)
    {
        int targetLen = k == -1 ? nums.Length : k;

        Array.Sort(nums);
        var results = new List<List<char>>();
        BacktrackPermutationsStr(nums, new bool[nums.Length], new List<char>(), results, targetLen);

        Console.WriteLine($"Total Unique Permutations of length {targetLen}: {results.Count}");
        foreach (var item in results)
        {
            Console.WriteLine($"[{string.Join(",", item)}]");
        }
    }
    private static void BacktrackPermutationsStr(char[] arr, bool[] used, List<char> current, List<List<char>> results, int targetLen)
    {
        if (current.Count == targetLen)
        {
            results.Add(new List<char>(current));
            return;
        }
        for (int i = 0; i < arr.Length; i++)
        {
            if (used[i])
                continue;

            if (i > 0 && arr[i] == arr[i - 1] && used[i - 1])
                continue;

            used[i] = true;
            current.Add(arr[i]);
            BacktrackPermutationsStr(arr, used, current, results, targetLen);

            used[i] = false;
            current.RemoveAt(current.Count - 1);
        }
    }
    private static void BacktrackPermutations(int[] nums, bool[] used, List<int> current, List<List<int>> results, int targetLen)
    {
        // BASE CASE: Stop recursion when the current permutation reaches the desired length.
        if (current.Count == targetLen)
        {
            // We must create a NEW copy (new List<int>(current)) because 'current' is passed by reference.
            // If we added 'current' directly, it would be modified by future steps, ruining the result.
            results.Add(new List<int>(current));
            return;
        }

        // RECURSIVE STEP: Try adding every available number to the current sequence.
        for (int i = 0; i < nums.Length; i++)
        {
            // CHECK 1: Is this specific index already used in the current branch?
            // If yes, we can't use it again (permutations don't reuse the exact same element instance).
            if (used[i]) continue;

            // CHECK 2: Handle Duplicates (The Tricky Part)
            // Logic: If the current number is the same as the previous number (nums[i] == nums[i-1]),
            // AND the previous number was NOT used (!used[i-1]), it means we skipped the previous copy.
            //
            // Example: nums = [1, 1, 2] (Sorted)
            // - Iteration i=0 (First '1'): used[0] is false. We pick it. Recurse.
            // - Backtrack... used[0] becomes false again.
            // - Iteration i=1 (Second '1'): used[0] is false. nums[1] == nums[0].
            //   Since the first '1' is available (not used), picking the second '1' now would start
            //   a sequence identical to the one we just finished with the first '1'.
            //   So, we SKIP to avoid generating the same permutation twice.
            if (i > 0 && nums[i] == nums[i - 1] && !used[i - 1])
                continue;

            // DO: Mark the number as used and add it to the current path.
            used[i] = true;
            current.Add(nums[i]);

            // RECURSE: Go deeper to find the next number for the sequence.
            BacktrackPermutations(nums, used, current, results, targetLen);

            // UNDO (Backtrack): Before moving to the next iteration of the loop (next 'i'),
            // we must undo our changes so the current state is clean for the next option.
            used[i] = false;
            current.RemoveAt(current.Count - 1);
        }
    }
```

```csharp
    private static void ThreeDigitUniqueEvenNumbers(params int[] arr)
    {

        /*
      * You are given an integer array digits, where each element is a digit. The array may contain duplicates.

            You need to find all the unique integers that follow the given requirements:

            The integer consists of the concatenation of three elements from digits in any arbitrary order.
            The integer does not have leading zeros.
            The integer is even.
            For example, if the given digits were [1, 2, 3], integers 132 and 312 follow the requirements.

            Return a sorted array of the unique integers.

 

            Example 1:

            Input: digits = [2,1,3,0]
            Output: [102,120,130,132,210,230,302,310,312,320]
            Explanation: All the possible integers that follow the requirements are in the output array. 
            Notice that there are no odd integers or integers with leading zeros.
            Example 2:

            Input: digits = [2,2,8,8,2]
            Output: [222,228,282,288,822,828,882]
            Explanation: The same digit can be used as many times as it appears in digits. 
            In this example, the digit 8 is used twice each time in 288, 828, and 882. 
            Example 3:

            Input: digits = [3,7,5]
            Output: []
            Explanation: No even integers can be formed using the given digits.
      */
        var count = new int[10];
        foreach (var d in arr) count[d]++;

        var result = new List<int>();
        for (int i = 100; i < 1000; i += 2)
        {
            int d1 = i / 100;
            int d2 = (i / 10) % 10;
            int d3 = i % 10;

            count[d1]--;
            count[d2]--;
            count[d3]--;

            if (count[d1] >= 0 && count[d2] >= 0 && count[d3] >= 0)
                result.Add(i);

            count[d1]++;
            count[d2]++;
            count[d3]++;
        }
        Console.WriteLine($"[{string.Join(",", result)}]");
    }

    private static void ThreeDigitPrimeNumbers()
    {
        var sb = new StringBuilder();
        // Sieve of Eratosthenes
        // 1. Create an array of 1000 booleans.
        // Default value is 'false', so initially, we assume ALL numbers are Prime.
        bool[] isComposite = new bool[1000];

        /*
        // 2. Start with the first prime number: 2.
        // We stop when i*i >= 1000 because any non-prime number X < 1000 
        // must have a factor less than or equal to sqrt(1000) (~31.6).
        
         The "Square Root" Rule
            If a number $X$ is not prime (it is "composite"), it can be broken into two factors: $a \times b = X$.

            The rule is: At least one of those factors ($a$ or $b$) must be smaller than or equal to the square root of $X$.

            Why? Imagine $X = 100$. The square root is $10$.

            If $a$ is 10, then $b$ is 10 ($10 \times 10 = 100$).
            If you make $a$ bigger (e.g., 20), $b$ must get smaller (5) to keep the total 100.
            It is impossible for both $a$ and $b$ to be larger than 10, because $11 \times 11 = 121$, which is already bigger than 100.
            2. Applying it to the Sieve
            We are looking for primes up to 1000. $\sqrt{1000} \approx 31.6$.

            This means every non-prime number up to 1000 is guaranteed to be divisible by a prime number roughly 31 or smaller (specifically 2, 3, 5, ... up to 31).
        */
        for (int i = 2; i * i < 1000; i++)
        {
            // 3. If isComposite[i] is still false, it means 'i' is a Prime Number.
            if (!isComposite[i])
            {
                // 4. Mark all multiples of 'i' as Composite (Not Prime).
                // We start at i*i because smaller multiples (like 2*i) 
                // have already been handled by previous loops.
                for (int j = i * i; j < 1000; j += i)
                    isComposite[j] = true;
            }
        }

        for (int i = 101; i < 1000; i += 2)
        {
            if (!isComposite[i])
                sb.Append(i).Append(',');
        }
        Console.Write(sb.ToString());
    }

    private static void ThreeDigitPrimeNumbers2()
    {
        var sb = new StringBuilder();
        bool isNotPrime = false;
        for (int i = 101; i < 1000; i = i + 2)
        {
            isNotPrime = false;
            for (int j = 3; j < i; j = j + 2)
            {
                if (i % j == 0)
                {
                    isNotPrime = true;
                    break;
                }
            }
            if (!isNotPrime)
                sb.Append(i + ",");
        }
        Console.Write(sb.ToString());
    }

    private static void ThreeDigitEvenNumbers()
    {
        var sb = new StringBuilder();
        for (int i = 100; i < 1000; i += 2)
        {
            sb.Append(i + ",");
        }
        Console.Write(sb.ToString());
    }
```

```csharp
    private static void Fibonacci(int n)
    {
        if (n <= 0)
        {
            Console.WriteLine();
            return;
        }

        var sb = new StringBuilder();
        int a = 0, b = 1;
        sb.Append(a);

        for (int i = 1; i < n; i++)
        {
            sb.Append(',').Append(b);
            (a, b) = (b, a + b);
        }
        Console.WriteLine(sb.ToString());

        /* - Old way
        int[] arr = new int[n];
        for (int i = 0; i < n; i++)
        {
            if (i == 0)
                arr[i] = 0;
            else if (i == 1)
                arr[i] = 1;
            else
                arr[i] = arr[i - 1] + arr[i - 2];
        }
        Console.WriteLine(string.Join(",", arr));
        */
    }
    public static double SquareRoot(double number, double tolerance = 1e-6)
    {
        if (number < 0)
        {
            throw new ArgumentException("Cannot compute square root of a negative number.");
        }

        if (number == 0) return 0;

        double root = number;

        // Newton-Raphson method: x(n+1) = 0.5 * (x(n) + S/x(n))
        while (true)
        {
            double next = 0.5 * (root + number / root);
            if (Math.Abs(root - next) < tolerance) return next;
            root = next;
        }
        /* Binaery search method
        double start = 0, mid = 0, end = number;
        while ((end - start) > tolerance)
        {
            mid = (start + end) / 2;
            if (mid * mid > number)
                end = mid;
            else
                start = mid;
        }
        return Math.Abs((end+start)/2);
        */
    }
    public static void PerfectNumber(int num)
    {
        int sum = 0;
        for (int i = 1; i < num; i++)
        {
            if (num % i == 0)
                sum += i;
        }
        if (sum == num)
            Console.WriteLine("Perfect Number");
        else
            Console.WriteLine("Not Perfect Number");
    }
    public static void PascalsTriangle(int lvl)
    {
        List<List<int>> triangle = new List<List<int>>();
        for (int i = 0; i < lvl; i++)
        {
            var currentLvl = new List<int>();
            for (int j = 0; j <= i; j++)
            {
                if (j == 0 || j == i)
                    currentLvl.Add(1);
                else
                {
                    var last = triangle[i - 1];
                    currentLvl.Add(last[j - 1] + last[j]);
                }
            }
            triangle.Add(currentLvl);
        }
        PrintTriangle(triangle);
    }
    private static void PrintTriangle(List<List<int>> triangle)
    {
        for (int i = 0; i < triangle.Count; i++)
        {
            Console.Write(new string(' ', triangle.Count - 1 - i));
            foreach (var item in triangle[i])
            {
                Console.Write(item + " ");
            }
            Console.WriteLine();
        }
    }
    public static void RemoveDuplicateWords(string input)
    {
        var strBuilder = new StringBuilder();
        int start = 0;
        HashSet<string> words = new HashSet<string>();
        for (int i = 0; i <= input.Length; i++)
        {
            if (i == input.Length || !IsAlphaNumeric(input[i]))
            {
                if (i > start)
                {
                    var word = input[start..i];
                    if (words.Add(word))
                    {
                        strBuilder.Append(word);
                    }
                }
                if (i < input.Length)
                    strBuilder.Append(input[i]);
                start = i + 1;
            }
        }
        Console.WriteLine(strBuilder.ToString());
    }
    public static void WordCount(string input)
    {
        Dictionary<string, int> words = new Dictionary<string, int>();
        char[] arr = input.ToCharArray();
        int start = 0;
        for (int i = 0; i <= input.Length; i++)
        {
            if (i == input.Length || !IsAlphaNumeric(input[i]))
            {
                /*
                 * This syntax uses the Range Operator (..), which was introduced in C# 8.0.
                    In the context of your code (var word = input[start..i];), it extracts a substring from the input string.
                    Breakdown
                    start: The index to start at (inclusive).
                    ..: The range operator.
                    i: The index to end at (exclusive).
                 */
                if (i > start)
                {
                    var word = input[start..i];// new string(input, start, i - start + 1);
                    words[word] = words.GetValueOrDefault(word) + 1;
                }
                start = i + 1;
            }
        }
        foreach (var word in words)
        {
            Console.WriteLine($"{word.Key}:{word.Value}");
        }
    }
    public static bool IsPlaindrome(string input)
    {
        for (int i = 0; i < input.Length / 2; i++)
        {
            if (input[i] != input[input.Length - 1 - i])
                return false;
        }
        return true;
    }
    public static string ReverseEachWordInSentance(string input)
    {
        char[] arr = input.ToCharArray();
        int start = 0;
        for (int i = 0; i <= arr.Length; i++)
        {
            if (i == arr.Length || !IsAlphaNumeric(arr[i]))
            {
                if (i > start)
                    ReverseWord(arr, start, i - 1);
                start = i + 1;
            }
        }
        return string.Concat(arr);

        void ReverseWord(char[] arr, int start, int end)
        {
            if (start >= end)
                return;
            for (int i = start; i <= start + (end - start) / 2; i++)
            {
                char c = arr[i];
                arr[i] = arr[start + end - i];
                arr[start + end - i] = c;
            }
        }
    }
    public static bool BracketMatchingUsingStack(string s)
    {

        Dictionary<char, char> BracketPairs = new Dictionary<char, char>
        {
            {'(', ')'},
            {'{', '}'},
            {'[', ']'}
        };

        if (s.Length % 2 != 0) return false;

        char[] stack = new char[s.Length];
        int top = -1;

        for (int i = 0; i < s.Length; i++)
        {
            char c = s[i];
            if (BracketPairs.ContainsKey(c))
            {
                stack[++top] = c;
            }
            else
            {
                if (top == -1 || BracketPairs[stack[top--]] != c)
                    return false;
            }
        }
        return top == -1;
    }
}
```
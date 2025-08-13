# exp.py

def exp(n: int):
    programs = {
        1: """package main
import "fmt"

func main() {
    fmt.Println("Hello, World!")
}""",

        2: """package main
import "fmt"

func main() {
    arr := []int{0, 1, 9, 8, 4, 0, 0, 2, 7, 0}
    pos := 0
    for _, num := range arr {
        if num != 0 {
            arr[pos] = num
            pos++
        }
    }
    for pos < len(arr) {
        arr[pos] = 0
        pos++
    }
    fmt.Println("After shifting zeros:", arr)
}""",

        3: """package main
import "fmt"

func printNames(names ...string) {
    for _, name := range names {
        fmt.Println(name)
    }
}

func main() {
    printNames("Alice", "Bob", "Charlie")
}""",

        4: """// analysis/marks.go
package analysis

import "fmt"

func AnalyzeMarks(marks []int) {
    total := 0
    for _, m := range marks {
        total += m
    }
    avg := float64(total) / float64(len(marks))
    fmt.Println("Total:", total)
    fmt.Println("Average:", avg)
}

// main.go
package main
import "myapp/analysis"

func main() {
    marks := []int{85, 90, 78, 88, 92}
    analysis.AnalyzeMarks(marks)
}""",

        5: """package main
import "fmt"

type Shape interface {
    Area() float64
}

type Rectangle struct{ width, height float64 }
func (r Rectangle) Area() float64 { return r.width * r.height }

type Circle struct{ radius float64 }
func (c Circle) Area() float64 { return 3.14 * c.radius * c.radius }

func main() {
    shapes := []Shape{
        Rectangle{10, 5},
        Circle{7},
    }
    for _, s := range shapes {
        fmt.Println("Area:", s.Area())
    }
}""",

        6: """package main
import "fmt"

type Node struct {
    value int
    left  *Node
    right *Node
}

func insert(root *Node, value int) *Node {
    if root == nil {
        return &Node{value: value}
    }
    if value < root.value {
        root.left = insert(root.left, value)
    } else {
        root.right = insert(root.right, value)
    }
    return root
}

func inorder(root *Node) {
    if root != nil {
        inorder(root.left)
        fmt.Print(root.value, " ")
        inorder(root.right)
    }
}

func main() {
    nums := []int{5, 3, 7, 1, 4, 6, 8}
    var root *Node
    for _, n := range nums {
        root = insert(root, n)
    }
    fmt.Print("Sorted: ")
    inorder(root)
}""",

        7: """package main
import (
    "encoding/json"
    "fmt"
)

type Student struct {
    Name string
    Age  int
}

func main() {
    s := Student{"Alice", 20}
    jsonData, _ := json.Marshal(s)
    fmt.Println(string(jsonData))
}""",

        8: """package main
import (
    "bufio"
    "fmt"
    "os"
)

func main() {
    seen := make(map[string]bool)
    scanner := bufio.NewScanner(os.Stdin)
    fmt.Println("Enter lines (Ctrl+D to stop):")
    for scanner.Scan() {
        line := scanner.Text()
        if !seen[line] {
            fmt.Println(line)
            seen[line] = true
        }
    }
}""",

        9: """package main
import (
    "fmt"
)

func fib(n int) int {
    if n <= 1 {
        return n
    }
    return fib(n-1) + fib(n-2)
}

func main() {
    ch := make(chan int)
    go func() {
        ch <- fib(50) // NOTE: Recursive fib(50) is slow
    }()
    fmt.Println("50th Fibonacci:", <-ch)
}""",

        10: """package main
import (
    "fmt"
    "os"
)

func main() {
    cities := []string{"New York", "London", "Tokyo", "Sydney"}
    file, err := os.Create("cities.txt")
    if err != nil {
        panic(err)
    }
    defer file.Close()

    for _, city := range cities {
        fmt.Fprintln(file, city)
    }
    fmt.Println("Cities written to file.")
}""",

        11: """package main
import "fmt"

func main() {
    ch := make(chan int, 5)
    fmt.Println("Channel capacity:", cap(ch))
}""",

        12: """package main
import (
    "fmt"
    "regexp"
)

func main() {
    var email string
    fmt.Print("Enter email: ")
    fmt.Scanln(&email)

    re := regexp.MustCompile(`^[a-z0-9._%+\\-]+@[a-z0-9.\\-]+\\.[a-z]{2,}$`)
    if re.MatchString(email) {
        fmt.Println("Valid email!")
    } else {
        fmt.Println("Invalid email!")
    }
}""",

        13: """package main
import (
    "fmt"
    "time"
)

func printAuthor(name string, id int) {
    fmt.Printf("Author: %s, ID: %d\\n", name, id)
}

func main() {
    authors := map[string]int{
        "Alice": 101,
        "Bob":   102,
        "Eve":   103,
    }

    for name, id := range authors {
        go printAuthor(name, id)
    }

    time.Sleep(1 * time.Second) // Wait for goroutines
}""",
    }

    if n not in programs:
        raise ValueError(f"Experiment {n} not found.")
    print(programs[n])

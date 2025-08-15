# Fibonacci Calculator in Fortran

A comprehensive Fortran program that calculates Fibonacci numbers using multiple methods.

## Features

- **Multiple Calculation Methods**:
  - Recursive calculation (educational, slower for large numbers)
  - Iterative calculation (efficient, recommended for large numbers)
  - Sequence generation (displays multiple Fibonacci numbers)

- **User-Friendly Interface**:
  - Interactive menu system
  - Input validation and error handling
  - Clear output formatting

- **Performance Considerations**:
  - Uses 64-bit integers to handle larger Fibonacci numbers
  - Warns users about performance implications of recursive method
  - Efficient iterative algorithms for better performance

## Requirements

- **Fortran Compiler**: GNU Fortran (gfortran) or compatible
- **Operating System**: Linux, macOS, or Windows with appropriate compiler

## Installation

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install gfortran
```

### macOS (with Homebrew)
```bash
brew install gcc
```

### Windows
Install MinGW-w64 or use Windows Subsystem for Linux (WSL)

## Compilation and Usage

### Using Make (Recommended)
```bash
# Build the program
make

# Build and run
make run

# Clean build artifacts
make clean

# Show help
make help
```

### Manual Compilation
```bash
# Compile the program
gfortran -Wall -Wextra -std=f2008 -O2 -g -o fibonacci fibonacci.f90

# Run the program
./fibonacci
```

## Program Usage

When you run the program, you'll see an interactive menu:

```
================================================
           FIBONACCI CALCULATOR
================================================

Choose calculation method:
1. Calculate single Fibonacci number (recursive)
2. Calculate single Fibonacci number (iterative)
3. Display Fibonacci sequence up to n terms
4. Exit program

Enter your choice (1-4):
```

### Option 1: Recursive Calculation
- Best for educational purposes and small numbers (n ≤ 45)
- Shows the mathematical definition of Fibonacci sequence
- Warning displayed for large numbers due to exponential time complexity

### Option 2: Iterative Calculation
- Recommended for all practical purposes
- Efficient O(n) time complexity
- Can handle larger numbers quickly

### Option 3: Sequence Display
- Shows the first n Fibonacci numbers
- Includes sum of the sequence
- Limited to 50 terms for display purposes

## Mathematical Background

The Fibonacci sequence is defined as:
- F(0) = 0
- F(1) = 1
- F(n) = F(n-1) + F(n-2) for n > 1

The sequence starts: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, ...

## Example Output

```
Enter the position (n >= 0): 10
Fibonacci(10) = 55

First 10 Fibonacci numbers:
----------------------------------------
F(0) = 0
F(1) = 1
F(2) = 1
F(3) = 2
F(4) = 3
F(5) = 5
F(6) = 8
F(7) = 13
F(8) = 21
F(9) = 34
----------------------------------------
Sum of sequence: 143
```

## Technical Details

- **Language Standard**: Fortran 2008
- **Integer Type**: 64-bit integers for handling large Fibonacci numbers
- **Error Handling**: Input validation and graceful error recovery
- **Memory Management**: Static arrays with defined limits
- **Code Style**: Modern Fortran with explicit interfaces and clear structure

## Performance Notes

- **Recursive Method**: O(2^n) time complexity - use only for educational purposes or small n
- **Iterative Method**: O(n) time complexity - recommended for all practical applications
- **Memory Usage**: Minimal memory footprint with static allocation

## License

This project is licensed under the Apache License 2.0. See the source files for full license text.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this Fibonacci calculator.
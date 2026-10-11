# funtion to get the item cost
def get_item_cost(n):
    prices = []
    for i in range(1, n + 1): 
        while True:
            try:
                price_str = input(f"Enter number {i}: ") #input number
                price = float(price_str) #convert strong to float
                prices.append(price)
                break
            except ValueError: #if not a number then raise error
                print("Invalid input. Please enter a valid number.")
    return prices

#function to get number of items
def get_no_of_items():
    while True:
        try:
            val = input("Enter the number of values to input: ")
            n = int(val)
            if n <= 0: #check if number is positive
                print(
                    "Invalid input: Please enter a positive integer greater than zero."
                )
                continue
            return n
        except ValueError as e:
            print(f"Invalid input: {e}. Please enter a valid positive integer.")

# main function 
def main():
    filename = "saved_numbers.txt" #file saving

    n = get_no_of_items()
    prices = get_item_cost(n)
    prices.sort()

    try:
        with open(filename, "w") as file:
            for price in prices:
                file.write(f"{price}\n") #for adding price in file
        print(f"Numbers written to {filename}.")
    except Exception as e:
        print(f"An rror occurred while writing to the file: {e}")
        return

    try:
        print("Reading numbers from file:")
        with open(filename, "r") as file:
            lines = [line.strip() for line in file if line.strip()]
            print(lines)
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")

if __name__ == "__main__":
    main()
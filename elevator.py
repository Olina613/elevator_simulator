import time
import threading

class Elevator:
    def __init__(self, name):
        self.name = name
        self.current_floor = 1

    def display_floor(self):
        print(f"Elevator {self.name} is currently on floor {self.current_floor}.")

    def move(self, target_floor, delay=1):
        current_floor = self.current_floor
        self.display_floor()
        if self.current_floor < target_floor:
            for i in range(current_floor + 1, target_floor + 1):
                self.current_floor = i
                self.display_floor() 
                time.sleep(delay)  
        else:
            for i in range(current_floor - 1, target_floor - 1, -1):
                self.current_floor = i
                self.display_floor() 
                time.sleep(delay)  


if __name__ == "__main__":
    elevator1 = Elevator("1")
    elevator2 = Elevator("2")

    while True:
        which = input("Which elevator? (1 or 2, or 'q' to quit): ")

        if which == "q":
            print("Goodbye!")
            break

        target = int(input("Target floor: "))

        if which == "1":
            t = threading.Thread(target=elevator1.move, args=(target,))
            t.start()
        elif which == "2":
            t = threading.Thread(target=elevator2.move, args=(target,))
            t.start()
        else:
            print("Please enter 1 or 2.")
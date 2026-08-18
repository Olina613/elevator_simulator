class Elevator:
    def __init__(self, name):
        self.name = name
        self.current_floor = 1

    def display_floor(self):
        print(f"Elevator {self.name} is currently on floor {self.current_floor}.")

    def move(self, current_floor, target_floor):
        self.current_floor = current_floor
        self.display_floor()
        if current_floor < target_floor:
            for i in range(current_floor + 1, target_floor + 1):
                print(f"Elevator {self.name} is moving up to floor {i}.")
                self.display_floor() 
        else:
            for i in range(current_floor - 1, target_floor - 1, -1):
                print(f"Elevator {self.name} is moving down to floor {i}.")
                self.display_floor() 

elevator1 = Elevator("電梯1")
elevator1.move(1, 5)

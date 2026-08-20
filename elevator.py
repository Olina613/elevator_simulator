import time
import threading

class Elevator:
    def __init__(self, name):
        self.name = name
        self.current_floor = 1
        self.direction = "idle"  # "up", "down", or "idle"
        self.target_floor = None 

    def display_floor(self):
        print(f"Elevator {self.name} is currently on floor {self.current_floor}.")

    def move(self, target_floor, delay=1):
        current_floor = self.current_floor
        self.display_floor()
        self.target_floor = target_floor

        if self.current_floor < target_floor:
            self.direction = "up"  
            for i in range(current_floor + 1, target_floor + 1):
                self.current_floor = i
                self.display_floor() 
                time.sleep(delay)  
        else:
            self.direction = "down"
            for i in range(current_floor - 1, target_floor - 1, -1):
                self.current_floor = i
                self.display_floor() 
                time.sleep(delay)  
        self.direction = "idle"
        self.target_floor = None 

def estimate_cost(elevator, call_floor, call_direction):
    distance = abs(elevator.current_floor - call_floor)

    # 情況 1:閒置
    if elevator.direction == "idle":
        return distance

    # 情況 2:順路
    if elevator.direction == "up" and call_direction == "up" and elevator.current_floor <= call_floor:
        return distance
    if elevator.direction == "down" and call_direction == "down" and elevator.current_floor >= call_floor:
        return distance

    # 情況 3:不順路
    to_finish = abs(elevator.current_floor - elevator.target_floor)   # 現在 → 原目標
    to_come = abs(elevator.target_floor - call_floor)
    return to_finish + to_come

def dispatch(elevators, call_floor, call_direction):
    best_elevator = None
    best_cost = None

    for elevator in elevators:
        cost = estimate_cost(elevator, call_floor, call_direction)
        if best_cost is None or cost < best_cost:
            best_cost = cost
            best_elevator = elevator

    return best_elevator

if __name__ == "__main__":
    elevator1 = Elevator("1")
    elevator2 = Elevator("2")
    elevators = [elevator1, elevator2]

    while True:
        call_floor_input = input("Which floor are you on? (or 'q' to quit): ")
        if call_floor_input == "q":
            print("Goodbye!")
            break
        call_floor = int(call_floor_input)

        call_direction = input("Going up or down? (up/down): ")
        if call_direction not in ("up", "down"):
            print("Please enter 'up' or 'down'.")
            continue

        # 派車員選出最適合的電梯
        chosen = dispatch(elevators, call_floor, call_direction)
        print(f"--> Dispatching Elevator {chosen.name} to floor {call_floor}")

        # 開 thread 讓被選中的電梯移動過來接人
        t = threading.Thread(target=chosen.move, args=(call_floor,))
        t.start()
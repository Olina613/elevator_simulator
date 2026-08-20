import time
import threading

class Elevator:
    def __init__(self, name):
        self.name = name
        self.current_floor = 1
        self.direction = "idle"  # "up", "down", or "idle"
        self.queue = [] 
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def display_floor(self):
        print(f"Elevator {self.name} is currently on floor {self.current_floor}.")

    def add_request(self, floor):
        with self.lock:
            if floor not in self.queue:
                self.queue.append(floor)

    def run(self): 
        while True:
            target = None
            with self.lock: 
                if self.queue:
                    target = self.pick_next_target()    

            if target is not None:
                self.move(target)       
                if self.current_floor == target:
                    with self.lock:
                        self.queue.remove(target)            
            else:
                self.direction = "idle"
                time.sleep(0.1)                  

    def move(self, target_floor, delay=1):  #一次一層(因為requst可能隨時加入)
        self.target_floor = target_floor

        if self.current_floor < target_floor:
            self.direction = "up"  
            self.current_floor += 1
        elif self.current_floor > target_floor:
            self.direction = "down"
            self.current_floor -= 1 
        else:
            self.direction = "idle"
        self.display_floor()
        time.sleep(delay)

    def pick_next_target(self):  #幫電梯選擇下一個目標樓層(選最近的)
        if self.direction == "up":
            # 先找「在乘客上方」的樓層，選其中最低的
            above = [f for f in self.queue if f >= self.current_floor]
            if above:
                return min(above)
            # 上方沒有了掉頭：選下方最高的
            return max(self.queue)

        elif self.direction == "down":
            # 先找「在乘客上方」的樓層，選其中最高的
            below = [f for f in self.queue if f <= self.current_floor]
            if below:
                return max(below)
            # 下方沒有了掉頭：選上方最低的
            return min(self.queue)

        else:  # idle：沒有方向,就選最近的
            return min(self.queue, key=lambda floor: abs(floor - self.current_floor))


def estimate_cost(elevator, call_floor, call_direction):  #計算該電梯到目標樓層的成本
    distance = abs(elevator.current_floor - call_floor) 

    # 情況 1:閒置
    if elevator.direction == "idle":
        return distance

    # 情況 2:順路
    if elevator.direction == "up" and call_direction == "up" and elevator.current_floor <= call_floor:
        return distance
    if elevator.direction == "down" and call_direction == "down" and elevator.current_floor >= call_floor:
        return distance

    # 情況 3:不順路 —— 走到方向盡頭,再折返回來
    if not elevator.queue:
        return distance
    if elevator.direction == "up":
        turning_point = max(elevator.queue)      # 往上的盡頭 = queue最大樓層
    else:
        turning_point = min(elevator.queue)      # 往下的盡頭 = queue最小樓層

    to_end = abs(elevator.current_floor - turning_point)   # 現在->盡頭
    back_to_client = abs(turning_point - call_floor)           # 盡頭->折返到乘客所在樓層
    return to_end + back_to_client

def dispatch(elevators, call_floor, call_direction):  #指派最適合的電梯
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
    elevator3 = Elevator("3")                 
    elevators = [elevator1, elevator2, elevator3]  

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

        chosen = dispatch(elevators, call_floor, call_direction)
        print(f"--> Dispatching Elevator {chosen.name} to floor {call_floor}")
        chosen.add_request(call_floor)
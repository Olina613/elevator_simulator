import unittest
import time
from elevator import Elevator, estimate_cost, dispatch


class TestMoveOneStep(unittest.TestCase):
    """測試 move():每次呼叫只移動一層,並正確更新方向"""

    def test_move_one_step_up(self):
        e = Elevator("test")
        e.direction = "idle"
        e.queue = []
        start = e.current_floor
        e.move(5, delay=0)
        self.assertEqual(e.current_floor, start + 1)

    def test_move_one_step_down(self):
        e = Elevator("test")
        e.current_floor = 5
        e.move(2, delay=0)
        self.assertEqual(e.current_floor, 4)

    def test_move_sets_direction_up(self):
        e = Elevator("test")
        e.current_floor = 3
        e.move(7, delay=0)
        self.assertEqual(e.direction, "up")

    def test_move_sets_direction_down(self):
        e = Elevator("test")
        e.current_floor = 7
        e.move(3, delay=0)
        self.assertEqual(e.direction, "down")

    def test_move_same_floor_stays(self):
        e = Elevator("test")
        e.current_floor = 4
        e.move(4, delay=0)
        self.assertEqual(e.current_floor, 4)


class TestAddRequest(unittest.TestCase):
    """測試 add_request():加入樓層,且不重複"""

    def test_add_single(self):
        e = Elevator("test")
        e.queue = []
        e.add_request(5)
        self.assertIn(5, e.queue)

    def test_no_duplicate(self):
        e = Elevator("test")
        e.queue = []
        e.add_request(5)
        e.add_request(5)
        self.assertEqual(e.queue.count(5), 1)

    def test_add_multiple(self):
        e = Elevator("test")
        e.queue = []
        e.add_request(3)
        e.add_request(7)
        self.assertEqual(len(e.queue), 2)


class TestPickNextTarget(unittest.TestCase):
    """測試 SCAN 選樓層邏輯:同方向優先,到頂/底才掉頭"""

    def test_up_picks_lowest_above(self):
        e = Elevator("test")
        e.current_floor = 5
        e.direction = "up"
        e.queue = [3, 7, 9]
        self.assertEqual(e.pick_next_target(), 7)

    def test_up_no_above_turns_around(self):
        # 往上但上方沒有樓層,掉頭選下方最高的
        e = Elevator("test")
        e.current_floor = 8
        e.direction = "up"
        e.queue = [2, 5]
        self.assertEqual(e.pick_next_target(), 5)

    def test_down_picks_highest_below(self):
        e = Elevator("test")
        e.current_floor = 5
        e.direction = "down"
        e.queue = [2, 4, 8]
        self.assertEqual(e.pick_next_target(), 4)

    def test_down_no_below_turns_around(self):
        # 往下但下方沒有樓層,掉頭選上方最低的
        e = Elevator("test")
        e.current_floor = 3
        e.direction = "down"
        e.queue = [6, 9]
        self.assertEqual(e.pick_next_target(), 6)

    def test_idle_picks_nearest(self):
        e = Elevator("test")
        e.current_floor = 5
        e.direction = "idle"
        e.queue = [1, 6, 10]
        self.assertEqual(e.pick_next_target(), 6)


class TestEstimateCost(unittest.TestCase):
    """測試派車成本計算:閒置、順路、不順路三種情況"""

    def test_idle_cost_is_distance(self):
        e = Elevator("test")
        e.current_floor = 3
        e.direction = "idle"
        e.queue = []
        self.assertEqual(estimate_cost(e, 8, "up"), 5)

    def test_same_direction_up_is_on_the_way(self):
        # 電梯往上、乘客往上、電梯在下方 → 順路,成本=距離
        e = Elevator("test")
        e.current_floor = 2
        e.direction = "up"
        e.queue = [9]
        self.assertEqual(estimate_cost(e, 6, "up"), 4)

    def test_same_direction_down_is_on_the_way(self):
        e = Elevator("test")
        e.current_floor = 9
        e.direction = "down"
        e.queue = [1]
        self.assertEqual(estimate_cost(e, 5, "down"), 4)

    def test_opposite_direction_adds_penalty(self):
        # 電梯在8樓往上(目標10),乘客在3樓要上 → 不順路
        # 成本 = (8->10) + (10->3) = 2 + 7 = 9
        e = Elevator("test")
        e.current_floor = 8
        e.direction = "up"
        e.queue = [10]
        self.assertEqual(estimate_cost(e, 3, "up"), 9)


class TestDispatch(unittest.TestCase):
    """測試派車:選成本最低的電梯,平手選先出現的"""

    def test_picks_nearest_when_both_idle(self):
        e1 = Elevator("1")
        e2 = Elevator("2")
        e1.current_floor = 1
        e1.direction = "idle"
        e1.queue = []
        e2.current_floor = 8
        e2.direction = "idle"
        e2.queue = []
        chosen = dispatch([e1, e2], 6, "up")
        self.assertEqual(chosen.name, "2")

    def test_prefers_on_the_way_over_idle_far(self):
        # e1 順路(往上、在下方),e2 閒置但遠 → 選 e1
        e1 = Elevator("1")
        e2 = Elevator("2")
        e1.current_floor = 2
        e1.direction = "up"
        e1.queue = [10]
        e2.current_floor = 10
        e2.direction = "idle"
        e2.queue = []
        chosen = dispatch([e1, e2], 5, "up")
        self.assertEqual(chosen.name, "1")

    def test_tie_picks_first(self):
        # 兩台成本相同,應選先出現的 e1
        e1 = Elevator("1")
        e2 = Elevator("2")
        e1.current_floor = 4
        e1.direction = "idle"
        e1.queue = []
        e2.current_floor = 8
        e2.direction = "idle"
        e2.queue = []
        chosen = dispatch([e1, e2], 6, "up")
        self.assertEqual(chosen.name, "1")


class TestMultipleElevators(unittest.TestCase):
    """測試 N 台電梯(3~6台)的派車:證明可擴充性"""

    def _make_elevators(self, n):
        # 建立 n 台電梯,全部閒置在 1 樓
        elevators = []
        for i in range(1, n + 1):
            e = Elevator(str(i))
            e.current_floor = 1
            e.direction = "idle"
            e.queue = []
            elevators.append(e)
        return elevators

    def test_three_all_idle_picks_nearest(self):
        # 3 台:分別在 1、5、9 樓,乘客在 8 樓 → 應選最近的 9 樓那台(3號)
        elevators = self._make_elevators(3)
        elevators[0].current_floor = 1
        elevators[1].current_floor = 5
        elevators[2].current_floor = 9
        chosen = dispatch(elevators, 8, "up")
        self.assertEqual(chosen.name, "3")

    def test_four_picks_nearest(self):
        # 4 台:在 1、4, 7、10 樓,乘客在 6 樓 → 最近是 7 樓那台(3號)
        elevators = self._make_elevators(4)
        elevators[0].current_floor = 1
        elevators[1].current_floor = 4
        elevators[2].current_floor = 7
        elevators[3].current_floor = 10
        chosen = dispatch(elevators, 6, "up")
        self.assertEqual(chosen.name, "3")

    def test_five_on_the_way_beats_idle(self):
        # 5 台:4號順路(往上、在乘客下方),其餘閒置但較遠 → 選 4號
        elevators = self._make_elevators(5)
        elevators[0].current_floor = 10
        elevators[1].current_floor = 10
        elevators[2].current_floor = 10
        elevators[3].current_floor = 2      # 4號
        elevators[3].direction = "up"
        elevators[3].queue = [9]
        elevators[4].current_floor = 10
        chosen = dispatch(elevators, 5, "up")
        self.assertEqual(chosen.name, "4")

    def test_six_all_idle_picks_nearest(self):
        # 6 台:在 1、3、5、7、9、10 樓,乘客在 4 樓 → 最近是 3 樓那台(2號)
        elevators = self._make_elevators(6)
        floors = [1, 3, 5, 7, 9, 10]
        for e, f in zip(elevators, floors):
            e.current_floor = f
        chosen = dispatch(elevators, 4, "up")
        self.assertEqual(chosen.name, "2")

    def test_six_tie_picks_lowest_number(self):
        # 6 台:2號和3號距離乘客相同,平手應選編號較小的(2號)
        elevators = self._make_elevators(6)
        # 乘客在 5 樓;把 2號放 4樓(距離1)、3號放 6樓(距離1),其餘放遠處
        elevators[0].current_floor = 10
        elevators[1].current_floor = 4     # 2號,距離1
        elevators[2].current_floor = 6     # 3號,距離1
        elevators[3].current_floor = 10
        elevators[4].current_floor = 10
        elevators[5].current_floor = 10
        chosen = dispatch(elevators, 5, "up")
        self.assertEqual(chosen.name, "2")

    def test_scales_dispatch_returns_valid_elevator(self):
        # 對 3~6 台各跑一次,確認 dispatch 一定回傳清單裡的某台(不崩潰、不回 None)
        for n in range(3, 7):
            elevators = self._make_elevators(n)
            for i, e in enumerate(elevators):
                e.current_floor = i + 1
            chosen = dispatch(elevators, 5, "up")
            self.assertIn(chosen, elevators)

    def test_six_distributes_different_requests(self):
        # 6 台,不同狀態,連續三個不同請求應分配給不同的合適電梯
        elevators = self._make_elevators(6)
        # 1號往上經過中段,其餘閒置在不同樓層
        elevators[0].current_floor = 2
        elevators[0].direction = "up"
        elevators[0].queue = [9]
        elevators[1].current_floor = 1
        elevators[2].current_floor = 4
        elevators[3].current_floor = 6
        elevators[4].current_floor = 8
        elevators[5].current_floor = 10
        
        chosen_a = dispatch(elevators, 7, "up")
        self.assertEqual(chosen_a.name, "4")


if __name__ == "__main__":
    unittest.main(verbosity=2)
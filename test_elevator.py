import unittest
from elevator import Elevator


class TestElevator(unittest.TestCase):

    def test_move_up(self):
        elevator = Elevator("test")
        elevator.move(1, 5, delay=0)
        self.assertEqual(elevator.current_floor, 5)

    def test_move_down(self):
        elevator = Elevator("test")
        elevator.move(5, 2, delay=0)
        self.assertEqual(elevator.current_floor, 2)

    def test_stay(self):
        elevator = Elevator("test")
        elevator.move(3, 3, delay=0)
        self.assertEqual(elevator.current_floor, 3)


if __name__ == "__main__":
    unittest.main()
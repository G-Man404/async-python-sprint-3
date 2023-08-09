import unittest
from server import Communication
import asyncio


class TestMessageProcessing(unittest.TestCase):
    def test_read_message_1(self):
        data = b"101 text"
        self.assertEqual(Communication.message_processing(data), (101, ["text"]))

    def test_read_message_2(self):
        data = b"120 exit"
        self.assertEqual(Communication.message_processing(data), (120, ["exit"]))

    def test_read_message_3(self):
        data = b"120"
        self.assertEqual(Communication.message_processing(data), (120, ""))

    def test_read_message_4(self):
        data = b"120"
        self.assertNotEqual(Communication.message_processing(data), 120)



if __name__ == "__main__":
    unittest.main()

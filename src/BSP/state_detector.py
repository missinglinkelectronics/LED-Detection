from typing import List

from cv2 import cv2
import numpy as np
import sched
import time

from src.BDG.model.board_model import Board
from src.BSP import led_state_detector
from src.BSP.BoardOrientation import BoardOrientation
from src.BSP.homographyProvider import homography_by_sift
from src.BSP.led_extractor import get_led_roi
from src.BSP.led_state import LedState
from src.BSP.state_table_entry import StateTableEntry


class StateDetector:

    def __init__(self, config: Board, webcam_id: int):
        self.board = config
        self.webcam_id = webcam_id
        self.delay_in_seconds = 1
        self.state_table: List[StateTableEntry] = []
        self.timer: sched.scheduler = sched.scheduler(time.time(), time.sleep)
        self.current_orientation: BoardOrientation = None
        self.video_capture: cv2.VideoCapture = None

        self._init_table()

    def create_state_table(self):
        pass

    def start(self):
        self.timer.enter(self.delay_in_seconds, 1, self._detect_current_state)

    def _detect_current_state(self):

        self._open_stream()

        read, frame = self.video_capture.read()

        if self.current_orientation is None or self.current_orientation.check_if_outdated():
            self.current_orientation = homography_by_sift(self.board.image, frame)

        leds_roi = get_led_roi(frame, self.board.led, self.current_orientation)

        led_states: List[LedState] = list(map(lambda x: led_state_detector.get_state(x[0], x[1].colors),
                                              zip(leds_roi, self.board.led)))

        for i in range(len(self.state_table)):
            entry = self.state_table[i]
            led = self.board.led[i]
            state = led_states[i]
            entry.current_state = state

            if state.power is "on":
                entry.last_time_on = state.timestamp
            else:
                entry.last_time_off = state.timestamp



    def _init_table(self):
        for led in self.board.led:
            self.state_table.append(StateTableEntry(led.id, None, 0, 0))

    def _open_stream(self):
        self.video_capture = cv2.VideoCapture(self.webcam_id)

        if not self.video_capture.isOpened():
            raise Exception(f"StateDetector is unable to open VideoCapture with index {self.webcam_id}")








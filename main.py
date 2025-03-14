import logging
from pathlib import Path
import asyncio
import enum

import pydantic

import krystallium
import rfid
from krystallium import samples


class Main(krystallium.component.MainLoop):
    class LightState(enum.Enum):
        Inactive = enum.auto()
        Active = enum.auto()
        Fadeout = enum.auto()
        Overload = enum.auto()

    def __init__(self):
        super().__init__(interval = 0.1)

        self.__lights = None
        self.__lights_state = self.LightState.Inactive

        self.__rfid_left = None
        self.__rfid_right = None

        self.__left_sample = None
        self.__right_sample = None

        self.__intensity = 0


    async def start(self):
        self.__serial_controller = rfid.RFIDController(
            self.on_card_detected,
            self.on_card_lost,
            self.on_traits,
        )
        self.__serial_controller.start()

    async def stop(self):
        self.__serial_controller.stop()

    async def update(self, elapsed: float):
        if not self.__lights:
            self.__lights = self.__serial_controller.getDeviceByName("pg-lights")
            if self.__lights:
                logging.info(f"Found light controller: {self.__lights.port}")

        if not self.__rfid_left:
            self.__rfid_left = self.__serial_controller.getDeviceByName("rfid-left")
            if self.__rfid_left:
                logging.info(f"Found left RFID: {self.__rfid_left.port}")

        if not self.__rfid_right:
            self.__rfid_right = self.__serial_controller.getDeviceByName("rfid-right")
            if self.__rfid_right:
                logging.info(f"Found right RFID: {self.__rfid_right.port}")

        if self.__left_sample and self.__right_sample and self.__lights_state == self.LightState.Inactive:
            if samples.Action.is_opposite(self.__left_sample.primary_action, self.__right_sample.primary_action):
                left_target = self.__left_sample.primary_target.to_int()
                right_target = self.__right_sample.primary_target.to_int()

                # Min: 16.2 Max: 162
                t = (left_target + right_target) * (2.4 + 5.7)

                left_purity = int(self.__left_sample.purity)
                right_purity = int(self.__right_sample.purity)
                # Min:
                p = ((left_purity * right_purity) / (1 + (abs(left_purity - right_purity) * 0.25))) * 8.4

                e = t * p

                self.__intensity = (e / 100000) * 255

                self.set_lights_state(self.LightState.Active, self.__intensity)

    def on_card_detected(self, name, rfid_id):
        pass

    def on_card_lost(self, name, rfid_id):
        if self.__left_sample and self.__right_sample:
            self.set_lights_state(self.LightState.Inactive, self.__lights_state)

        if self.__left_sample and self.__left_sample.rfid_id == rfid_id:
            self.__left_sample = None
        elif self.__right_sample and self.__right_sample.rfid_id == rfid_id:
            self.__right_sample = None

    def on_traits(self, name, traits):
        if not self.__rfid_left or not self.__rfid_right:
            return

        if traits[0] != "refined":
            logging.warning(f"Invalid sample type {traits[0]}")

        if name == self.__rfid_left.name:
            self.__left_sample = krystallium.samples.RefinedSample.from_traits(
                self.__rfid_left.card_id,
                traits
            )
            if self.__lights:
                self.__lights.sendRawCommand("DETECTED LEFT")
        elif name == self.__rfid_right.name:
            self.__right_sample = krystallium.samples.RefinedSample.from_traits(
                self.__rfid_right.card_id,
                traits
            )
            if self.__lights:
                self.__lights.sendRawCommand("DETECTED RIGHT")

    def set_lights_state(self, state, intensity):
        if state == self.__lights_state or not self.__lights:
            return

        self.__lights_state = state
        logging.info(f"New light state {self.__lights_state}")
        match state:
            case self.LightState.Inactive:
                self.__lights.sendRawCommand(f"SETSTATE INACTIVE {intensity}")
            case self.LightState.Active:
                self.__lights.sendRawCommand(f"SETSTATE ACTIVE {intensity}")
            case self.LightState.Fadeout:
                self.__lights.sendRawCommand(f"SETSTATE FADEOUT {intensity}")
            case self.LightState.Overload:
                self.__lights.sendRawCommand(f"SETSTATE OVERLOAD {intensity}")


if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO)

    main = Main()
    main.run()

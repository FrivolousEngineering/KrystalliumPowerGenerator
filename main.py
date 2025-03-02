import time

import pydantic

import rfid


@pydantic.dataclasses.dataclass(kw_only = True, frozen = True)
class RefinedSample:
    id: int
    rfid_id: str

    primary_action: str
    primary_target: str
    secondary_action: str
    secondary_target: str
    purity: str


class Main:
    def __init__(self):
        self.__rfid_controller = rfid.RfidController(
            self.on_card_detected,
            self.on_card_lost,
            self.on_traits,
        )
        self.__rfid_controller.start()

        self.__first_sample = None
        self.__second_sample = None

    def run(self):
        while True:
            time.sleep(0.1)



    def on_card_detected(self, name, rfid_id):
        pass

    def on_card_lost(self, name, rfid_id):
        if self.__first_sample.rfid_id == rfid_id:
            self.__first_sample = None
        elif self.__second_sample.rfid_id == rfid_id:
            self.__second_sample = None

    def on_traits(self, name, traits):
        pass


if __name__ == "__main__":
    main = Main()
    main.run()

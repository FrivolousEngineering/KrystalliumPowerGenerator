import rfid


class Main:
    def __init__(self):
        self.__rfid_controller = rfid.RfidController(
            self.on_card_detected,
            self.on_card_lost,
            self.on_traits,
        )
        self.__rfid_controller.start()

    def run(self):
        pass

    def on_card_detected(self, name, rfid_id):
        pass

    def on_card_lost(self, name, rfid_id):
        pass

    def on_traits(self, name, traits):
        pass


if __name__ == "__main__":
    main = Main()
    main.run()


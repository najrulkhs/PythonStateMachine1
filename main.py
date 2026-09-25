class TrafficLight:
    TRANSITIONS = {
        "red": "green",
        "green": "yellow",
        "yellow": "red",
    }

    def __init__(self):
        self.state = "red"

    def next(self):
        self.state = self.TRANSITIONS[self.state]
        return self.state


def main():
    light = TrafficLight()
    print(f"start: {light.state}")
    for _ in range(6):
        print(f"-> {light.next()}")


if __name__ == "__main__":
    main()

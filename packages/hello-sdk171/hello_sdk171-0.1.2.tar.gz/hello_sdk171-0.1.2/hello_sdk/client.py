class HelloClient:
    def say_hello(self, name: str) -> str:
        return f"Hello, {name}! Welcome to my SDK."
    def say_goodbye(self, name: str) -> str:
        return f"Goodbye, {name}! Hope to see you again soon."
    def greet(self, name: str) -> str:
        return self.say_hello(name) + " " + self.say_goodbye(name)
    def farewell(self, name: str) -> str:
        return self.say_goodbye(name)
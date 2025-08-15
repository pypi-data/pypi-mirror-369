from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label

class HelpInput(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.input = TextInput(hint_text="Enter value")
        self.help_label = Label(text="This is help text.", size_hint_y=None, height=30)
        self.help_label.opacity = 0  # Hide initially
        self.input.bind(focus=self.on_focus)
        self.add_widget(self.input)
        self.add_widget(self.help_label)

    def on_focus(self, instance, value):
        self.help_label.opacity = 1 if value else 0

class TestApp(App):
    def build(self):
        return HelpInput()

if __name__ == '__main__':
    TestApp().run()
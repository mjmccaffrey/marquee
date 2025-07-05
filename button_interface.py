"""Marquee Lighted Sign Project - button interface."""

class ButtonInterface:
    """Button interface."""

    @classmethod
    def reset(cls):
        """Prepare for a button press."""

    @classmethod
    def wait(cls, seconds: float | None):
        """Wait until seconds have elapsed or any button is pressed."""
    
    def close(self):
        """Clean up."""

    def button_pressed(self):
        """Callback for button press."""

    def virtual_button_pressed(self):
        """Callback for virtual button press."""

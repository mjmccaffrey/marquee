**Marquee semi-retro lighted sign project**

I have wanted to make this project for a while, and our son's graduation from the University Alabama was the excuse I needed.<br/><br/>
While the Raspberry Pi and other electronics are relatively modern, the incandescent bulbs and ceramic lamp holders give it a retro feel, as do the mechanical relays, whose clicks resonate in the wooden cabinet.<br/>

<b>Version 3.0.0 represents a substantial amount of hardware and software work, including the following:
* Added dimmers, allowing independent control of each bulb's brightness.
* Added new Dimmer, Executor and Mode classes.
* Added a 4-button remote control and receiver.
* Revamped the wiring and electrical components.</b>

<b>Version 3 demo video</b>
[![](readme/marquee_v3_front.jpg)](https://www.youtube.com/watch?v=Xw9Ktnp-iGw)

<figure>
<figcaption>Version 3 internals (more or less - work in progress)</figcaption>
<img src="readme/marquee_v3_back_open.jpg" height=400>
</figure>

Version 2.2.0 includes the following:
* Moved most of the main application code into the new class Player.
* Added the initial fetching and subsequent tracking of the state of the lights.
* Added random light sequences, along with a new mode random_flip that utilizes the new state tracking feature.

Version 2.1.0 includes the following:
* Command-line specification of the initial mode.
* Command-line specification of a light pattern.  If specified, the application will set the lights accordingly and then exit.

Version 2.0.0 includes the following:
* Added a button to the back of the cabinet to allow the operator to change modes at any time.
* Added an RS-232 port for easy Raspberry Pi console access.
* Reworked the code rather extensively.

<figure>
<figcaption>Our son's graduation</figcaption>
<img src="readme/marquee_bama_grad.jpg" height=400>
</figure>

<figure>
<figcaption>Our 27th wedding anniversary</figcaption>
<img src="readme/marquee_27th_anniversary.jpg" height=400>
</figure>

<figure>
<figcaption>Version 2 internals</figcaption>
<img src="readme/marquee_v2_back_open.jpg" height=400>
</figure>
  
<figure>
<figcaption>Version 2 externals</figcaption>
<img src="readme/marquee_v2_back_closed.jpg" height=400>
</figure>

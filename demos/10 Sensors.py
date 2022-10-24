# These scripts are created to demo how sensor components can work async.
# Sensor components are components that interact with the user or measure something. This would
# include buttons, joysticks, keypads, temperature, humidity, sounds and other sensors
# Sensor components either use a callback or scan approach.
# Callbacks are used when a certain event (such as button press or button release) happens. This event will execute
#     the callback method. (callbacks are never used as IRQ handlers so anything can be done in these methods)

# Scan approach is used when at specific time intervals the state of the component is scanned and the current state is
#     set. This is typical for most sensors including joysticks, potentiometer, temperature.

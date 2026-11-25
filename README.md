# Transformation Matrix Multiplication Visualizer
An interactive interface to visualize the effect of transformation matrix multipllication to a frame. Shows the effect of pre-multiplication and post-multiplication of transformation matrix. This work is based on Chapter 3 of Lynch, K. and Park, F. (2017) Modern Robotics: Mechanics, Planning, and Control. Made with Copilot (GPT 6 Luna). 

| Legends | X axis | Y axis | Z axis | Center |
| - | - | - | - | - |
| World Coordinate | X | Y | Z | s |
| Frame 1 (T1 or Tsb) | X1 | Y1 | Z1 | Tsb |
| Frame 1 * T2 (Tsb * T)         | X12   | Y12   | Z12   | Tsb * T
| T2 * Frame 1 (T * Tsb)                     | X21      | Y21      | Z21      | T * Tsb
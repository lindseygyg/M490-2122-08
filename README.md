# M490-2122-08
Repository for MECH490 (2021-2022) Team 8: Improving a CPR Manikin. All sensors are placed on an upper human torso manikin that was manufactured by the same group.

This repository will control the web server (django) and all the classes for the sensors.

Initially, an accelerometer was used, however drift was too much to account for and was therefore defunct. The Accelerometer class remains for data. This sensor was replacecd by a simple touch sensor that keeps track of each compression.

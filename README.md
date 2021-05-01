# TTM4133-group16
## Braze Device 
Semester project for the course "TTM4133 - Design of Communicating Systems"

We made a Walkietalkie program in python using MQTT and state machines. The walkietalkie supports VoiceRecognizion.

### Contributors
* Erik Turøy Midtun
* Simen Melleby Aarnseth
* Wictor Zhao
* Ingrid Nord
 
### Prerequisites

* Python3
* pip
* [PyAudio and portAudio](https://people.csail.mit.edu/hubert/pyaudio/)

### Virtualenv
Create a virtual environment for Python to handle packages:

```bash
python3 -m pip install virtualenv
virtualenv -p python3 venv
source venv/bin/activate # venv\Scripts\activate for windows
```

### Install requirements

```bash
pip install -r requirements.txt
```

### How to run
The complete program can be run with 
```bash
python src/main.py 7
```
where the number '7' spesifies the device_id. if no device id is provided you will get device_id=0.



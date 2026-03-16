import json
import time
import random
import argparse
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

TOPICS = {
    "temperature":    {"min": 15.0,  "max": 85.0,  "unit": "celsius"},
    "vibration":      {"min": 0.0,   "max": 10.0,  "unit": "mm/s"},
    "rpm":            {"min": 400,   "max": 1800,  "unit": "rpm"},
    "brake-pressure": {"min": 2.0,   "max": 8.0,   "unit": "bar"},
    "load-weight":    {"min": 0,     "max": 80000, "unit": "kg"},
}

def generate_reading(metric: str, anomaly: bool = False) -> float:
    cfg = TOPICS[metric]
    value = random.uniform(cfg["min"], cfg["max"])
    if anomaly and random.random() < 0.05:
        value = cfg["max"] * random.uniform(1.1, 1.5)
    return round(value, 2)

def build_payload(device_id: str, zone: str, metric: str, value: float) -> str:
    return json.dumps({
        "device_id": device_id,
        "zone": zone,
        "metric": metric,
        "value": value,
        "unit": TOPICS[metric]["unit"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

def run(args):
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(args.host, args.port, 60)
    client.loop_start()

    zones = args.zone if args.zone else ["zona-centro"]
    print(f"[simulator] {args.devices} devices/zone | zones={zones} | interval={args.interval}ms | anomaly={args.anomaly}")

    while True:
        for zone in zones:
            for i in range(args.devices):
                device_id = f"sensor-{zone}-{i:03d}"
                for metric in TOPICS:
                    value = generate_reading(metric, anomaly=args.anomaly)
                    topic = f"rail/{zone}/{device_id}/{metric}"
                    payload = build_payload(device_id, zone, metric, value)
                    client.publish(topic, payload, qos=0)
        time.sleep(args.interval / 1000)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Railway IoT Sensor Simulator")
    parser.add_argument("--host",     default="localhost",  help="MQTT broker host")
    parser.add_argument("--port",     type=int, default=1883, help="MQTT broker port")
    parser.add_argument("--devices",  type=int, default=5,  help="Number of simulated devices per zone")
    parser.add_argument("--zone",     action="append",      help="Railway zone name (repeatable)")
    parser.add_argument("--interval", type=int, default=1000, help="Publish interval in ms")
    parser.add_argument("--anomaly",  action="store_true",  help="Inject random anomaly events")
    run(parser.parse_args())

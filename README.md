# railway-iot-sensor-simulator

Python IoT sensor simulator for development and demo environments of **railway-iot-platform**.

---

## Responsibilities

- Simulates ESP32/Raspberry Pi sensor devices publishing telemetry via MQTT
- Configurable number of devices, zones, and publish interval
- Injects anomaly scenarios (out-of-range values) for threshold alert and ML testing
- Publishes to topic pattern: `rail/<zone>/<device_id>/<metric>`

---

## Sensor Metrics Simulated

| Metric | Normal Range | Unit | Anomaly Range |
|---|---|---|---|
| `temperature` | 15–65 | °C | 70–85 |
| `vibration` | 0–6 | mm/s | 7–10 |
| `rpm` | 400–1500 | rpm | 1600–1800 |
| `brake-pressure` | 2–6.5 | bar | 7–8 |
| `load-weight` | 0–70,000 | kg | 72,000–80,000 |

---

## MQTT Payload Format

```json
{
  "device_id": "track-sensor-01",
  "zone": "zone-a",
  "metric": "temperature",
  "value": 68.4,
  "timestamp": "2026-03-17T10:30:00.123456Z"
}
```

Topic: `rail/zone-a/track-sensor-01/temperature`

---

## Usage

### Run with Docker Compose (recommended)

```bash
cd railway-iot-infra

# Start simulator (uses docker-compose simulator profile)
docker compose --profile simulator up -d simulator

# View simulator logs
docker compose logs -f simulator
```

The simulator is pre-configured in `docker-compose.yml` to publish every **2 seconds** with anomaly injection enabled.

### Run directly

```bash
cd railway-iot-sensor-simulator
pip install -r requirements.txt

# Simulate 5 devices per zone, 3 zones, publish every 2 seconds with anomaly injection
python src/simulator.py --devices 5 --zone zone-a --interval 2000 --anomaly

# Custom MQTT broker
python src/simulator.py --host localhost --port 1883 --devices 10 --zone zone-b

# Multiple zones (run separate instances)
python src/simulator.py --zone zone-a --devices 5 --anomaly &
python src/simulator.py --zone zone-b --devices 5 --anomaly &
```

---

## CLI Options

| Flag | Default | Description |
|---|---|---|
| `--host` | `mqtt` | MQTT broker hostname |
| `--port` | `1883` | MQTT broker port |
| `--devices` | `5` | Number of simulated devices |
| `--zone` | `zone-a` | Zone identifier |
| `--interval` | `2000` | Publish interval in milliseconds |
| `--anomaly` | off | Enable anomaly injection |

> **Interval note:** Using intervals below 1000 ms with many devices may overflow the Celery task queue. The recommended minimum is **2000 ms**.

---

## Anomaly Injection

When `--anomaly` is passed, each publish has a ~10% probability of emitting an out-of-range value for a random metric. This is designed to trigger:
1. `check_threshold_alert` Celery task → creates an alert in the database
2. ML Engine Isolation Forest → flags the reading as anomalous
3. Alert WebSocket push → displays in the dashboard alert panel

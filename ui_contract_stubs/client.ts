export type CommandRequest = {
  payload: Record<string, unknown>;
  confirm: boolean;
};

export type CommandResult = {
  command: string;
  command_id: string;
  accepted: boolean;
  detail?: string | null;
  timestamp_ms: number;
};

const jsonHeaders = { "Content-Type": "application/json" };

export class NDefenderClient {
  constructor(private baseUrl: string) {}

  private async get<T>(path: string): Promise<T> {
    const resp = await fetch(`${this.baseUrl}${path}`);
    if (!resp.ok) throw new Error(`${resp.status}`);
    return (await resp.json()) as T;
  }

  private async post<T>(path: string, body: CommandRequest): Promise<T> {
    const resp = await fetch(`${this.baseUrl}${path}`, {
      method: "POST",
      headers: jsonHeaders,
      body: JSON.stringify(body),
    });
    if (!resp.ok) {
      const payload = await resp.json().catch(() => ({}));
      const detail = (payload as any).detail || resp.status;
      throw new Error(String(detail));
    }
    return (await resp.json()) as T;
  }

  health() {
    return this.get("/health");
  }

  status() {
    return this.get("/status");
  }

  contacts() {
    return this.get("/contacts");
  }

  gps() {
    return this.get("/gps");
  }

  networkWifiState() {
    return this.get("/network/wifi/state");
  }

  networkWifiScan() {
    return this.get("/network/wifi/scan");
  }

  networkBluetoothState() {
    return this.get("/network/bluetooth/state");
  }

  networkBluetoothDevices() {
    return this.get("/network/bluetooth/devices");
  }

  audio() {
    return this.get("/audio");
  }

  audioMute(muted: boolean) {
    return this.post<CommandResult>("/audio/mute", { payload: { muted }, confirm: false });
  }

  audioVolume(volume_percent: number) {
    return this.post<CommandResult>("/audio/volume", {
      payload: { volume_percent },
      confirm: false,
    });
  }

  esp32() {
    return this.get("/esp32");
  }

  esp32Buzzer(mode: string, duration_ms?: number) {
    return this.post<CommandResult>("/esp32/buzzer", {
      payload: { mode, duration_ms },
      confirm: false,
    });
  }

  esp32Leds(r: number, y: number, g: number) {
    return this.post<CommandResult>("/esp32/leds", { payload: { r, y, g }, confirm: false });
  }

  vrxTune(vrx_id: number, freq_hz: number) {
    return this.post<CommandResult>("/vrx/tune", { payload: { vrx_id, freq_hz }, confirm: false });
  }

  scanStart(dwell_ms: number, step_hz: number, start_hz: number, stop_hz: number) {
    return this.post<CommandResult>("/scan/start", {
      payload: { dwell_ms, step_hz, start_hz, stop_hz },
      confirm: false,
    });
  }

  scanStop() {
    return this.post<CommandResult>("/scan/stop", { payload: {}, confirm: false });
  }

  videoSelect(sel: number) {
    return this.post<CommandResult>("/video/select", { payload: { sel }, confirm: false });
  }
}

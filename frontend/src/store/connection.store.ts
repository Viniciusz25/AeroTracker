import { create } from 'zustand';

interface ConnectionStore {
  channels: Record<string, boolean>;
  setChannelConnected: (channel: string, connected: boolean) => void;
  isConnected: (channel: string) => boolean;
}

export const useConnectionStore = create<ConnectionStore>((set, get) => ({
  channels: {
    aircraft: false,
    iss: false,
    weather: false,
    system: false,
  },
  setChannelConnected: (channel, connected) =>
    set((state) => ({
      channels: { ...state.channels, [channel]: connected },
    })),
  isConnected: (channel) => Boolean(get().channels[channel]),
}));

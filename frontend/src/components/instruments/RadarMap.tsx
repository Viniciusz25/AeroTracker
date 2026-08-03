import { FC } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, Tooltip } from 'react-leaflet';
import L from 'leaflet';
import type { AircraftState } from '../../types/aircraft.types';
import { useSettingsStore } from '../../store/settings.store';
import { useAircraftStore } from '../../store/aircraft.store';

export interface RadarMapProps {
  aircraft?: AircraftState[];
  onSelectAircraft?: (icao24: string) => void;
  className?: string;
}

// Custom DivIcon creator for aircraft targets with rotated SVG icon
const createAircraftIcon = (heading: number, onGround: boolean, isSelected: boolean) => {
  const color = isSelected ? '#00D4FF' : onGround ? '#FFC857' : '#47F3A0';
  const glow = isSelected ? 'filter: drop-shadow(0 0 8px #00D4FF);' : 'filter: drop-shadow(0 0 4px rgba(71,243,160,0.5));';

  const svgHtml = `
    <div style="transform: rotate(${heading}deg); width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; ${glow}">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3.5c-.5-.5-2.5 0-4 1.5L13.5 8.5 5.3 6.7c-.8-.2-1.6.4-1.8 1.2l-.4 1.5c-.2.7.2 1.5 1 1.7l6.2 2.3-3 3-2.3-.6c-.4-.1-.8.1-1 .5l-.6 text-.6c-.3.4-.2.9.2 1.2l3 2.5 2.5 3c.3.4.8.5 1.2.2l.6-.6c.4-.2.6-.6.5-1l-.6-2.3 3-3 2.3 6.2c.2.8 1 1.2 1.7 1l1.5-.4c.8-.2 1.4-1 1.2-1.8z"/>
      </svg>
    </div>
  `;

  return L.divIcon({
    html: svgHtml,
    className: 'aircraft-marker-icon',
    iconSize: [28, 28],
    iconAnchor: [14, 14],
  });
};

// Custom DivIcon for station marker (GRU)
const stationIcon = L.divIcon({
  html: `
    <div style="position: relative; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center;">
      <div style="position: absolute; width: 12px; height: 12px; background: #47F3A0; border-radius: 50%; box-shadow: 0 0 12px #47F3A0;"></div>
      <div style="position: absolute; width: 24px; height: 24px; border: 2px solid #47F3A0; border-radius: 50%; animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite; opacity: 0.7;"></div>
    </div>
  `,
  className: 'station-marker-icon',
  iconSize: [24, 24],
  iconAnchor: [12, 12],
});

export const RadarMap: FC<RadarMapProps> = ({
  aircraft = [],
  onSelectAircraft,
  className = '',
}) => {
  const { latitude: centerLat, longitude: centerLon } = useSettingsStore();
  const { selectedIcao, selectAircraft, radarRangeKm } = useAircraftStore();

  const centerPos: [number, number] = [centerLat, centerLon];

  return (
    <div className={`relative bg-[#050608] border border-[#1A1F2B] rounded-2xl overflow-hidden shadow-2xl z-10 flex flex-col ${className}`}>
      {/* Map Header Overlay */}
      <div className="absolute top-3 left-3 right-3 z-[1000] flex items-center justify-between pointer-events-none">
        <div className="bg-[#0C0E12]/90 border border-[#1A1F2B] backdrop-blur-md px-3 py-1.5 rounded-xl pointer-events-auto flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#47F3A0] animate-pulse" />
          <span className="text-xs font-mono text-white font-bold">REAL-TIME FLIGHT MAP</span>
          <span className="text-[10px] font-mono text-[#47F3A0]">({aircraft.length} TARGETS)</span>
        </div>

        <div className="bg-[#0C0E12]/90 border border-[#1A1F2B] backdrop-blur-md px-3 py-1.5 rounded-xl pointer-events-auto text-[10px] font-mono text-[#B0BAC8]">
          CENTER: <strong className="text-white">SBGR (GRU)</strong> · RANGE: <strong className="text-[#00D4FF]">{radarRangeKm}km</strong>
        </div>
      </div>

      {/* Leaflet Map Engine */}
      <MapContainer
        center={centerPos}
        zoom={12}
        scrollWheelZoom={true}
        className="w-full h-full min-h-[500px] z-0"
        zoomControl={false}
      >
        {/* CartoDB Dark Matter High Quality Map Tiles */}
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a> &copy; <a href="https://openstreetmap.org">OpenStreetMap</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          maxZoom={19}
        />

        {/* Station 10km Sector Range Circle */}
        <Circle
          center={centerPos}
          radius={radarRangeKm * 1000}
          pathOptions={{
            color: '#00D4FF',
            fillColor: '#00D4FF',
            fillOpacity: 0.04,
            weight: 1.5,
            dashArray: '6 6',
          }}
        />

        {/* Airport Station Marker */}
        <Marker position={centerPos} icon={stationIcon}>
          <Tooltip permanent direction="top" offset={[0, -10]} className="bg-transparent border-0 shadow-none">
            <span className="bg-[#0C0E12] text-[#47F3A0] font-mono text-[10px] px-2 py-0.5 rounded border border-[#47F3A0]/40 font-bold shadow-lg">
              SBGR / GRU STATION
            </span>
          </Tooltip>
        </Marker>

        {/* Live Aircraft Target Markers */}
        {aircraft.map((ac) => {
          if (!ac.position?.latitude || !ac.position?.longitude) return null;

          const isSelected = selectedIcao === ac.icao24;
          const icon = createAircraftIcon(ac.heading ?? 0, ac.on_ground, isSelected);
          const pos: [number, number] = [ac.position.latitude, ac.position.longitude];

          return (
            <Marker
              key={ac.icao24}
              position={pos}
              icon={icon}
              eventHandlers={{
                click: () => {
                  selectAircraft(ac.icao24);
                  if (onSelectAircraft) onSelectAircraft(ac.icao24);
                },
              }}
            >
              {/* Tooltip on hover */}
              <Tooltip direction="top" offset={[0, -12]} opacity={0.95}>
                <div className="font-mono text-xs space-y-0.5">
                  <div className="font-bold text-white flex items-center justify-between gap-3">
                    <span>{ac.callsign || ac.icao24.toUpperCase()}</span>
                    <span className={ac.on_ground ? 'text-[#FFC857]' : 'text-[#47F3A0]'}>
                      {ac.on_ground ? 'GND' : 'AIRBORNE'}
                    </span>
                  </div>
                  <div className="text-[10px] text-[#B0BAC8]">
                    ALT: <strong className="text-white">{ac.altitude?.value ? `${Math.round(ac.altitude.value)}m` : 'GND'}</strong> · SPD: <strong className="text-white">{ac.velocity?.value ? `${Math.round(ac.velocity.value * 3.6)}km/h` : '0'}</strong>
                  </div>
                </div>
              </Tooltip>

              {/* Popup on click */}
              <Popup>
                <div className="p-1 space-y-1 font-mono text-xs">
                  <div className="font-bold text-sm text-[#47F3A0] border-b border-[#242C3A] pb-1 flex justify-between items-center">
                    <span>{ac.callsign || ac.icao24.toUpperCase()}</span>
                    <span className="text-[10px] text-[#B0BAC8]">{ac.icao24.toUpperCase()}</span>
                  </div>
                  <div>ALTITUDE: <strong className="text-white">{ac.altitude?.value ? `${Math.round(ac.altitude.value)}m` : '0m (GND)'}</strong></div>
                  <div>SPEED: <strong className="text-white">{ac.velocity?.value ? `${Math.round(ac.velocity.value * 3.6)} km/h` : '0 km/h'}</strong></div>
                  <div>HEADING: <strong className="text-white">{ac.heading !== null ? `${Math.round(ac.heading)}°` : 'N/A'}</strong></div>
                  <div>COUNTRY: <strong className="text-[#33A8FF]">{ac.origin_country || 'Unknown'}</strong></div>
                  <div>SQUAWK: <strong className="text-[#FFC857]">{ac.squawk || '7000'}</strong></div>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
};

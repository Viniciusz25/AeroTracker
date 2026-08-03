import { FC, useState } from 'react';
import { Save, MapPin } from 'lucide-react';
import { useSettingsStore } from '../store/settings.store';
import { Button } from '../components/atoms/Button';

export const SettingsPage: FC = () => {
  const { locationName, latitude, longitude, radiusKm, updateLocation, setRadiusKm } =
    useSettingsStore();

  const [name, setName] = useState(locationName);
  const [lat, setLat] = useState(latitude.toString());
  const [lon, setLon] = useState(longitude.toString());
  const [radius, setRadius] = useState(radiusKm.toString());
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    updateLocation(name, parseFloat(lat), parseFloat(lon));
    setRadiusKm(parseFloat(radius));
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="p-6 space-y-6 max-w-[1000px] mx-auto">
      <h2 className="font-['Outfit'] font-bold text-xl text-white">System & Station Settings</h2>

      <form onSubmit={handleSave} className="bg-[#131720] border border-[#1A1F2B] rounded-2xl p-6 space-y-6">
        {/* Station Location Section */}
        <div className="space-y-4">
          <h3 className="font-['Outfit'] font-bold text-base text-[#47F3A0] flex items-center gap-2">
            <MapPin size={18} /> Station Geographical Position
          </h3>

          <div className="space-y-3 font-mono text-xs">
            <div>
              <label className="block text-[#5A6475] mb-1">STATION DISPLAY NAME</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full bg-[#0C0E12] border border-[#242C3A] rounded-lg px-3 py-2 text-white focus:border-[#47F3A0] focus:outline-none"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-[#5A6475] mb-1">LATITUDE (°)</label>
                <input
                  type="number"
                  step="0.0001"
                  value={lat}
                  onChange={(e) => setLat(e.target.value)}
                  className="w-full bg-[#0C0E12] border border-[#242C3A] rounded-lg px-3 py-2 text-white focus:border-[#47F3A0] focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-[#5A6475] mb-1">LONGITUDE (°)</label>
                <input
                  type="number"
                  step="0.0001"
                  value={lon}
                  onChange={(e) => setLon(e.target.value)}
                  className="w-full bg-[#0C0E12] border border-[#242C3A] rounded-lg px-3 py-2 text-white focus:border-[#47F3A0] focus:outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block text-[#5A6475] mb-1">RADAR SEARCH RADIUS (KM)</label>
              <input
                type="number"
                value={radius}
                onChange={(e) => setRadius(e.target.value)}
                className="w-full bg-[#0C0E12] border border-[#242C3A] rounded-lg px-3 py-2 text-white focus:border-[#47F3A0] focus:outline-none"
              />
            </div>
          </div>
        </div>

        {/* Save Bar */}
        <div className="pt-4 border-t border-[#1A1F2B] flex items-center justify-between">
          {saved ? (
            <span className="text-xs font-mono text-[#47F3A0]">✓ STATION CONFIGURATION SAVED</span>
          ) : (
            <span />
          )}
          <Button type="submit" variant="primary" icon={<Save size={16} />}>
            Save Configuration
          </Button>
        </div>
      </form>
    </div>
  );
};

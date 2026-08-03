import type { FC } from 'react';

export const SettingsPage: FC = () => {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white font-['Outfit']">System Settings</h1>
      <p className="text-sm text-[#B0BAC8]">Configure station location, search radius, API credentials and refresh rates</p>
    </div>
  );
};

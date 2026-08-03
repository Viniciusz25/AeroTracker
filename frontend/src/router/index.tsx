import { createBrowserRouter } from 'react-router-dom';
import { AppLayout } from '../layouts/AppLayout';
import { DashboardPage } from '../pages/Dashboard';
import { RadarPage } from '../pages/Radar';
import { FlightsPage } from '../pages/Flights';
import { WeatherPage } from '../pages/Weather';
import { ClockPage } from '../pages/Clock';
import { ISSPage } from '../pages/ISS';
import { MoonPage } from '../pages/Moon';
import { SolarSystemPage } from '../pages/SolarSystem';
import { SatellitesPage } from '../pages/Satellites';
import { LaunchesPage } from '../pages/Launches';
import { SettingsPage } from '../pages/Settings';
import { DiagnosticsPage } from '../pages/Diagnostics';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: 'radar', element: <RadarPage /> },
      { path: 'flights', element: <FlightsPage /> },
      { path: 'weather', element: <WeatherPage /> },
      { path: 'clock', element: <ClockPage /> },
      { path: 'iss', element: <ISSPage /> },
      { path: 'moon', element: <MoonPage /> },
      { path: 'solar-system', element: <SolarSystemPage /> },
      { path: 'satellites', element: <SatellitesPage /> },
      { path: 'launches', element: <LaunchesPage /> },
      { path: 'settings', element: <SettingsPage /> },
      { path: 'diagnostics', element: <DiagnosticsPage /> },
    ],
  },
]);

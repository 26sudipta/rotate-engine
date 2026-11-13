import { useEffect, useRef, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, ZoomControl, useMap } from "react-leaflet";
import L from "leaflet";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
import { Search, MapPin } from "lucide-react";
import { locations } from "../data/mockLocations.js";

// Leaflet's default marker icons reference bundler-relative image paths that
// break under Vite; rebuild the default icon from CDN assets instead.
const defaultIcon = new L.Icon({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

const selectedIcon = new L.Icon({
  iconUrl: markerIcon2x,
  shadowUrl: markerShadow,
  iconSize: [30, 49],
  iconAnchor: [15, 49],
  popupAnchor: [1, -40],
  className: "hue-rotate-[110deg]",
});

function FlyToLocation({ location }) {
  const map = useMap();
  useEffect(() => {
    if (location) {
      map.flyTo([location.lat, location.lng], location.zoom, { duration: 1.1 });
    }
  }, [location, map]);
  return null;
}

export default function MapPanel({ selectedLocationId, onSelectLocation }) {
  const [query, setQuery] = useState("");
  const [flyTarget, setFlyTarget] = useState(null);
  const containerRef = useRef(null);

  const suggestions = query
    ? locations.filter((l) => l.name.toLowerCase().includes(query.toLowerCase()))
    : [];

  const handlePick = (location) => {
    onSelectLocation(location.id);
    setFlyTarget(location);
    setQuery("");
  };

  return (
    <div className="relative h-full w-full overflow-hidden rounded-[24px] border border-border">
      <div className="absolute left-3 right-3 top-3 z-[1000]">
        <div className="relative">
          <Search size={15} className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-ink-soft" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search location..."
            className="w-full rounded-full border border-border bg-surface/95 py-3 pl-10 pr-3 text-[13px] text-ink shadow-sm backdrop-blur placeholder:text-ink-soft focus:outline-none focus:ring-2 focus:ring-paddy/30"
          />
          {suggestions.length > 0 && (
            <ul className="absolute mt-1.5 w-full overflow-hidden rounded-lg border border-border bg-surface shadow-lg">
              {suggestions.map((s) => (
                <li key={s.id}>
                  <button
                    type="button"
                    onClick={() => handlePick(s)}
                    className="flex w-full items-center gap-2 px-3 py-2 text-left text-[13px] text-ink hover:bg-canvas"
                  >
                    <MapPin size={13} className="text-paddy" />
                    {s.name}
                    <span className="ml-auto text-[11px] text-ink-soft">{s.region}</span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <MapContainer
        ref={containerRef}
        center={[23.6, 90.4]}
        zoom={7}
        scrollWheelZoom
        className="h-full w-full"
        zoomControl={false}
      >
        <ZoomControl position="bottomright" />
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <FlyToLocation location={flyTarget} />
        {locations.map((loc) => (
          <Marker
            key={loc.id}
            position={[loc.lat, loc.lng]}
            icon={loc.id === selectedLocationId ? selectedIcon : defaultIcon}
            eventHandlers={{ click: () => handlePick(loc) }}
          >
            <Popup>
              <div className="text-[13px]">
                <p className="font-semibold">{loc.farmName}</p>
                <p className="text-ink-soft">{loc.name}, Bangladesh</p>
                <p className="text-ink-soft">{loc.soilType}</p>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}

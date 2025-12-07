// application/static/js/map.js

document.addEventListener("DOMContentLoaded", async () => {
  const mapContainer = document.getElementById("map");
  if (!mapContainer) return; // not on this page

  const map = L.map("map", {
    zoomControl: true,
  }).setView([1.3521, 103.8198], 11);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);

  const townLayer = L.layerGroup().addTo(map);

  function colourForPrice(price) {
    if (price < 350000) return "#38bdf8"; // blue-ish
    if (price < 550000) return "#fb923c"; // orange
    return "#ef4444"; // red
  }

  try {
    const res = await fetch("/api/map-data");
    if (!res.ok) throw new Error("Failed to load map data");
    const data = await res.json();

    const towns = data.towns || [];
    let latest = data.latest || null;

    if (towns.length === 0) {
      // Nothing predicted yet – short message overlay
      const emptyNotice = L.control({ position: "topright" });
      emptyNotice.onAdd = () => {
        const div = L.DomUtil.create("div", "leaflet-control");
        div.style.background = "rgba(15,23,42,0.9)";
        div.style.color = "white";
        div.style.padding = "6px 10px";
        div.style.borderRadius = "999px";
        div.style.fontSize = "11px";
        div.textContent =
          "Make a few predictions to see your price patterns by town.";
        return div;
      };
      emptyNotice.addTo(map);
      return;
    }

    const latLngs = [];

    towns.forEach((t) => {
      const lat = t.lat;
      const lng = t.lng;
      const count = t.count;
      const avg = t.avg_price;

      const radius = 10 + Math.min(count, 12); // scale by count

      const marker = L.circleMarker([lat, lng], {
        radius,
        color: colourForPrice(avg),
        fillColor: colourForPrice(avg),
        fillOpacity: 0.75,
        weight: 1,
      });

      marker.bindPopup(
        `<b>${t.town}</b><br>` +
          `${count} scenario${count > 1 ? "s" : ""}<br>` +
          `Avg predicted price: <b>$${Math.round(avg).toLocaleString()}</b>`
      );

      marker.addTo(townLayer);
      latLngs.push([lat, lng]);
    });

    if (latLngs.length) {
      map.fitBounds(latLngs, { padding: [20, 20] });
    }

    // Highlight latest prediction if available
    if (latest && latest.lat && latest.lng) {
      const latestMarker = L.circleMarker([latest.lat, latest.lng], {
        radius: 8,
        color: "#22c55e",
        fillColor: "#22c55e",
        fillOpacity: 0.9,
        weight: 2,
      }).addTo(map);

      latestMarker.bindPopup(
        `<b>Latest prediction</b><br>` +
          `${latest.town} · ${latest.flat_type}<br>` +
          `${latest.year} · <b>$${Math.round(
            latest.price
          ).toLocaleString()}</b>`
      );
    }
  } catch (err) {
    console.error(err);
  }
});
